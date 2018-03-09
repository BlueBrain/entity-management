'''Base simulation entities'''
import typing
import six

from inspect import getmro

import attr

from entity_management import nexus
from entity_management.util import _clean_up_dict
from entity_management.util import attributes, AttrOf
from entity_management.settings import (DATA_SIM, VERSION, JSLD_ID, JSLD_REV, JSLD_DEPRECATED,
                                        ENTITY_CTX, NSG_CTX)


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
        obj = Identifiable()
        return obj.evolve(_proxied_type=data_type,
                          _types=['nsg:Entity', 'nsg:' + data_type.__name__],
                          _uuid=nexus.get_uuid_from_url(data_raw[JSLD_ID]))
    elif isinstance(data_raw, dict):
        return data_type(**_clean_up_dict(data_raw))
    else:
        return data_type(data_raw)


@attr.s(frozen=True)
class Frozen(object):
    '''Utility class making derived classed immutable. Use `evolve` method to introduce changes.'''

    def evolve(self, **changes):
        '''Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        '''

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
    deserialization.
    Initialize class variable _base_url.'''

    def __init__(cls, name, bases, attrs):
        cls._base_url = DATA_SIM + '/' + name.lower() + '/' + VERSION
        super(_IdentifiableMeta, cls).__init__(name, bases, attrs)

    def __instancecheck__(cls, inst):
        ''''''
        if hasattr(inst, '_proxied_type'):
            # if instance has _proxied_type then it is a proxy
            # compare to proxied type
            return cls == inst._proxied_type # pylint: disable=protected-access
        else:
            # fallback to default check
            return cls == type(inst)


@attributes()
class Identifiable(Frozen):
    '''Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    requests to that entity.'''
    # Identifiable can be used on its own but json-ld deserialization will set _proxied_type
    # to make it behave like proxy to underlying Entity instance

    __metaclass__ = _IdentifiableMeta

    def __attrs_post_init__(self):
        object.__setattr__(self, '_types', ['nsg:Entity', 'nsg:' + type(self).__name__])

    def __getattr__(self, name):
        if type(self) == Identifiable: # isinstance is overriden in metaclass which is true for
                                       # all subclasses of Identifiable
            # Identifiable instances behave like proxies, set it up and then forward attr request
            if '_proxied_object' not in self.__dict__: # can't use hasattr as it will call getattr
                                                       # and that will cause recursion to _getattr_
                object.__setattr__(self, '_proxied_object',
                                   self._proxied_type.from_uuid(self._uuid))
            if self._proxied_object is None:
                raise ValueError('Unable to find proxied entity for uuid:%s and %s' %
                                 (self._uuid, self._proxied_type))
            return getattr(self._proxied_object, name)
        else:
            # subclasses of Identifiable just raise if arrived in __getattr__
            raise AttributeError("No attribute '%s' in %s" % (name, type(self)))

    def __dir__(self):
        '''If Identifiable is a proxy(has _proxied_type attribute) then collect attributes from
        proxied object'''
        if hasattr(self, '_proxied_type') and self.name: # access proxied attr to trigger lazy load
            attrs_from_mro = set(attrib for cls in getmro(type(self._proxied_object))
                                        for attrib in dir(cls))
            attrs_from_obj = set(self._proxied_object.__dict__)
        else:
            attrs_from_mro = set(attrib for cls in getmro(type(self)) for attrib in dir(cls))
            attrs_from_obj = set(self.__dict__)
        return sorted(attrs_from_mro | attrs_from_obj)

    @classmethod
    def from_uuid(cls, uuid):
        '''Load entity from UUID.'''
        js = nexus.load_by_uuid(cls._base_url, uuid) # pylint: disable=no-member

        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            attr_name = field.name
            raw = js.get(attr_name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[attr_name] = _deserialize_json_to_datatype(type_, raw)

        obj = cls(**init_args)
        return obj.evolve(_uuid=js[JSLD_ID], _rev=js[JSLD_REV], _deprecated=js[JSLD_DEPRECATED])

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
        for attr_name in ['_uuid', '_rev', '_deprecated', '_types', '_proxied_type',
                          '_proxied_object']:
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
            object.__setattr__(obj, attr_name, hidden_attrs[attr_name])

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
            attr_name = attribute.name
            if attr.has(type(attr_value)):
                if issubclass(type(attr_value), Identifiable):
                    rv[attr_name] = {'@id': '%s/%s' % (getattr(attr_value, '_base_url'),
                                                       getattr(attr_value, '_uuid')),
                                     '@type': getattr(attr_value, '_types'),
                                     'name': 'dummy'} # TODO remove when nexus starts using
                                                      # graph traversal for validation
                else:
                    rv[attr_name] = attr.asdict(
                            attr_value,
                            recurse=True)
            elif isinstance(attr_value, (tuple, list, set)):
                rv[attr_name] = [
                        attr.asdict(i, recurse=True)
                        if attr.has(type(i)) else i
                        for i in attr_value]
            elif isinstance(attr_value, dict):
                rv[attr_name] = dict((
                    attr.asdict(kk) if attr.has(type(kk)) else kk,
                    attr.asdict(vv) if attr.has(type(vv)) else vv)
                    for kk, vv in six.iteritems(attr_value))
            else:
                rv[attr_name] = attr_value
        rv['@context'] = [ENTITY_CTX, NSG_CTX,
                          {
                              'accessURL': {'@id': 'schema:accessURL', '@type': '@id'},
                              'downloadURL': {'@id': 'schema:downloadURL', '@type': '@id'},
                              'distribution': {'@id': 'schema:distribution'},
                              'mediaType': {'@id': 'schema:mediaType', },
                              'cellPlacement': {'@id': 'nsg:cellPlacement'},
                              'memodelRelease': {'@id': 'nsg:memodelRelease'},
                              'property': {'@id': 'nsg:property'},
                              'synapseRelease': {'@id': 'nsg:synapseRelease'},
                              'nodeCollection': {'@id': 'nsg:nodeCollection'},
                              'isPartOf': {'@id': 'dcterms:isPartOf'},
                          }]
        rv['@type'] = self._types
        return rv


@attributes({
    'downloadURL': AttrOf(str, default=None),
    'accessURL': AttrOf(str, default=None),
    'contentSize': AttrOf(dict, default=None),
    'digest': AttrOf(dict, default=None),
    'mediaType': AttrOf(str, default=None),
    'originalFileName': AttrOf(str, default=None),
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

    either `downloadURL` for files or `accessURL` for folders must be provided'''

    def __attrs_post_init__(self):
        if not self.downloadURL and not self.accessURL: # pylint: disable=no-member
            raise ValueError('downloadURL or accessURL must be provided')


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
    'distribution': AttrOf(Distribution, default=None)
    })
class Entity(Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''

    @classmethod
    def from_name(cls, name):
        '''Load entity from name.'''
        uuid = nexus.find_uuid_by_name(cls._base_url, name) # pylint: disable=no-member
        if uuid:
            return cls.from_uuid(uuid)
        else:
            return None

    def save(self):
        '''Save or update entity.'''
        if hasattr(self, '_uuid') and self._uuid:
            js = nexus.update(self._base_url, self._uuid, self._rev, self.as_json_ld())
        else:
            js = nexus.save(self._base_url, self.as_json_ld())
        return self.evolve(_uuid=nexus.get_uuid_from_url(js[JSLD_ID]), _rev=js[JSLD_REV])

    def deprecate(self):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.'''
        assert self._uuid is not None
        js = nexus.deprecate(self._base_url, self._uuid, self._rev)
        return self.evolve(_rev=js[JSLD_REV], _deprecated=True)

    def attach(self, file_name, data, content_type='text/html'):
        '''Attach binary data to entity.
        Attached data downloadURL and other metadata will be available in ``distribution``.

        Args:
            file_name(str): Original file name.
            data(file): File like data stream.
            content_type(str): Content type with which attachment will be delivered when
                accessed with the download url. Default value is `text/html`.

        Returns:
            New instance with distribution attribute updated.
        '''
        assert self._uuid is not None # pylint: disable=no-member
        js = nexus.attach(self._base_url, self._uuid, self._rev, file_name, data, content_type)
        return self.evolve(_rev=js[JSLD_REV], distribution=_deserialize_json_to_datatype(
            Distribution, js['distribution'][0]))


@attributes()
class Release(Entity):
    '''Release base entity'''
    pass


@attributes({'modelOf': AttrOf(str, default=None)})
class ModelInstance(Entity):
    '''Model instance collection'''
    pass
