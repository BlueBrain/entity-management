'''Utilities'''

import typing
import six
import attr
from attr import validators


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


# copied from attrs, their standard way to make validators
@attr.s(repr=False, slots=True, hash=True)
class _SubClassOfValidator(object):
    '''SubClass validator'''
    type_ = attr.ib()

    def __call__(self, inst, attribute, value):
        '''
        We use a callable class to be able to change the ``__repr__``.
        '''
        # pylint: disable=protected-access
        value_type = value._proxied_type if hasattr(value, '_proxied_type') else type(value)

        if not issubclass(value_type, self.type_):
            raise TypeError(
                "'{name}' must be a subclass of {type!r} (got {value!r} that is a "
                "{actual!r})."
                .format(name=attribute.name, type=self.type_,
                        actual=value.__class__, value=value),
                attribute, self.type_, value,
            )

    def __repr__(self):
        return (
            "<subclass_of validator for type {type!r}>"
            .format(type=self.type_)
        )


def subclass_of(type_):
    '''
    A validator that raises a :exc:`TypeError` if the initializer is called
    with a wrong type for this particular attribute (checks are performed using
    :func:`issubclass` therefore it's also valid to pass a tuple of types).

    Args:
        type_(type): The type to check for.

    Raises:
        TypeError: With a human readable error message, the attribute
        (of type :class:`attr.Attribute`), the expected type, and the value it
        got.
    '''
    return _SubClassOfValidator(type_)


def optional_of(type_):
    '''Composition of optional and subclass_of'''
    return validators.optional(subclass_of(type_))


class AttrOf(object):
    '''Create an object with self.is_positional(Bool) and self.fn(Callable) that will be used
    to create an attr.ib by invoking Callable. is_positional signifies that attribute will have
    no default value and will appear in class init method as positional argument else it will
    be kwarg.

    This is needed so that @attributes decorator can create the attr.ib's in order
    because they have a counter inside that is used to order them.
    '''

    def __init__(self, type_, optional=Ellipsis, default=Ellipsis):
        if isinstance(type_, typing.GenericMeta):
            # the collection was explicitly specified in attr.ib
            # like typing.List[Distribution]
            assert type_.__extra__ == list
            list_element_type = type_.__args__[0]
            if type(list_element_type) == type(typing.Union):
                types = list_element_type.__args__
                validator = _list_of(types)
            else:
                validator = _list_of(type_.__args__[0])
        else:
            if optional is Ellipsis:
                if default is Ellipsis:
                    validator = subclass_of(type_)
                elif default is None:
                    validator = optional_of(type_)
            else:
                if optional is False:
                    validator = subclass_of(type_)
                else:
                    validator = optional_of(type_)

        if default is Ellipsis: # no default value -> positional arg
            self.is_positional = True
            self.fn = lambda: attr.ib(type=type_, validator=validator)
        else:
            self.is_positional = False
            self.fn = lambda: attr.ib(type=type_, validator=validator, default=default)

    def __call__(self):
        return self.fn()


def attributes(attr_dict=None):
    '''decorator to simplify creation of classes that have args and kwargs'''
    if attr_dict is None:
        attr_dict = {} # just inherit attributes from parent class

    def wrap(cls):
        '''wraps'''
        these = _merge(
            _attrs_pos(cls),
            {k: v() for k, v in attr_dict.items() if v.is_positional},
            {k: v() for k, v in attr_dict.items() if not v.is_positional},
            _attrs_kw(cls))
        return attr.attrs(cls, these=these)

    return wrap


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
        if dicts:
            result.update(d)
    return result


def _clean_up_dict(d):
    '''Produce new dictionary without json-ld attrs which start with @'''
    return {k: v for k, v in six.iteritems(d) if not k.startswith('@')}
