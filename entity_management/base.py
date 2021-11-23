'''
Base simulation entities

.. inheritance-diagram:: entity_management.base
   :parts: 2
'''
from __future__ import print_function
import logging
import typing
from datetime import datetime
from collections.abc import Iterable, Mapping
from pprint import pformat
from dateutil.parser import parse

import attr
from rdflib.graph import Graph, BNode

from entity_management import nexus
from entity_management.state import get_org, get_proj, get_base_resources, get_base_url
from entity_management.settings import JSLD_ID, JSLD_TYPE, JSLD_CTX, RDF, NXV, NSG, DASH
from entity_management.util import (AttrOf, NotInstantiated, _clean_up_dict, _get_list_params,
                                    quote)


L = logging.getLogger(__name__)

SYS_ATTRS = {
    '_id',
    '_type',
    '_context',
    '_constrainedBy',
    '_createdAt',
    '_createdBy',
    '_deprecated',
    '_project',
    '_rev',
    '_self',
    '_updatedAt',
    '_updatedBy'
}


def _copy_sys_meta(src, dest):
    '''Copy system metadata from source to destination entity.'''
    for attribute in SYS_ATTRS:
        if hasattr(src, attribute):
            dest._force_attr(attribute, getattr(src, attribute))


def _type_class(type_):
    '''Get type class. First try if it's `typing` type class then fallback to regular type.'''
    try:
        try:
            return type_.__extra__  # 3.6
        except AttributeError:
            return type_.__origin__  # 3.7
    except AttributeError:
        return type_


def _is_typing_generic(type_):
    '''Check if type is typing.Generic.'''
    return hasattr(type_, '__origin__')


def custom_getattr(obj, name):
    '''Overload of __getattribute__ to trigger instantiation of Nexus object
    if the attribute is NotInstantiated'''
    if name == '__class__' or not isinstance(obj, Identifiable):
        return object.__getattribute__(obj, name)

    value = object.__getattribute__(obj, name)
    if value is NotInstantiated and obj._id is not None:
        obj._instantiate()
        return getattr(obj, name)
    else:
        return value


def attributes(attr_dict=None, repr=True):  # pylint: disable=redefined-builtin
    '''decorator to simplify creation of classes that have args and kwargs'''
    if attr_dict is None:
        attr_dict = {}  # just inherit attributes from parent class

    return lambda cls: attr.attrs(cls, these={k: v() for k, v in attr_dict.items()}, repr=repr)


@attr.s
class _NexusBySchemaIterator():
    '''Nexus paginated list iterator.'''
    cls = attr.ib()
    total_items = attr.ib(type=int, default=None)
    page_from = attr.ib(type=int, default=0)
    page_size = attr.ib(type=int, default=50)
    deprecated = attr.ib(type=bool, default=False)
    base = attr.ib(default=None)
    org = attr.ib(default=None)
    proj = attr.ib(default=None)
    use_auth = attr.ib(default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __iter__(self):
        return self

    def __next__(self):
        '''Return next entity from the paginated result set, fetch next page if required'''
        # fetch next page if needed
        if self.total_items is None or self.page_from + self.page_size == self._item_index:
            self.page_from = self._item_index
            data = nexus.load_by_url(
                self.cls.get_constrained_url(base=self.base, org=self.org, proj=self.proj),
                stream=True,
                params={'from': self.page_from,
                        'size': self.page_size,
                        'deprecated': self.deprecated},
                token=self.use_auth)
            graph = Graph().parse(data=data, format='json-ld')
            self.total_items = [o for s, o in graph.subject_objects(NXV.total)
                                if isinstance(s, BNode)][0].value
            self._page = [str(subj) for subj in graph.subjects(RDF.type, self.cls._nsg_type)]

        if self._item_index >= self.total_items:
            raise StopIteration()

        id_url = self._page[self._item_index - self.page_from]
        self._item_index += 1
        return self.cls._lazy_init(id_url, base=self.base, org=self.org, proj=self.proj)


@attr.s
class _NexusBySparqlIterator():
    '''Nexus paginated list iterator.'''
    cls = attr.ib()
    query = attr.ib(type=str)
    base = attr.ib(type=str, default=None)
    org = attr.ib(type=str, default=None)
    proj = attr.ib(type=str, default=None)
    use_auth = attr.ib(type=str, default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __iter__(self):
        return self

    def __next__(self):
        '''Return next entity from the paginated result set, fetch next page if required'''
        # fetch next page if needed
        if self._page is None:
            json = nexus.sparql_query(self.query,
                                      base=self.base,
                                      org=self.org,
                                      proj=self.proj,
                                      token=self.use_auth)
            self._page = [i['entity']['value'] for i in json['results']['bindings']]

        if self._item_index >= len(self._page):
            raise StopIteration()

        id_url = self._page[self._item_index]
        self._item_index += 1
        return self.cls._lazy_init(id_url, base=self.base, org=self.org, proj=self.proj)


@attr.s(frozen=True)
class Frozen():
    '''Utility class making derived classed immutable. Use `evolve` method to introduce changes.'''

    def _force_attr(self, attribute, value):
        '''Helper method to enforce attribute value on frozen instance'''
        object.__setattr__(self, attribute, value)

    def evolve(self, **changes):
        '''Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''

        obj = attr.evolve(self, **changes)
        return obj


class BlankNode(Frozen):
    '''Blank node.'''

    def __attrs_post_init__(self):
        self._force_attr('_type', type(self).__name__)


def _serialize_obj(value):
    '''Serialize object'''
    if isinstance(value, OntologyTerm):
        return {JSLD_ID: value.url, 'label': value.label}

    if isinstance(value, Identifiable):
        return {JSLD_ID: value._id, JSLD_TYPE: value._type}

    if isinstance(value, datetime):
        return value.isoformat()

    if attr.has(type(value)):
        rv = {}
        for attribute in attr.fields(type(value)):
            attr_name = attribute.name
            attr_value = getattr(value, attr_name)
            if attr_value is not None:  # ignore empty values
                if isinstance(attr_value, (tuple, list, set)):
                    rv[attr_name] = [_serialize_obj(i) for i in attr_value]
                elif isinstance(attr_value, dict):
                    rv[attr_name] = dict((kk, _serialize_obj(vv))
                                         for kk, vv in attr_value.items())
                else:
                    rv[attr_name] = _serialize_obj(attr_value)
        if hasattr(value, '_type'):  # BlankNode have types
            rv[JSLD_TYPE] = value._type
        return rv

    return value


def _deserialize_list(data_type, data_raw, base=None, org=None, proj=None, token=None):
    '''Deserialize list of json elements'''
    result_list = []
    is_explicit_list = False
    # find the type of collection element
    if _is_typing_generic(data_type) and issubclass(_type_class(data_type), list):
        # the collection was explicitly specified in attr.ib
        # like typing.List[Distribution]
        is_explicit_list = True
        list_element_type = _get_list_params(data_type)[0]
    else:
        # nexus returns a collection of one element
        # element type is the type specified in attr.ib
        list_element_type = data_type
    for data_element in data_raw:
        data = _deserialize_json_to_datatype(list_element_type, data_element,
                                             base, org, proj, token)
        if data is not None:
            result_list.append(data)
    # if only one then probably nexus is just responding with the collection for single element
    # TODO check this with nexus it might be a bug on their side
    if not len(result_list):
        return None
    # do not use collection for single elements unless it was explicitly specified as typing.List
    elif not is_explicit_list and len(result_list) == 1:
        return result_list[0]
    else:
        return result_list


def _deserialize_json_to_datatype(data_type, data_raw, base=None, org=None, proj=None, token=None):
    '''Deserialize raw data json to data_type'''
    # pylint: disable=too-many-return-statements,too-many-branches
    if data_raw is None:
        return None

    try:
        if (not isinstance(data_raw, dict)
                and not isinstance(data_raw, str)
                and isinstance(data_raw, Iterable)):
            return _deserialize_list(data_type, data_raw, base, org, proj, token)

        if (  # in case we have bunch of the Identifiable types as a Union
                (_type_class(data_type) is typing.Union  # noqa
                    and all(issubclass(cls, Identifiable) for cls in _get_list_params(data_type)))
                # or we have just Identifiable, make sure it is not typing.Generic
                or (not _is_typing_generic(data_type) and issubclass(data_type, Identifiable))):
            resource_id = data_raw[JSLD_ID]
            type_ = data_raw[JSLD_TYPE]
            # root type was used or union of types, try to recover it from resource_id
            if data_type is Identifiable or _type_class(data_type) is typing.Union:
                data_type = nexus.get_type_from_id(resource_id, base, org, proj, token=token)
            return data_type._lazy_init(resource_id, type_, base, org, proj)

        if not _is_typing_generic(data_type) and issubclass(data_type, OntologyTerm):
            return data_type(url=data_raw[JSLD_ID], label=data_raw['label'])

        if data_type == datetime:
            return parse(data_raw)

        if not _is_typing_generic(data_type) and issubclass(data_type, Frozen):
            # nested obj literals should be deserialized before passed to composite obj constructor
            data = data_type(
                **{k: _deserialize_json_to_datatype(attr.fields_dict(data_type)[k].type, v,
                                                    base, org, proj, token)
                   for k, v in data_raw.items() if k in attr.fields_dict(data_type)})
            if issubclass(data_type, BlankNode):
                data._force_attr('_type', data_raw[JSLD_TYPE])
            return data

        if isinstance(data_raw, Mapping):  # we have dict although in class it is specified as List
            if _is_typing_generic(data_type) and issubclass(_type_class(data_type), typing.List):
                return _deserialize_list(data_type, [data_raw], base, org, proj, token)
            else:
                return data_type(**_clean_up_dict(data_raw))

        return data_type(data_raw)

    except Exception:
        L.error('Error deserializing type: %s for raw data:\n%s', data_type, pformat(data_raw))
        raise


def _deserialize_resource(json_ld, cls, base=None, org=None, proj=None, token=None):
    '''Build class instance from json.'''
    if cls == Unconstrained:
        instance = Unconstrained(json=json_ld)
    else:
        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            raw = json_ld.get(field.name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[field.name] = _deserialize_json_to_datatype(type_, raw,
                                                                      base, org, proj, token)
        instance = cls(**init_args)

    # augment instance with extra params present in the response
    instance._force_attr('_id', json_ld.get(JSLD_ID))
    instance._force_attr('_type', json_ld.get(JSLD_TYPE))
    instance._force_attr('_context', json_ld.get(JSLD_CTX))
    for key, value in json_ld.items():
        if key in SYS_ATTRS:
            instance._force_attr(key, value)

    if cls == Unconstrained:
        for sys_attr in SYS_ATTRS:
            json_ld.pop(sys_attr, None)
        json_ld.pop(JSLD_ID, None)
        json_ld.pop(JSLD_TYPE, None)
        json_ld.pop(JSLD_CTX, None)

    return instance


class _IdentifiableMeta(type):
    '''Initialize class variables.'''

    def __init__(cls, name, bases, attrs):
        # Always register constrained type hint, so we can recover in a unique way class from
        # _constrainedBy
        constrained_by = str(DASH[name.lower()])
        nexus.register_type(constrained_by, cls)
        # also registre by class name so we can recover from @type
        nexus.register_type(name, cls)

        cls._nsg_type = NSG[name]
        cls.__getattribute__ = custom_getattr

        super(_IdentifiableMeta, cls).__init__(name, bases, attrs)


@attr.s
class Identifiable(Frozen, metaclass=_IdentifiableMeta):
    '''Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    requests to that entity.
    '''
    _id = None
    _self = None
    _type = NotInstantiated
    _context = NotInstantiated
    _constrainedBy = NotInstantiated
    _createdAt = NotInstantiated
    _createdBy = NotInstantiated
    _deprecated = NotInstantiated
    _project = NotInstantiated
    _rev = NotInstantiated
    _updatedAt = NotInstantiated
    _updatedBy = NotInstantiated

    @classmethod
    def _lazy_init(cls, resource_id, type_=NotInstantiated, base=None, org=None, proj=None):
        '''Instantiate an object and put all its attributes to NotInstantiated.'''
        # Running the validator has the side effect of instantiating
        # the object, which we do not want
        attr.set_run_validators(False)
        obj = cls(**{arg.name: NotInstantiated for arg in attr.fields(cls)})
        obj._force_attr('_id', resource_id)
        obj._force_attr('_type', type_)
        obj._force_attr('_lazy_meta_', (base, org, proj))
        attr.set_run_validators(True)
        return obj

    @classmethod
    def get_constrained_url(cls, base=None, org=None, proj=None):
        '''Get schema constrained url.'''
        constrained_by = str(DASH[cls.__name__.lower()])
        return f'{get_base_resources(base)}/{get_org(org)}/{get_proj(proj)}/{quote(constrained_by)}'

    @classmethod
    def from_id(cls, resource_id, on_no_result=None, base=None, org=None, proj=None, use_auth=None,
                **kwargs):
        '''
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. It will receive
                `resource_id` as a first argument.
            kwargs: Keyword arguments which will be forwarded to ``on_no_result`` function.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        url = f'{get_base_url(base, org, proj)}/{quote(resource_id)}'
        json_ld = nexus.load_by_url(url, token=use_auth)
        if json_ld is not None:
            return _deserialize_resource(json_ld, cls,
                                         base=base, org=org, proj=proj, token=use_auth)
        elif on_no_result is not None:
            return on_no_result(resource_id,
                                base=base, org=org, proj=proj, use_auth=use_auth, **kwargs)
        else:
            return None

    @classmethod
    def from_url(cls, url, base=None, org=None, proj=None, use_auth=None):
        '''
        Load entity from url.

        Args:
            url (str): Full url to the entity in nexus. ``_self`` content is a valid full URL.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        json_ld = nexus.load_by_url(url, token=use_auth)
        if json_ld is not None:
            return _deserialize_resource(json_ld, cls,
                                         base=base, org=org, proj=proj, token=use_auth)
        else:
            return None

    @classmethod
    def list_by_schema(cls, **kwargs):
        '''List all instances belonging to the schema this type defines.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''
        return _NexusBySchemaIterator(cls, **kwargs)

    def get_id(self):
        '''Retrieve _id property.'''
        return self._id

    def get_url(self):
        '''Retrieve URL of the nexus entity.

        Returns:
            Content of the ``_self`` property.
        '''
        return self._self

    def as_json_ld(self):
        '''Get json-ld representation of the Entity
        Return json with added json-ld properties such as @context and @type
        '''
        if isinstance(self, Unconstrained):
            return self.json  # pylint: disable=no-member

        json_ld = {}
        for attribute in attr.fields(type(self)):
            attr_value = getattr(self, attribute.name)
            if attr_value is not None:  # ignore empty values
                attr_name = attribute.name
                if isinstance(attr_value, (tuple, list, set)):
                    json_ld[attr_name] = [_serialize_obj(i) for i in attr_value]
                elif isinstance(attr_value, dict):
                    json_ld[attr_name] = dict((kk, _serialize_obj(vv))
                                              for kk, vv in attr_value.items())
                else:
                    json_ld[attr_name] = _serialize_obj(attr_value)
        if hasattr(self, '_context') and self._context is not NotInstantiated:
            json_ld[JSLD_CTX] = self._context
        else:
            json_ld[JSLD_CTX] = ['https://bbp.neuroshapes.org']
            # json_ld[JSLD_CTX] = ['https://bluebrainnexus.io/contexts/shacl-20170720.json',
            #                      'https://bluebrainnexus.io/contexts/resource.json',
            #                      'https://incf.github.io/neuroshapes/contexts/data.json']

        # obj was already deserialized from nexus => we have type
        # or we explicitly set the _type in the class
        if self._type is not NotInstantiated:
            json_ld[JSLD_TYPE] = self._type  # pylint: disable=no-member
        else:  # by default use class name
            json_ld[JSLD_TYPE] = type(self).__name__
        return json_ld

    def publish(self, resource_id=None, base=None, org=None, proj=None, use_auth=None):
        '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes.

        Args:
            resource_id (str): Resource identifier. If not provided nexus will generate one.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if self._self:
            json_ld = nexus.update(self._self, self._rev, self.as_json_ld(), token=use_auth)
        else:
            json_ld = nexus.create(get_base_url(base, org, proj),
                                   self.as_json_ld(),
                                   resource_id,
                                   token=use_auth)

        for sys_attr in SYS_ATTRS:
            if sys_attr in json_ld:
                self._force_attr(sys_attr, json_ld[sys_attr])
        self._force_attr('_id', json_ld.get(JSLD_ID))
        self._force_attr('_type', json_ld.get(JSLD_TYPE))
        return self

    def _instantiate(self):
        '''Fetch nexus object with id=self._id if it was not initialized before.'''
        if hasattr(self, '_lazy_meta_'):
            base, org, proj = getattr(self, '_lazy_meta_')
        else:
            base, org, proj = (None, None, None)
        fetched_instance = type(self).from_id(self._id, base=base, org=org, proj=proj)
        for attribute in attr.fields(type(self)):
            self._force_attr(attribute.name, getattr(fetched_instance, attribute.name))
        _copy_sys_meta(fetched_instance, self)

    def deprecate(self, use_auth=None):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.

        Args:
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        nexus.deprecate(self._id, self._rev, token=use_auth)
        return self

    def evolve(self, **changes):
        '''Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''
        obj = attr.evolve(self, **changes)
        _copy_sys_meta(self, obj)
        return obj


@attributes({
    'json': AttrOf(dict),
})
class Unconstrained(Identifiable):
    '''Shapeless data.

    Args:
        json (dict): python dictionary which will be seralized into json.
    '''
    _url_schema = '_'


@attributes({
    'value': AttrOf(str),
    'unitText': AttrOf(str, default=None),
    'unitCode': AttrOf(str, default=None),
})
class QuantitativeValue(Frozen):
    '''External resource representations,
    this can be a file or a folder on gpfs

    Args:
        value (str): Value.
        unitText (str): Unit text.
        unitCode (str): The unit of measurement given using the UN/CEFACT Common Code (3 characters)
            or a URL. Other codes than the UN/CEFACT Common Code may be used with a prefix followed
            by a colon.
    '''


@attributes({
    'url': AttrOf(str),
    'label': AttrOf(str, default=None),
})
class OntologyTerm(Frozen):
    '''Ontology term such as brain region or species

    Args:
        url (str): Ontology term url identifier.
        label (str): Label for the ontology term.
    '''


@attributes({'brainRegion': AttrOf(OntologyTerm)})
class BrainLocation(Frozen):
    '''Brain location.

    Args:
        brainRegion (OntologyTerm): Brain region ontology term.
    '''
