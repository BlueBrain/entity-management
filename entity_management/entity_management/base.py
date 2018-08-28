'''
Base simulation entities

.. inheritance-diagram:: entity_management.base entity_management.simulation.Entity
                         entity_management.core.Entity
   :parts: 2
'''
import typing
import six
from six.moves.urllib.parse import (urlsplit, # pylint: disable=import-error,no-name-in-module
                                    parse_qsl, urlunsplit, urlencode)

from datetime import datetime
from inspect import getmro

import attr
from dateutil.parser import parse

from entity_management import nexus
from entity_management.util import _clean_up_dict
from entity_management.util import attributes, AttrOf, resolve_path
from entity_management.settings import (BASE_DATA, ORG, VERSION, JSLD_ID, JSLD_REV,
                                        JSLD_DEPRECATED, JSLD_CTX, JSLD_TYPE, NSG_CTX)


@attr.s
class NexusResultsIterator(six.Iterator):
    '''Nexus paginated results iterator'''
    cls = attr.ib()
    url = attr.ib()
    token = attr.ib()
    total_items = attr.ib(type=int, default=None)
    page_from = attr.ib(type=int, default=None)
    page_size = attr.ib(type=int, default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __attrs_post_init__(self):
        split_url = urlsplit(self.url)
        query_params = dict(parse_qsl(split_url.query))
        self.page_from = int(query_params['from'])
        self.page_size = int(query_params['size'])

    def __iter__(self):
        return self

    def __next__(self):
        '''Return next entity from the paginated result set, fetch next page if required'''
        # fetch next page if needed
        if self.total_items is None or self.page_from + self.page_size == self._item_index:
            self.page_from = self._item_index
            split_url = urlsplit(self.url)
            self.url = urlunsplit(split_url._replace( # pylint: disable=protected-access
                    query=urlencode({'from': self.page_from, 'size': self.page_size})))
            json_payload = nexus.load_by_url(self.url, token=self.token)
            self._page = [entity['resultId'] for entity in json_payload['results']]
            self.total_items = int(json_payload['total'])

        if self._item_index >= self.total_items:
            raise StopIteration()

        entity_url = self._page[self._item_index - self.page_from]
        obj = Identifiable()
        obj = obj.evolve(_id=entity_url,
                         _proxied_type=self.cls,
                         _proxied_token=self.token)
        self._item_index += 1
        return obj


def _deserialize_list(data_type, data_raw, token):
    '''Deserialize list of json elements'''
    result_list = []
    # find the type of collection element
    if isinstance(data_type, typing.GenericMeta):
        # the collection was explicitly specified in attr.ib
        # like typing.List[Distribution]
        assert data_type.__extra__ == list
        list_element_type = data_type.__args__[0]
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
    elif len(result_list) == 1 and not isinstance(data_type, typing.GenericMeta):
        return result_list[0]
    else:
        return result_list


def _deserialize_json_to_datatype(data_type, data_raw, token=None):
    '''Deserialize raw data json to data_type'''
    if data_raw is None:
        value = None
    elif isinstance(data_raw, list):
        value = _deserialize_list(data_type, data_raw, token)
    elif (# in case we have bunch of the Identifiable types as a Union
            (type(data_type) is type(typing.Union)
                and all(issubclass(cls, Identifiable) for cls in data_type.__args__))
            # or we have just Identifiable
            or issubclass(data_type, Identifiable)):
        # make lazy proxy for identifiable object
        obj = Identifiable()
        url = data_raw[JSLD_ID]
        if data_type is Identifiable: # root type was used, try to recover it from url
            data_type = nexus.get_type(url)
        # pylint: disable=protected-access
        value = obj.evolve(_proxied_type=data_type,
                           _proxied_token=token,
                           _types=data_raw[JSLD_TYPE],
                           _id=url)
    elif issubclass(data_type, OntologyTerm):
        value = data_type(url=data_raw[JSLD_ID], label=data_raw['label'])
    elif data_type == datetime:
        value = parse(data_raw)
    elif issubclass(data_type, Frozen):
        # nested obj literals should be deserialized before passed to composite obj constructor
        value = data_type(
                **{k: _deserialize_json_to_datatype(attr.fields_dict(data_type)[k].type, v, token)
                    for k, v in six.iteritems(data_raw)
                    if k in attr.fields_dict(data_type)})
    elif isinstance(data_raw, dict):
        value = data_type(**_clean_up_dict(data_raw))
    else:
        value = data_type(data_raw)

    return value


def _serialize_obj(value):
    '''Serialize object'''
    if isinstance(value, Identifiable):
        return {JSLD_ID: value.id, JSLD_TYPE: value.types}
    elif isinstance(value, OntologyTerm):
        return {JSLD_ID: value.url, 'label': value.label}
    elif isinstance(value, datetime):
        return value.isoformat()
    elif attr.has(type(value)):
        return attr.asdict(value, recurse=True, filter=lambda _, value: value is not None)
    else:
        return value


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

        return attr.evolve(self, **changes)


class _IdentifiableMeta(type):
    '''Make Identifiable behave as it's _proxied_type, _proxied_type is set by json-ld
    deserialization.
    Initialize class variable _base_url.'''

    def __init__(cls, name, bases, attrs):
        # initialize base_url
        version = getattr(cls, '_url_version', VERSION)
        url_org = getattr(cls, '_url_org', ORG)
        url_domain = getattr(cls, '_url_domain', 'simulation')

        type_id = '%s/%s' % (url_domain, name.lower())
        cls._base_url = '%s/%s/%s/%s' % (BASE_DATA, url_org, type_id, version)
        nexus.register_type(type_id, cls)

        super(_IdentifiableMeta, cls).__init__(name, bases, attrs)

    def __instancecheck__(cls, inst):
        '''If instance has _proxied_type then it is a proxy and instance check should be done
        against proxied type'''
        if '_proxied_type' in dir(inst):
            mro = getmro(inst._proxied_type) # pylint: disable=protected-access
        else:
            mro = getmro(type(inst))
        return any(c == cls for c in mro)


@six.add_metaclass(_IdentifiableMeta)
@attributes()
class Identifiable(Frozen):
    '''Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    requests to that entity.
    '''
    # entity namespace which should be used for json-ld @type attribute
    _type_namespace = '' # Entity classes from specific domains will override this
    _type_name = '' # Entity classes from specific domains will override this

    @classmethod
    def get_type(cls):
        '''Get class type. Can be overriden by class varable _type_name.'''
        if cls._type_name:
            return '%s:%s' % (cls._type_namespace, cls._type_name)
        else:
            return '%s:%s' % (cls._type_namespace, cls.__name__)

    @property
    def base_url(self):
        '''base url'''
        return self._base_url

    @property
    def id(self):
        '''id'''
        return self._id

    @property
    def types(self):
        '''types'''
        return self._types

    def __getattr__(self, name):
        # isinstance is overriden in metaclass which is true for all subclasses of Identifiable
        if (type(self) == Identifiable and '_id' in self.__dict__):
            # Identifiable instances behave like proxies, set it up and then forward attr request
            if '_proxied_object' not in self.__dict__: # can't use hasattr as it will call getattr
                                                       # and that will cause recursion to _getattr_
                self._force_attr('_proxied_object',
                                 self._proxied_type.from_url(self._id, self._proxied_token))
            if self._proxied_object is None:
                raise ValueError('Unable to find proxied entity for %s and %s' %
                                 (self._id, self._proxied_type))
            return getattr(self._proxied_object, name)
        else:
            # subclasses of Identifiable just raise if arrived in __getattr__
            if name == 'id':
                suggestion = '\nSuggestion: did you forget to publish it before using it ?'
            else:
                suggestion = ''
            raise AttributeError("No attribute '%s' in %s%s" % (name, type(self), suggestion))

    def __dir__(self):
        '''If Identifiable is a proxy(has _proxied_type attribute) then collect attributes from
        proxied object'''
        if '_proxied_object' in self.__dict__ and self.name: # get proxied attr to trigger lazy load
            attrs_from_mro = set(attrib for cls in getmro(type(self._proxied_object))
                                        for attrib in dir(cls))
            attrs_from_obj = set(self._proxied_object.__dict__)
        else:
            attrs_from_mro = set(attrib for cls in getmro(type(self)) for attrib in dir(cls))
            attrs_from_obj = set(self.__dict__)
        return sorted(attrs_from_mro | attrs_from_obj)

    @classmethod
    def from_url(cls, url, use_auth=None):
        '''
        Load entity from URL.

        Args:
            url(str): URL of the entity to load.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        js = nexus.load_by_url(url, token=use_auth)

        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            attr_name = field.name
            raw = js.get(attr_name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[attr_name] = _deserialize_json_to_datatype(type_, raw, use_auth)

        obj = cls(**init_args)
        return obj.evolve(_id=js[JSLD_ID],
                          _rev=js[JSLD_REV],
                          _deprecated=js[JSLD_DEPRECATED],
                          _types=js[JSLD_TYPE])

    @classmethod
    def from_uuid(cls, uuid, use_auth=None):
        '''
        Load entity from UUID.

        Args:
            uuid(str): UUID of the entity to load.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        js = nexus.load_by_uuid(cls._base_url, uuid, token=use_auth) # pylint: disable=no-member

        if js is None:
            return None

        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            attr_name = field.name
            raw = js.get(attr_name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[attr_name] = _deserialize_json_to_datatype(type_, raw, use_auth)

        obj = cls(**init_args)
        return obj.evolve(_id=js[JSLD_ID],
                          _rev=js[JSLD_REV],
                          _deprecated=js[JSLD_DEPRECATED],
                          _types=js[JSLD_TYPE])

    @classmethod
    def from_name(cls, name, use_auth=None):
        '''Load entity from name.

        Args:
            name(str): Name of the entity to load.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        # pylint: disable=no-member
        uuid = nexus.find_uuid_by_name(cls._base_url, name, token=use_auth)
        if uuid:
            return cls.from_uuid(uuid, use_auth)
        else:
            return None

    @classmethod
    def find_by(cls, all_versions=False, all_domains=False, all_organizations=False,
                query=None, use_auth=None, **properties): # TODO improve query params passing
        '''Load entity from properties.

        Args:
            collection_address(str): Selected collection to list, filter or search;
                for example: ``/myorg/mydomain``, ``/myorg/mydomain/myschema/v1.0.0``
            query(dict): Provide explicit nexus query.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
            **properties: Keyword args. If ``key`` has words separated by double underscore they
                will be replaced with ``/`` forming deep path for the query. Single underscores
                will be replaced with ``:`` explicitly specifying namespaces(otherwise default
                ``nsg:`` namespace will be used).
        Returns:
            Results iterator.
        '''

        # pylint: disable=too-many-locals
        # build collection address
        version = getattr(cls, '_url_version', VERSION)
        url_org = getattr(cls, '_url_org', ORG)
        url_domain = getattr(cls, '_url_domain', 'simulation')
        if all_versions:
            collection_address = '/%s/%s/%s' % (url_org, url_domain, cls.__name__.lower())
        elif all_domains:
            collection_address = '/%s' % url_org
        elif all_organizations:
            collection_address = None
        else:
            collection_address = '/%s/%s/%s/%s' % (url_org, url_domain, cls.__name__.lower(),
                                                   version)

        if query is None:
            # prepare properties
            props = []
            for key, value in six.iteritems(properties):
                path = resolve_path(key)

                if isinstance(value, OntologyTerm):
                    props.append({'op': 'eq', 'path': path, 'value': value.url})
                elif isinstance(value, tuple):
                    props.append({'op': value[0], 'path': path, 'value': value[1]})
                elif isinstance(value, Identifiable):
                    props.append({'op': 'eq', 'path': path, 'value': value.id})
                else:
                    props.append({'op': 'eq', 'path': path, 'value': value})

            props.append({'op': 'in', 'path': 'rdf:type', 'value': cls.get_type()})

            query = {'op': 'and', 'value': props}

        location = nexus.find_by(collection_address, query, token=use_auth)
        if location is not None:
            return NexusResultsIterator(cls, location, use_auth)
        return None

    def evolve(self, **changes):
        '''Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''

        hidden_attrs = {}
        # copy hidden attrs values from changes(remove with pop) else from original if present
        for attr_name in ['_id', '_rev', '_deprecated', '_types', '_proxied_type',
                          '_proxied_object', '_proxied_token']:
            attr_value = Ellipsis

            # take value from original if present
            if attr_name in self.__dict__:            # can't use hasattr as it will call getattr
                attr_value = getattr(self, attr_name) # and that will cause recursion to _getattr_

            # prefer value explicitly provided in changes
            attr_value = changes.pop(attr_name, attr_value)

            if attr_value is not Ellipsis:
                hidden_attrs[attr_name] = attr_value

        obj = super(Identifiable, self).evolve(**changes)

        for attr_name in hidden_attrs:
            obj._force_attr(attr_name, hidden_attrs[attr_name]) # pylint: disable=protected-access

        return obj

    def as_json_ld(self):
        '''Get json-ld representation of the Entity
        Return json with added json-ld properties such as @context and @type
        @type is filled from the self._types
        '''
        attrs = attr.fields(type(self))
        rv = {}
        for attribute in attrs:
            attr_value = getattr(self, attribute.name)
            if attr_value is not None: # ignore empty values
                attr_name = attribute.name
                if isinstance(attr_value, (tuple, list, set)):
                    rv[attr_name] = [_serialize_obj(i) for i in attr_value]
                elif isinstance(attr_value, dict):
                    rv[attr_name] = dict((
                        attr.asdict(kk) if attr.has(type(kk)) else kk,
                        attr.asdict(vv) if attr.has(type(vv)) else vv)
                        for kk, vv in six.iteritems(attr_value))
                else:
                    rv[attr_name] = _serialize_obj(attr_value)
        rv[JSLD_CTX] = []
        vocab = getattr(self, '_vocab', None)
        if vocab is not None:
            rv[JSLD_CTX].append({'@vocab': vocab})
        rv[JSLD_CTX].append({'wasAttributedTo': {'@id': 'prov:wasAttributedTo'},
                             'dateCreated': {'@id': 'schema:dateCreated'}})
        rv[JSLD_CTX].append(NSG_CTX)
        if not hasattr(self, '_types'):
            self._force_attr('_types', ['prov:Entity', self.get_type()])
        rv[JSLD_TYPE] = self.types
        return rv


@attributes({
    'downloadURL': AttrOf(str, default=None),
    'accessURL': AttrOf(str, default=None),
    'contentSize': AttrOf(dict, default=None),
    'digest': AttrOf(dict, default=None),
    'mediaType': AttrOf(str, default=None),
    'originalFileName': AttrOf(str, default=None),
    'storageType': AttrOf(str, default=None),
    })
class Distribution(Frozen):
    '''External resource representations,
    this can be a file or a folder on gpfs

    Args:
        downloadURL(str): For directly accessible resources for example files.
        accessURL(str): For container locations for example folders.
        contentSize(int): If known in advance size of the resource.
        digest(int): Hash/Checksum of the resource.
        mediaType(str): Type of the resource accessible by the downloadURL.
        originalFileName(str): File name which was submitted as an attachment.
        storageType(str): storage type, will contain `gpfs` for gpfs links.

    either `downloadURL` for files or `accessURL` for folders must be provided'''

    def __attrs_post_init__(self):
        if not self.downloadURL and not self.accessURL: # pylint: disable=no-member
            raise ValueError('downloadURL or accessURL must be provided')


@attributes({
    'value': AttrOf(str),
    'unitCode': AttrOf(str),
    })
class QuantitativeValue(Frozen):
    '''External resource representations,
    this can be a file or a folder on gpfs

    Args:
        value(str): Value.
        unitCode(str): The unit of measurement given using the UN/CEFACT Common Code (3 characters)
            or a URL. Other codes than the UN/CEFACT Common Code may be used with a prefix followed
            by a colon.
    '''
    pass


@attributes({
    'url': AttrOf(str),
    'label': AttrOf(str),
    })
class OntologyTerm(Frozen):
    '''Ontology term such as brain region or species

    Args:
        url(str): Ontology term url identifier.
        label(str): Label for the ontology term.
    '''
    pass


@attributes({'brainRegion': AttrOf(OntologyTerm)})
class BrainLocation(Frozen):
    '''Brain location'''
    pass
