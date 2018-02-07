'''Base simulation entities'''
import typing
import six

import attr
from attr.validators import instance_of, optional

from uuid import UUID

from entity_management import nexus
from entity_management.settings import JSLD_ID, JSLD_REV, JSLD_DEPRECATED, ENTITY_CTX, NSG_CTX


def _optional_of(type_):
    '''Composition of optional and instance_of'''
    return optional(instance_of(type_))


def _deserialize_json_to_datatype(data_type, data_raw):
    '''Deserialize raw data json to data_type'''
    # first check if it is a collection
    if isinstance(data_raw, list):
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
            data = _deserialize_json_to_datatype(list_element_type, data_element)
            result_list.append(data)
        # if only one then probably nexus is just responding with the collection for single element
        # TODO check this with nexus it might be a bug on their side
        if len(result_list) == 1:
            return result_list[0]
        else:
            return result_list
    elif issubclass(data_type, Identifiable):
        # make lazy proxy for identifiable object
        obj = Identifiable(uuid=nexus.get_uuid_from_url(data_raw['@id']))
        object.__setattr__(obj, '_proxied_type', data_type)
        object.__setattr__(obj, 'types', ['nsg:Entity', 'nsg:' + data_type.__name__])
        return obj
    elif isinstance(data_raw, dict):
        return data_type(**data_raw)
    else:
        return data_type(data_raw)


def _attrs_pos(cls):
    '''Clone all mandatory/positional attr fields of the cls
    Return dictionary with name as key and as value new attribute with cloned properties
    '''
    return {field.name: attr.ib(**{slot: getattr(field, slot) # name becomes key so skip it
                                   for slot in field.__slots__ if slot != 'name'})
            for field in attr.fields(cls)
            # only fields which are part of __init__ and have NO default value
            if field.init and field.default == attr.NOTHING}


def _attrs_kw(cls):
    '''Clone all optional/keyword attr fields of the cls.
    Return dictionary with name as key and as value new attribute with cloned properties
    '''
    return {field.name: attr.ib(**{slot: getattr(field, slot) # name becomes key so skip it
                                   for slot in field.__slots__ if slot != 'name'})
            for field in attr.fields(cls)
            # only fields which are part of __init__ and have default value
            if field.init and field.default != attr.NOTHING}


def _merge(*dicts):
    '''Merge dictionaries using update from left to right'''
    result = {}
    for d in dicts:
        result.update(d)
    return result


@attr.s(frozen=True)
class _Frozen(object):
    '''Utility class with evolve method'''

    def evolve(self, **changes):
        '''Create new instance of the frozen(immutable) object with *changes* applied.

        :param changes: Keyword changes in the new copy, should be a subset of class
                        constructor(__init__) keyword arguments.'''

        return attr.evolve(self, **changes)


# copied from attrs, their standard way to make validators
@attr.s(repr=False, slots=True, hash=True)
class _ListOfValidator(object):
    '''Validate list of type'''
    type_ = attr.ib()

    def __call__(self, inst, attribute, value):
        '''
        We use a callable class to be able to change the ``__repr__``.
        '''
        if type(value) != list or len(value) == 0:
            raise TypeError(
                "'{name}' must be non empty list"
                .format(name=attribute.name), attribute, self.type_, value,
            )

        if not all(isinstance(v, self.type_) for v in value):
            raise TypeError(
                "'{name}' must be list of {type!r} (got {value!r} that is a "
                '{actual!r}).'
                .format(name=attribute.name, type=self.type_,
                        actual=type(value), value=value),
                attribute, self.type_, value,
            )

    def __repr__(self):
        return (
            '<instance_of validator for list of type {type!r}>'
            .format(type=self.type_)
        )


def _list_of(type_):
    '''
    A validator that raises a :exc:`TypeError` if the initializer is called
    with a list of wrong types for this particular attribute (checks are performed
    using :func:`isinstance` therefore it's also valid to pass a tuple of types).

    :param type_: The type to check for.
    :type type_: type or tuple of types

    :raises TypeError: With a human readable error message, the attribute
        (of type :class:`attr.Attribute`), the expected type, and the value it
        got.
    '''
    return _ListOfValidator(type_)


class _IdentifiableMeta(type):
    '''Make Identifiable behave as it's _proxied_type, _proxied_type is set by json-ld
    deserialization'''
    def __instancecheck__(cls, inst):
        ''''''
        if hasattr(inst, '_proxied_type'):
            # if instance has _proxied_type then it is a proxy
            # compare to proxied type
            return cls == inst._proxied_type # pylint: disable=protected-access
        else:
            # fallback to default check
            return cls == type(inst)


@attr.s(these={
    'uuid': attr.ib(
        type=str,
        validator=optional(lambda inst, attr, value: UUID(value)),
        default=None),
    'types': attr.ib(
        init=False,
        default=attr.Factory(
            lambda self: ['nsg:Entity', 'nsg:' + type(self).__name__], takes_self=True))})
class Identifiable(_Frozen):
    '''Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    request to that entity.'''
    __metaclass__ = _IdentifiableMeta

    def __getattr__(self, name):
        if isinstance(self, Identifiable):
            # Identifiable instances behave like proxies, set it up and then forward attr request
            if not hasattr(self, '_proxied_object'):
                object.__setattr__(self, '_proxied_object', self._proxied_type.from_uuid(self.uuid))
            if self._proxied_object is None:
                raise ValueError('Unable to find proxied entity for uuid:%s and %s' %
                                 (self.uuid, self._proxied_type))
            return getattr(self._proxied_object, name)
        else:
            # subclasses of Identifiable just raise if arrived in __getattr__
            raise AttributeError("No attribute '%s' in %s" % (name, type(self)))

    def __dir__(self):
        '''If Identifiable is a proxy(has _proxied_object attribute) then collect attributes from
        proxied object'''
        current = self.__dict__.keys()
        if hasattr(self, '_proxied_object'):
            return sorted(set(current + dir(self._proxied_object)))
        else:
            return sorted(current)

    def as_json_ld(self):
        '''Get json-ld representation of the Entity
        Return json with added json-ld properties such as @context and @type
        @type is filled from the self.types
        '''
        attributes = attr.fields(type(self))
        rv = {}
        essential_attrs = lambda attribute, value: value and attribute.name not in (
                'uuid', 'rev', 'types', 'deprecated')
        for attribute in attributes:
            attr_value = getattr(self, attribute.name)
            if not essential_attrs(attribute, attr_value):
                continue
            if attr.has(type(attr_value)):
                if issubclass(type(attr_value), Identifiable):
                    rv[attribute.name] = {'@id': '%s/%s' % (attr_value.base_url, attr_value.uuid),
                                          '@type': attr_value.types,
                                          'name': 'dummy'} # TODO remove when nexus starts using
                                                           # graph traversal for validation
                else:
                    rv[attribute.name] = attr.asdict(
                            attr_value,
                            recurse=True,
                            filter=essential_attrs)
            elif isinstance(attr_value, (tuple, list, set)):
                rv[attribute.name] = [
                        attr.asdict(i, recurse=True, filter=essential_attrs)
                        if attr.has(type(i)) else i
                        for i in attr_value]
            elif isinstance(attr_value, dict):
                rv[attribute.name] = dict((
                    attr.asdict(kk) if attr.has(type(kk)) else kk,
                    attr.asdict(vv) if attr.has(type(vv)) else vv)
                    for kk, vv in six.iteritems(attr_value))
            else:
                rv[attribute.name] = attr_value
        rv['@context'] = [ENTITY_CTX, NSG_CTX,
                          {
                              'accessURL': {'@id': 'schema:accessURL'},
                              'downloadURL': {'@id': 'schema:downloadURL'},
                              'distribution': {'@id': 'schema:distribution'},
                              'mediaType': {'@id': 'schema:mediaType', },
                              'cellPlacement': {'@id': 'nsg:cellPlacement'},
                              'memodelRelease': {'@id': 'nsg:memodelRelease'},
                          }]
        rv['@type'] = self.types # pylint: disable=no-member
        return rv


@attr.s(these=_merge(
    {'name': attr.ib(type=str, validator=instance_of(str))},
    _attrs_pos(Identifiable),
    {'description': attr.ib(type=str, validator=_optional_of(str), default=None),
     'rev': attr.ib(type=int, validator=_optional_of(int), default=None),
     'deprecated': attr.ib(type=bool, default=None)},
    _attrs_kw(Identifiable)))
class Entity(Identifiable):
    '''Models of many things such as cells, ion channels, circuits, whole brains'''
    base_url = None

    @classmethod
    def from_uuid(cls, uuid):
        '''Load entity from UUID.'''
        js = nexus.load_by_uuid(cls.base_url, uuid)

        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            name = field.name
            raw = js.get(name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[name] = _deserialize_json_to_datatype(type_, raw)

        entity = cls(uuid=js[JSLD_ID],
                     rev=js[JSLD_REV],
                     deprecated=js[JSLD_DEPRECATED],
                     **init_args)
        return entity

    @classmethod
    def from_name(cls, name):
        '''Load entity from name.'''
        uuid = nexus.find_uuid_by_name(cls.base_url, name)
        if uuid:
            return cls.from_uuid(uuid)
        else:
            return None

    def save(self):
        '''Save or update entity.'''
        if self.uuid: # pylint: disable=no-member
            return nexus.update(self)
        else:
            return nexus.save(self)

    def deprecate(self):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.'''
        assert self.uuid is not None # pylint: disable=no-member
        return nexus.deprecate(self)


@attr.s(these=_merge(
    {'modelOf': attr.ib()},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class ModelInstance(Entity):
    '''Model instance collection'''
    pass


@attr.s(these={
    'downloadURL': attr.ib(validator=_optional_of(str), default=None),
    'accessURL': attr.ib(validator=_optional_of(str), default=None),
    'contentSize': attr.ib(validator=_optional_of(int), default=None),
    'digest': attr.ib(validator=_optional_of(int), default=None),
    'mediaType': attr.ib(validator=_optional_of(str), default=None)
    })
class Distribution(_Frozen):
    '''External resource representations,
    this can be a file or a folder on gpfs

    :param str downloadURL: for directly accessible resources for example files
    :param str accessURL: for container locations for example folders
    :param int contentSize: if known in advance size of the resource
    :param int digest: hash/checksum of the resource
    :param str mediaType: type of the resource accessible by the downloadURL

    either `downloadURL` for files or `accessURL` for folders must be provided'''

    def __attrs_post_init__(self):
        if not self.downloadURL and not self.accessURL: # pylint: disable=no-member
            raise ValueError('downloadURL or accessURL must be provided')
