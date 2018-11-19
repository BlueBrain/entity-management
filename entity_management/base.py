'''
Base simulation entities

.. inheritance-diagram:: entity_management.base entity_management.simulation.Entity
                         entity_management.core.Entity
   :parts: 2
'''
from __future__ import print_function
import logging
import operator
from time import sleep
import typing
from datetime import datetime

from pprint import pformat
from dateutil.parser import parse

import six
# noqa pylint: disable=import-error,no-name-in-module,relative-import,ungrouped-imports,wrong-import-order
from six.moves.urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import attr
from attr import set_run_validators, fields

from entity_management import nexus
from entity_management.settings import (BASE_DATA, JSLD_CTX, JSLD_DEPRECATED,
                                        JSLD_ID, JSLD_REV, JSLD_TYPE, NSG_CTX,
                                        ORG, VERSION)
from entity_management.util import (AttrOf, NotInstantiated, _attrs_clone, resolve_path,
                                    _clean_up_dict, _get_list_params, _merge)

L = logging.getLogger(__name__)


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

        def custom_getattr(obj, name):
            '''Overload of __getattribute__ to trigger instantiation of Nexus object
            if the attribute is NotInstantiated'''
            if name == '__class__' or not isinstance(obj, Identifiable):
                return object.__getattribute__(obj, name)

            _attr = object.__getattribute__(obj, name)
            if (_attr is NotInstantiated and name not in set(dir(Identifiable))):
                obj._instantiate()
                return getattr(obj, name)
            else:
                return _attr

        cls.__getattribute__ = custom_getattr

        return attr.attrs(cls, these=these, repr=repr)

    return wrap


@attr.s
class NexusResultsIterator(six.Iterator):
    '''Nexus paginated results iterator'''
    url = attr.ib()
    token = attr.ib()
    total_items = attr.ib(type=int, default=None)
    page_from = attr.ib(type=int, default=None)
    page_size = attr.ib(type=int, default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.url.endswith('/incoming') or self.url.endswith('/outcoming'):
            self.page_from = 0
            self.page_size = 10
        else:
            split_url = urlsplit(self.url)
            query_params = dict(parse_qsl(split_url.query))
            self.page_from = int(query_params['from'])
            self.page_size = int(query_params['size'])

    def __iter__(self):  # pragma: no cover pylint: disable=non-iterator-returned
        return self

    def __next__(self):
        '''Return next entity from the paginated result set, fetch next page if required'''
        # fetch next page if needed
        if self.total_items is None or self.page_from + self.page_size == self._item_index:
            self.page_from = self._item_index
            split_url = urlsplit(self.url)
            self.url = urlunsplit(split_url._replace(
                query=urlencode({'from': self.page_from, 'size': self.page_size})))
            json_payload = nexus.load_by_url(self.url, token=self.token)
            self._page = [entity['resultId']
                          for entity in json_payload['results']]
            self.total_items = int(json_payload['total'])

        if self._item_index >= self.total_items:
            raise StopIteration()

        self._item_index += 1

        id_url = self._page[self._item_index - 1 - self.page_from]
        cls = nexus.get_type(id_url)
        if cls is None:
            print('No python class found for object at url: {} -> Skipping it'.format(id_url))
            return None
        return cls._lazy_init(id=id_url, token=self.token)


def _deserialize_list(data_type, data_raw, token):
    '''Deserialize list of json elements'''
    result_list = []
    # find the type of collection element
    if isinstance(data_type, typing.GenericMeta):
        # the collection was explicitly specified in attr.ib
        # like typing.List[Distribution]
        list_element_type = _get_list_params(data_type)[0]
    else:
        # nexus returns a collection of one element
        # element type is the type specified in attr.ib
        list_element_type = data_type
    for data_element in data_raw:
        data = _deserialize_json_to_datatype(
            list_element_type, data_element, token)
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


def _deserialize_json_to_datatype(data_type, data_raw, token=None):  # noqa pylint: disable=too-many-return-statements
    '''Deserialize raw data json to data_type'''
    if data_raw is None:
        return None

    try:
        if isinstance(data_raw, list):
            return _deserialize_list(data_type, data_raw, token)

        if (  # in case we have bunch of the Identifiable types as a Union
                (type(data_type) is type(typing.Union)  # noqa
                    and all(issubclass(cls, Identifiable) for cls in _get_list_params(data_type)))
                # or we have just Identifiable
                or issubclass(data_type, Identifiable)):
            url = data_raw[JSLD_ID]
            types = data_raw[JSLD_TYPE]
            # root type was used or union of types, try to recover it from url
            if data_type is Identifiable or type(data_type) is type(typing.Union):  # noqa
                data_type = nexus.get_type(url)
            return data_type._lazy_init(id=url, types=types, token=token)

        if issubclass(data_type, OntologyTerm):
            return data_type(url=data_raw[JSLD_ID], label=data_raw['label'])

        if data_type == datetime:
            return parse(data_raw)

        if issubclass(data_type, Frozen):
            # nested obj literals should be deserialized before passed to composite obj constructor
            return data_type(
                **{k: _deserialize_json_to_datatype(attr.fields_dict(data_type)[k].type, v, token)
                   for k, v in six.iteritems(data_raw)
                   if k in attr.fields_dict(data_type)})

        if isinstance(data_raw, dict):
            return data_type(**_clean_up_dict(data_raw))

        return data_type(data_raw)

    except Exception:
        L.error('Error deserializing type: %s for raw data:\n%s', data_type, pformat(data_raw))
        raise


def _serialize_obj(value, fix_types=False):
    '''Serialize object'''
    if isinstance(value, OntologyTerm):
        return {JSLD_ID: value.url, 'label': value.label}

    if isinstance(value, Identifiable):
        # FIXME remove when nexus decides to fix this bug
        # identify entity by url and then remove nsg:Entity if fix_types
        types = set(value.types) if value.types else {}
        if value.id and '/entity/v' in value.id and fix_types:
            types -= {'nsg:Entity'}
        return {JSLD_ID: value.id,
                JSLD_TYPE: list(types),
                'name': ''}  # add fake name to keep nexus happy

    if isinstance(value, datetime):
        return value.isoformat()

    if attr.has(type(value)):
        rv = {}
        for attribute in attr.fields(type(value)):
            attr_name = attribute.name
            attr_value = getattr(value, attr_name)
            if attr_value is not None:  # ignore empty values
                if isinstance(attr_value, (tuple, list, set)):
                    rv[attr_name] = [_serialize_obj(i, fix_types) for i in attr_value]
                elif isinstance(attr_value, dict):
                    rv[attr_name] = dict((kk, _serialize_obj(vv))
                                         for kk, vv in six.iteritems(attr_value))
                else:
                    rv[attr_name] = _serialize_obj(attr_value, fix_types)
        return rv

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

        meta = changes.pop('meta', None)
        obj = attr.evolve(self, **changes)
        if hasattr(obj, 'meta'):
            obj._force_attr('meta', meta or self.meta)  # pylint: disable=no-member
        return obj


class _IdentifiableMeta(type):
    '''Make Identifiable behave as it's _proxied_type, _proxied_type is set by json-ld
    deserialization.
    Initialize class variable _base_url.'''

    def __init__(cls, name, bases, attrs):
        # initialize base_url
        version = getattr(cls, '_url_version', VERSION)
        url_org = getattr(cls, '_url_org', ORG)
        url_domain = getattr(cls, '_url_domain', 'simulation')
        url_name = getattr(cls, '_url_name', name.lower())

        type_id = '%s/%s' % (url_domain, url_name)
        cls.base_url = '%s/%s/%s/%s' % (BASE_DATA, url_org, type_id, version)
        nexus.register_type(type_id, cls)

        super(_IdentifiableMeta, cls).__init__(name, bases, attrs)


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


def from_url(url, use_auth=None):
    '''
    Load entity from URL.

    Args:
        url (str): URL of the entity to load.
        use_auth (str): OAuth token in case access is restricted.
            Token should be in the format for the authorization header: Bearer VALUE.
    '''
    cls = nexus.get_type(url)
    if cls is None:
        raise Exception('Cannot find python class of object at url: {}'.format(url))
    js = nexus.load_by_url(url, token=use_auth)

    # prepare all entity init args
    init_args = {}
    for field in attr.fields(cls):  # pylint: disable=not-an-iterable
        raw = js.get(field.name)
        if field.init and raw is not None:
            type_ = field.type
            init_args[field.name] = _deserialize_json_to_datatype(type_, raw, use_auth)

    return cls(id=js[JSLD_ID], **init_args).evolve(meta=Metadata.from_json(js, token=use_auth))


@six.add_metaclass(_IdentifiableMeta)
@attr.s
class Identifiable(Frozen):
    '''Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    requests to that entity.
    '''
    # entity namespace which should be used for json-ld @type attribute
    _type_namespace = 'nsg'  # Entity classes from specific domains can override this
    _type_name = ''  # Entity classes from specific domains will override this
    id = attr.ib(type=str, default=None)
    meta = attr.ib(type=Metadata, factory=Metadata, init=False)

    def _instantiate(self):
        '''Fetch nexus object with id=self.id and copy its attribute into current object'''
        fetched_instance = type(self).from_url(self.id, self.meta.token)
        for attribute in fields(type(self)):
            self._force_attr(attribute.name, getattr(fetched_instance, attribute.name))

    @classmethod
    def _lazy_init(cls, id, types=None, token=None):  # pylint: disable=redefined-builtin
        '''Instantiate an object and put all its attributes to NotInstantiated
        except "id"'''
        # Running the validator has the side effect of instantiating
        # the object, which we do not want
        set_run_validators(False)
        obj = cls(id=id,
                  **{arg.name: NotInstantiated for arg in
                     set(attr.fields(cls)) - set(attr.fields(Identifiable))})
        obj.meta.token = token
        obj.meta.types = types
        set_run_validators(True)
        return obj

    @classmethod
    def get_type(cls):
        '''Get class type. Can be overriden by class varable _type_name.'''
        return '%s:%s' % (cls._type_namespace, cls._type_name or cls.__name__)

    @property
    def types(self):
        '''Get json-ld types'''
        # in case object has identity(persisted) types might not have been yet retrieved
        if self.meta.types is None and self.id:
            self._instantiate()
        return self.meta.types

    @property
    def incoming(self):
        '''Get an iterator on incoming nodes'''
        return NexusResultsIterator(self.id + '/incoming', self.meta.token)

    @property
    def outcoming(self):
        '''Get an iterator on outcoming nodes'''
        return NexusResultsIterator(self.id + '/outcoming', self.meta.token)

    @classmethod
    def from_url(cls, url, use_auth=None):
        '''
        Load entity from URL.

        Args:
            url (str): URL of the entity to load.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        return from_url(url, use_auth=use_auth)

    @classmethod
    def from_uuid(cls, uuid, use_auth=None):
        '''
        Load entity from UUID.

        Args:
            uuid (str): UUID of the entity to load.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        return cls.from_url('{}/{}'.format(cls.base_url, uuid), use_auth=use_auth)

    @classmethod
    def find_unique(cls, throw=False, on_no_result=None, poll_until_exists=False, **kwargs):
        '''Wrapper around find_by that will:
        - return the result if there is only one result
        - throw if there are more than one results

        Args:
            throw (bool): Whether to throw when no result found
            on_no_result (Callable): A function to be called when no result found and throw==False
            poll_until_exists (bool): flag to enable polling after the execution of on_no_result()
                                     until find_unique returns something. The polling frequency is
                                     2 seconds and the timeout is 1 minute.
            kwargs: Arguments to be passed to the underlying cls.find_by
        '''

        iterator = cls.find_by(**kwargs)
        try:
            result = next(iterator)
        except StopIteration:
            if throw:
                raise Exception('{}.find_unique({}) did not return anything'
                                .format(cls, str(kwargs)))

            if on_no_result:
                result = on_no_result()
                if poll_until_exists:
                    for i in range(30):
                        L.debug('Poll #%s for %s.find_unique(%s)', i, cls, str(kwargs))
                        if cls.find_unique(**kwargs):
                            return result
                        sleep(2)
                    raise Exception('Timeout reached while polling for {}.find_unique({})'
                                    .format(cls, str(kwargs)))
                return result
            else:
                return None

        second = next(iterator, None)
        if second:
            raise Exception('ERROR: {}.find_unique({}) found more than one result.'
                            '\nFirst 2 results are:\n- {}\n- {}'.format(
                                cls, str(kwargs), result.id, second.id))
        return result

    @classmethod
    def find_by(cls, all_versions=False, all_domains=False, all_organizations=False,
                query=None, use_auth=None, **properties):  # TODO improve query params passing
        '''Load entity from properties.

        Args:
            collection_address (str): Selected collection to list, filter or search;
                for example: ``/myorg/mydomain``, ``/myorg/mydomain/myschema/v1.0.0``
            query (dict): Provide explicit nexus query.
            use_auth (str): OAuth token in case access is restricted.
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
        url_org = getattr(cls, '_url_org', ORG)
        url_domain = getattr(cls, '_url_domain', 'simulation')
        url_name = getattr(cls, '_url_name', cls.__name__.lower())
        url_version = getattr(cls, '_url_version', VERSION)
        if all_versions:
            collection_address = '/%s/%s/%s' % (url_org, url_domain, url_name)
        elif all_domains:
            collection_address = '/%s' % url_org
        elif all_organizations:
            collection_address = None
        else:
            collection_address = '/%s/%s/%s/%s' % (url_org, url_domain, url_name, url_version)

        if query is None:
            # prepare properties
            props = []
            for key, value in six.iteritems(properties):
                path = resolve_path(key)

                if isinstance(value, OntologyTerm):
                    props.append(
                        {'op': 'eq', 'path': path, 'value': value.url})
                elif isinstance(value, tuple):
                    props.append(
                        {'op': value[0], 'path': path, 'value': value[1]})
                elif isinstance(value, Identifiable):
                    props.append({'op': 'eq', 'path': path, 'value': value.id})
                else:
                    props.append({'op': 'eq', 'path': path, 'value': value})

            props.append({'op': 'in', 'path': 'rdf:type',
                          'value': cls.get_type()})

            query = {'op': 'and', 'value': props}

        location = nexus.find_by(collection_address, query, token=use_auth)
        if location is not None:
            return NexusResultsIterator(location, use_auth)
        return None

    def as_json_ld(self):
        '''Get json-ld representation of the Entity
        Return json with added json-ld properties such as @context and @type
        '''
        attrs = set(attr.fields(type(self))) - set(attr.fields(Identifiable))
        rv = {}
        fix_types = 'nsg:Entity' in self.types if self.types else False
        for attribute in attrs:  # pylint: disable=not-an-iterable
            attr_value = getattr(self, attribute.name)
            if attr_value is not None:  # ignore empty values
                attr_name = attribute.name
                if isinstance(attr_value, (tuple, list, set)):
                    rv[attr_name] = [_serialize_obj(i, fix_types) for i in attr_value]
                elif isinstance(attr_value, dict):
                    rv[attr_name] = dict((kk, _serialize_obj(vv))
                                         for kk, vv in six.iteritems(attr_value))
                else:
                    rv[attr_name] = _serialize_obj(attr_value, fix_types)
        rv[JSLD_CTX] = []
        vocab = getattr(self, '_vocab', None)
        if vocab is not None:
            rv[JSLD_CTX].append({'@vocab': vocab})
        rv[JSLD_CTX].append({'wasAttributedTo': {'@id': 'prov:wasAttributedTo'},
                             'dateCreated': {'@id': 'schema:dateCreated'}})
        rv[JSLD_CTX].append(NSG_CTX)
        rv[JSLD_TYPE] = self.types
        return rv

    def publish(self, use_auth=None):
        '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes.

        Args:
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if self.id:
            js = nexus.update(self.id, self.meta.rev, self.as_json_ld(), token=use_auth)
        else:
            self.meta.types = ['prov:Entity', self.get_type()]
            js = nexus.create(self.base_url, self.as_json_ld(), token=use_auth)  # noqa pylint: disable=no-member

        self.meta.rev = js[JSLD_REV]
        return self.evolve(id=js[JSLD_ID])

    def deprecate(self, use_auth=None):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.

        Args:
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        self._instantiate()
        js = nexus.deprecate(self.id, self.meta.rev, token=use_auth)
        self.meta.rev = js[JSLD_REV]
        self.meta.deprecated = True
        return self


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
        downloadURL (str): For directly accessible resources for example files.
        accessURL (str): For container locations for example folders.
        contentSize (int): If known in advance size of the resource.
        digest (int): Hash/Checksum of the resource.
        mediaType (str): Type of the resource accessible by the downloadURL.
        originalFileName (str): File name which was submitted as an attachment.
        storageType (str): storage type, will contain `gpfs` for gpfs links.

    either `downloadURL` for files or `accessURL` for folders must be provided'''

    def __attrs_post_init__(self):
        if not self.downloadURL and not self.accessURL:  # pylint: disable=no-member
            raise ValueError('downloadURL or accessURL must be provided')


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
    pass


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
    pass


@attributes({'brainRegion': AttrOf(OntologyTerm)})
class BrainLocation(Frozen):
    '''Brain location'''
    pass
