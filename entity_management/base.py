'''
Base simulation entities

.. inheritance-diagram:: entity_management.base
   :parts: 2
'''
from __future__ import print_function
import logging
import operator
import typing
from datetime import datetime
from collections import Iterable, Mapping
from pprint import pformat
from dateutil.parser import parse

import six
import attr
from rdflib.graph import Graph, BNode

from entity_management import nexus
from entity_management.settings import (BASE_RESOURCES, JSLD_DEPRECATED, JSLD_ID, JSLD_REV,
                                        JSLD_TYPE, JSLD_CTX, ORG, PROJ, RDF, NXV, NSG, DASH)
from entity_management.util import (AttrOf, NotInstantiated, _attrs_clone, _clean_up_dict,
                                    _get_list_params, _merge, quote)


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

    def wrap(cls):
        '''wraps'''
        these = _merge(
            _attrs_clone(cls, check_default=operator.eq),
            {k: v() for k, v in attr_dict.items() if v.is_positional},
            {k: v() for k, v in attr_dict.items() if not v.is_positional},
            _attrs_clone(cls, check_default=operator.ne))

        return attr.attrs(cls, these=these, repr=repr)

    return wrap


@attr.s
class _NexusListIterator(six.Iterator):
    '''Nexus paginated list iterator.'''
    cls = attr.ib()
    total_items = attr.ib(type=int, default=None)
    page_from = attr.ib(type=int, default=0)
    page_size = attr.ib(type=int, default=50)
    deprecated = attr.ib(type=bool, default=False)
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
                self.cls._base_url,
                stream=True,
                params={
                    'from': self.page_from,
                    'size': self.page_size,
                    'deprecated': self.deprecated})
            graph = Graph().parse(data=data, format='json-ld')
            self.total_items = [o for s, o in graph.subject_objects(NXV.total)
                                if isinstance(s, BNode)][0].value
            self._page = [str(subj) for subj in graph.subjects(RDF.type, self.cls._nsg_type)]

        if self._item_index >= self.total_items:
            raise StopIteration()

        self._item_index += 1

        id_url = self._page[self._item_index - 1 - self.page_from]
        return self.cls._lazy_init(id_url)


@attr.s(frozen=True)
class Frozen(object):
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

        meta = changes.pop('meta', None)
        obj = attr.evolve(self, **changes)
        if hasattr(obj, 'meta'):
            obj._force_attr('meta', meta or self.meta)  # pylint: disable=no-member
        return obj


class BlankNode(Frozen):
    '''Blank node.'''
    _type = None


@attr.s
class Metadata(object):
    '''A class storing all metadata attributes'''
    token = attr.ib(default=None)
    rev = attr.ib(default=None)
    deprecated = attr.ib(default=False)
    types = attr.ib(default=None)

    @classmethod
    def from_json(cls, json, token):
        '''Build a Metadata from a json payload'''
        return Metadata(rev=json[JSLD_REV], deprecated=json[JSLD_DEPRECATED],
                        types=json[JSLD_TYPE], token=token)


# def from_url(url, use_auth=None):
#     '''
#     Load entity from URL.
#
#     Args:
#         url (str): URL of the entity to load.
#         use_auth (str): OAuth token in case access is restricted.
#             Token should be in the format for the authorization header: Bearer VALUE.
#     '''
#     cls = nexus.get_type(url)
#     if cls is None:
#         raise Exception('Cannot find python class of object at url: {}'.format(url))
#     js = nexus.load_by_url(url, token=use_auth)
#
#     # prepare all entity init args
#     init_args = {}
#     for field in attr.fields(cls):  # pylint: disable=not-an-iterable
#         raw = js.get(field.name)
#         if field.init and raw is not None:
#             type_ = field.type
#             init_args[field.name] = _deserialize_json_to_datatype(type_, raw, use_auth)
#
#     return cls(id=js[JSLD_ID], **init_args).evolve(meta=Metadata.from_json(js, token=use_auth))


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
                                         for kk, vv in six.iteritems(attr_value))
                else:
                    rv[attr_name] = _serialize_obj(attr_value)
        return rv

    return value


def _deserialize_list(data_type, data_raw, token):
    '''Deserialize list of json elements'''
    result_list = []
    is_explicit_list = False
    # find the type of collection element
    if (hasattr(data_type, '__origin__') and issubclass(data_type.__origin__, typing.List)):
        # the collection was explicitly specified in attr.ib
        # like typing.List[Distribution]
        is_explicit_list = True
        list_element_type = _get_list_params(data_type)[0]
    else:
        # nexus returns a collection of one element
        # element type is the type specified in attr.ib
        list_element_type = data_type
    for data_element in data_raw:
        data = _deserialize_json_to_datatype(list_element_type, data_element, token)
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


def _deserialize_json_to_datatype(data_type, data_raw, token=None):
    '''Deserialize raw data json to data_type'''
    # pylint: disable=too-many-return-statements,too-many-branches
    if data_raw is None:
        return None

    try:
        if (not isinstance(data_raw, dict)
                and not isinstance(data_raw, six.string_types)
                and isinstance(data_raw, Iterable)):
            return _deserialize_list(data_type, data_raw, token)

        if (  # in case we have bunch of the Identifiable types as a Union
                (type(data_type) is type(typing.Union)  # noqa
                    and all(issubclass(cls, Identifiable) for cls in _get_list_params(data_type)))
                # or we have just Identifiable
                or issubclass(data_type, Identifiable)):
            resource_id = data_raw[JSLD_ID]
            type_ = data_raw[JSLD_TYPE]
            # root type was used or union of types, try to recover it from resource_id
            if data_type is Identifiable or type(data_type) is type(typing.Union):  # noqa
                data_type = nexus.get_type_from_id(resource_id)
            return data_type._lazy_init(resource_id, type_)

        if issubclass(data_type, OntologyTerm):
            return data_type(url=data_raw[JSLD_ID], label=data_raw['label'])

        if data_type == datetime:
            return parse(data_raw)

        if issubclass(data_type, Frozen):
            # nested obj literals should be deserialized before passed to composite obj constructor
            data = data_type(
                **{k: _deserialize_json_to_datatype(attr.fields_dict(data_type)[k].type, v, token)
                   for k, v in six.iteritems(data_raw)
                   if k in attr.fields_dict(data_type)})
            if issubclass(data_type, BlankNode):
                data._force_attr('_type', data_raw[JSLD_TYPE])
            return data

        if isinstance(data_raw, Mapping):  # we have dict although in class it is specified as List
            if (hasattr(data_type, '__origin__') and issubclass(data_type.__origin__, typing.List)):
                return _deserialize_list(data_type, [data_raw], token)
            else:
                return data_type(**_clean_up_dict(data_raw))

        return data_type(data_raw)

    except Exception:
        L.error('Error deserializing type: %s for raw data:\n%s', data_type, pformat(data_raw))
        raise


def _deserialize_resource(json_ld, cls, use_auth=None):
    '''Build class instance from json.'''
    if cls == Unconstrained:
        instance = Unconstrained(json=json_ld)
    else:
        # prepare all entity init args
        init_args = dict()
        for field in attr.fields(cls):
            raw = json_ld.get(field.name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[field.name] = _deserialize_json_to_datatype(type_, raw, use_auth)
        instance = cls(**init_args)

    # augment instance with extra params present in the response
    instance._force_attr('_id', json_ld.get(JSLD_ID))
    instance._force_attr('_type', json_ld.get(JSLD_TYPE))
    instance._force_attr('_context', json_ld.get(JSLD_CTX))
    for key, value in six.iteritems(json_ld):
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
    '''Initialize class variable _base_url.'''

    def __init__(cls, name, bases, attrs):
        # tag = getattr(cls, '_url_tag', DEFAULT_TAG)
        org = getattr(cls, '_url_org', ORG)
        proj = getattr(cls, '_url_proj', PROJ)

        # Always register constrained type hint, so we can recover in a unique way class from
        # _constrainedBy
        constrained_by = str(DASH[name.lower()])
        nexus.register_type(constrained_by, cls)
        # by default entities are unconstrained unless _is_constrained is provided
        if not getattr(cls, '_is_constrained', False):
            constrained_by = '_'
            nexus.register_type(name, cls)

        cls._base_url = '%s/%s/%s/%s' % (BASE_RESOURCES, org, proj, quote(constrained_by))
        cls._nsg_type = NSG[name]
        cls.__getattribute__ = custom_getattr

        super(_IdentifiableMeta, cls).__init__(name, bases, attrs)


@six.add_metaclass(_IdentifiableMeta)
@attr.s
class Identifiable(Frozen):
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
    def _lazy_init(cls, resource_id, type_=NotInstantiated):
        '''Instantiate an object and put all its attributes to NotInstantiated.'''
        # Running the validator has the side effect of instantiating
        # the object, which we do not want
        attr.set_run_validators(False)
        obj = cls(**{arg.name: NotInstantiated for arg in attr.fields(cls)})
        obj._force_attr('_id', resource_id)
        obj._force_attr('_type', type_)
        attr.set_run_validators(True)
        return obj

    @classmethod
    def from_id(cls, resource_id, on_no_result=None, use_auth=None):
        '''
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. Usually it is
                a lambda calling publish with resource_id.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        id_ = '{}/{}'.format(cls._base_url, quote(resource_id))
        json_ld = nexus.load_by_url(id_, token=use_auth)
        if json_ld is not None:
            return _deserialize_resource(json_ld, cls, use_auth)
        elif on_no_result is not None:
            return on_no_result(use_auth=use_auth)
        else:
            return None

    @classmethod
    def list(cls):
        '''List all instances belonging to the schema this type defines.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''
        return _NexusListIterator(cls)

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
                                              for kk, vv in six.iteritems(attr_value))
                else:
                    json_ld[attr_name] = _serialize_obj(attr_value)
        if hasattr(self, '_context') and self._context is not NotInstantiated:
            json_ld[JSLD_CTX] = self._context
        else:
            json_ld[JSLD_CTX] = ['https://bbp.neuroshapes.org']

        # obj was already deserialized from nexus => we have type
        # or we explicitly set the _type in the class
        if self._type is not NotInstantiated:
            json_ld[JSLD_TYPE] = self._type  # pylint: disable=no-member
        else:  # by default use class name
            json_ld[JSLD_TYPE] = type(self).__name__
        return json_ld

    def publish(self, resource_id=None, use_auth=None):
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
            json_ld = nexus.create(self._base_url,  # pylint: disable=no-member
                                   self.as_json_ld(),
                                   resource_id,
                                   token=use_auth)

        for sys_attr in SYS_ATTRS:
            if sys_attr in json_ld:
                self._force_attr(sys_attr, json_ld[sys_attr])
        self._force_attr('_id', json_ld.get(JSLD_ID))
        self._force_attr('_type', json_ld.get(JSLD_TYPE))
        self._force_attr('_context', json_ld.get(JSLD_CTX))
        return self

    def _instantiate(self, use_auth=None):
        '''Fetch nexus object with id=self._id if it was not initialized before.'''
        fetched_instance = type(self).from_id(self._id, use_auth)
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


# @six.add_metaclass(_IdentifiableMeta)
# @attr.s
# class Identifiable(Frozen):
#     '''Represents collapsed/lazy loaded entity having type and id.
#     Access to any attributes will load the actual entity from nexus and forward property
#     requests to that entity.
#     '''
#     # entity namespace which should be used for json-ld @type attribute
#     _type_namespace = 'nsg'  # Entity classes from specific domains can override this
#     _type_name = ''  # Entity classes from specific domains will override this
#     id = attr.ib(type=str, default=None)
#     meta = attr.ib(type=Metadata, factory=Metadata, init=False)
#
#     def _instantiate(self):
#         '''Fetch nexus object with id=self.id and copy its attribute into current object'''
#         fetched_instance = type(self).from_url(self.id, self.meta.token)
#         for attribute in fields(type(self)):
#             self._force_attr(attribute.name, getattr(fetched_instance, attribute.name))
#
#     @classmethod
#     def _lazy_init(cls, id, types=None, token=None):  # pylint: disable=redefined-builtin
#         '''Instantiate an object and put all its attributes to NotInstantiated
#         except "id"'''
#         # Running the validator has the side effect of instantiating
#         # the object, which we do not want
#         set_run_validators(False)
#         obj = cls(id=id,
#                   **{arg.name: NotInstantiated for arg in attr.fields(cls)
#                      if arg.name not in attr.fields_dict(Identifiable)})
#         obj.meta.token = token
#         obj.meta.types = types
#         set_run_validators(True)
#         return obj
#
#     @classmethod
#     def get_type(cls):
#         '''Get class type. Can be overriden by class varable _type_name.'''
#         return '%s:%s' % (cls._type_namespace, cls._type_name or cls.__name__)
#
#     @property
#     def id_rev(self):
#         '''Id with revision'''
#         return '{}?rev={}'.format(self.id, self.meta.rev)
#
#     @property
#     def types(self):
#         '''Get json-ld types'''
#         # in case object has identity(persisted) types might not have been yet retrieved
#         if self.meta.types is None and self.id:
#             self._instantiate()
#         return self.meta.types
#
#     @property
#     def incoming(self):
#         '''Get an iterator on incoming nodes'''
#         return NexusResultsIterator(self.id + '/incoming', self.meta.token)
#
#     @property
#     def outcoming(self):
#         '''Get an iterator on outcoming nodes'''
#         return NexusResultsIterator(self.id + '/outcoming', self.meta.token)
#
#     @classmethod
#     def from_url(cls, url, use_auth=None):
#         '''
#         Load entity from URL.
#
#         Args:
#             url (str): URL of the entity to load.
#             use_auth (str): OAuth token in case access is restricted.
#                 Token should be in the format for the authorization header: Bearer VALUE.
#         '''
#         return from_url(url, use_auth=use_auth)
#
#     @classmethod
#     def from_uuid(cls, uuid, use_auth=None):
#         '''
#         Load entity from UUID.
#
#         Args:
#             uuid (str): UUID of the entity to load.
#             use_auth (str): OAuth token in case access is restricted.
#                 Token should be in the format for the authorization header: Bearer VALUE.
#         '''
#         return cls.from_url('{}/{}'.format(cls.base_url, uuid), use_auth=use_auth)
#
#     @classmethod
#     def find_unique(cls, throw=False, on_no_result=None, poll_until_exists=False, **kwargs):
#         '''Wrapper around find_by that will:
#         - return the result if there is only one result
#         - throw if there are more than one results
#
#         Args:
#             throw (bool): Whether to throw when no result found
#             on_no_result (Callable): A function to be called when no result found and throw==False
#             poll_until_exists (bool): flag to enable polling after the execution of on_no_result()
#                                      until find_unique returns something. The polling frequency is
#                                      2 seconds and the timeout is 1 minute.
#             kwargs: Arguments to be passed to the underlying cls.find_by
#         '''
#
#         iterator = cls.find_by(**kwargs)
#         try:
#             result = next(iterator)
#         except StopIteration:
#             if throw:
#                 raise Exception('{}.find_unique({}) did not return anything'
#                                 .format(cls, str(kwargs)))
#
#             if on_no_result:
#                 result = on_no_result()
#                 if poll_until_exists:
#                     for i in range(30):
#                         L.debug('Poll #%s for %s.find_unique(%s)', i, cls, str(kwargs))
#                         if cls.find_unique(**kwargs):
#                             return result
#                         sleep(2)
#                     raise Exception('Timeout reached while polling for {}.find_unique({})'
#                                     .format(cls, str(kwargs)))
#                 return result
#             else:
#                 return None
#
#         second = next(iterator, None)
#         if second:
#             raise Exception('ERROR: {}.find_unique({}) found more than one result.'
#                             '\nFirst 2 results are:\n- {}\n- {}'.format(
#                                 cls, str(kwargs), result.id, second.id))
#         return result
#
#     @classmethod
#     def find_by(cls, all_versions=False, all_domains=False, all_organizations=False,
#                 query=None, use_auth=None, **properties):  # TODO improve query params passing
#         '''Load entity from properties.
#
#         Args:
#             collection_address (str): Selected collection to list, filter or search;
#                 for example: ``/myorg/mydomain``, ``/myorg/mydomain/myschema/v1.0.0``
#             query (dict): Provide explicit nexus query.
#             use_auth (str): OAuth token in case access is restricted.
#                 Token should be in the format for the authorization header: Bearer VALUE.
#             **properties: Keyword args. If ``key`` has words separated by double underscore they
#                 will be replaced with ``/`` forming deep path for the query. Single underscores
#                 will be replaced with ``:`` explicitly specifying namespaces(otherwise default
#                 ``nsg:`` namespace will be used).
#         Returns:
#             Results iterator.
#         '''
#
#         # pylint: disable=too-many-locals
#         # build collection address
#         url_org = getattr(cls, '_url_org', ORG)
#         url_domain = getattr(cls, '_url_domain', 'simulation')
#         url_name = getattr(cls, '_url_name', cls.__name__.lower())
#         url_version = getattr(cls, '_url_version', VERSION)
#         if all_versions:
#             collection_address = '/%s/%s/%s' % (url_org, url_domain, url_name)
#         elif all_domains:
#             collection_address = '/%s' % url_org
#         elif all_organizations:
#             collection_address = None
#         else:
#             collection_address = '/%s/%s/%s/%s' % (url_org, url_domain, url_name, url_version)
#
#         if query is None:
#             # prepare properties
#             props = []
#             for key, value in six.iteritems(properties):
#                 path = resolve_path(key)
#
#                 if isinstance(value, OntologyTerm):
#                     props.append(
#                         {'op': 'eq', 'path': path, 'value': value.url})
#                 elif isinstance(value, tuple):
#                     props.append(
#                         {'op': value[0], 'path': path, 'value': value[1]})
#                 elif isinstance(value, Identifiable):
#                     props.append({'op': 'eq', 'path': path, 'value': value.id})
#                 else:
#                     props.append({'op': 'eq', 'path': path, 'value': value})
#
#             props.append({'op': 'in', 'path': 'rdf:type',
#                           'value': cls.get_type()})
#
#             query = {'op': 'and', 'value': props}
#
#         location = nexus.find_by(collection_address, query, token=use_auth)
#         if location is not None:
#             return NexusResultsIterator(location, use_auth)
#         return None
#
#     def as_json_ld(self):
#         '''Get json-ld representation of the Entity
#         Return json with added json-ld properties such as @context and @type
#         '''
#         rv = {}
#         fix_types = 'nsg:Entity' in self.types if self.types else False
#         for attribute in attr.fields(type(self)):
#             if attribute.name in attr.fields_dict(Identifiable):
#                 continue  # skip Identifiable attributes
#             attr_value = getattr(self, attribute.name)
#             if attr_value is not None:  # ignore empty values
#                 attr_name = attribute.name
#                 if isinstance(attr_value, (tuple, list, set)):
#                     rv[attr_name] = [_serialize_obj(i, fix_types) for i in attr_value]
#                 elif isinstance(attr_value, dict):
#                     rv[attr_name] = dict((kk, _serialize_obj(vv))
#                                          for kk, vv in six.iteritems(attr_value))
#                 else:
#                     rv[attr_name] = _serialize_obj(attr_value, fix_types)
#         rv[JSLD_TYPE] = self.types
#         return rv
#
#     def publish(self, use_auth=None):
#         '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
#         entity attributes.
#
#         Args:
#             use_auth (str): OAuth token in case access is restricted.
#                 Token should be in the format for the authorization header: Bearer VALUE.
#         Returns:
#             New instance of the same class with revision updated.
#         '''
#         if self.id:
#             js = nexus.update(self.id, self.meta.rev, self.as_json_ld(), token=use_auth)
#         else:
#             self.meta.types = ['prov:Entity', self.get_type()]
#             js = nexus.create(self.base_url, self.as_json_ld(), token=use_auth)  # noqa pylint: disable=no-member
#
#         self.meta.rev = js[JSLD_REV]
#         return self.evolve(id=js[JSLD_ID])
#
#     def deprecate(self, use_auth=None):
#         '''Mark entity as deprecated.
#         Deprecated entities are not possible to retrieve by name.
#
#         Args:
#             use_auth (str): OAuth token in case access is restricted.
#                 Token should be in the format for the authorization header: Bearer VALUE.
#         '''
#         self._instantiate()
#         js = nexus.deprecate(self.id, self.meta.rev, token=use_auth)
#         self.meta.rev = js[JSLD_REV]
#         self.meta.deprecated = True
#         return self


# @attributes({
#     'downloadURL': AttrOf(str, default=None),
#     'accessURL': AttrOf(str, default=None),
#     'contentSize': AttrOf(dict, default=None),
#     'digest': AttrOf(dict, default=None),
#     'mediaType': AttrOf(str, default=None),
#     'originalFileName': AttrOf(str, default=None),
#     'storageType': AttrOf(str, default=None),
# })
# class Distribution(Frozen):
#     '''External resource representations,
#     this can be a file or a folder on gpfs
#
#     Args:
#         downloadURL (str): For directly accessible resources for example files.
#         accessURL (str): For container locations for example folders.
#         contentSize (int): If known in advance size of the resource.
#         digest (int): Hash/Checksum of the resource.
#         mediaType (str): Type of the resource accessible by the downloadURL.
#         originalFileName (str): File name which was submitted as an attachment.
#         storageType (str): storage type, will contain `gpfs` for gpfs links.
#
#     either `downloadURL` for files or `accessURL` for folders must be provided'''
#
#     def __attrs_post_init__(self):
#         if not self.downloadURL and not self.accessURL:  # pylint: disable=no-member
#             raise ValueError('downloadURL or accessURL must be provided')


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
    '''Brain location'''


class File(Identifiable):
    '''Blank node.'''
    _url_base = 'files'
    _type = None

    def upload(self, resource_id=None, use_auth=None):
        '''.'''
        pass

    # def download(self, path, use_auth=None):
    #     '''Download attachment of the entity and save it on the path with the originalFileName.
    #
    #     Args:
    #         path(str): Absolute filename or path where to save the file.
    #                    If path is an existing folder, file name will be taken from
    #                    distribution originalFileName.
    #         use_auth(str): Optional OAuth token.
    #     '''
    #     if os.path.exists(path) and os.path.isdir(path):
    #         filename = dist.originalFileName
    #     else:
    #         filename = os.path.basename(path)
    #         path = os.path.dirname(path)
    #     nexus.download(dist.downloadURL, path, filename, token=use_auth)
    #     return os.path.join(os.path.realpath(path), filename)

    def tag(self, use_auth=None):
        '''.'''
        pass

    def deprecate(self, use_auth=None):
        '''.'''
        pass
