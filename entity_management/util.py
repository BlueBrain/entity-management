'''Utilities'''

import typing
from inspect import getmro
from six.moves.urllib.parse import quote as parse_quote

import attr
from attr.validators import instance_of as instance_of_validator, optional as optional_validator
import six

from devtools import pformat

# copied from attrs, their standard way to make validators


@attr.s(repr=False, slots=True, hash=True)
class _ListOfValidator(object):
    '''Validate list of type'''
    type_ = attr.ib()
    default = attr.ib()

    def __call__(self, inst, attribute, value):
        '''
        We use a callable class to be able to change the ``__repr__``.
        '''
        if self.default is not None and value is None:
            raise TypeError(
                "'{name}' must be provided"
                .format(name=attribute.name), attribute, self.type_, value,
            )

        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "'{name}' must be a list"
                    .format(name=attribute.name), attribute, self.type_, value,
                )
            if not all(isinstance(v, self.type_) for v in value):
                raise TypeError(
                    "'{name}' must be list of {type!r} (got {value!r} that is a "
                    '{actual!r}).'
                    .format(name=attribute.name, type=self.type_, actual=type(value), value=value),
                    attribute, self.type_, value,
                )

    def __repr__(self):
        return (
            '<instance_of validator for list of type {type!r}>'
            .format(type=self.type_)
        )


def _list_of(type_, default):
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
    return _ListOfValidator(type_, default)


@attr.s(repr=False, slots=True, hash=True)
class _NotInstatiatedValidator(object):
    '''A validator that allows NotInstantiated values.'''
    validator = attr.ib()

    def __call__(self, inst, attribute, value):
        if value is NotInstantiated:
            return

        self.validator(inst, attribute, value)  # pylint: disable=not-callable

    def __repr__(self):
        return "<not instantiated validator for {what} or None>".format(what=repr(self.validator))


class NotInstantiated(object):  # pylint: disable=no-init
    '''A class for not instantiated attributes
    Trying to access an attribute with this value will trigger
    the instantiation. A Nexus query will be performed and the attribute
    will be filled with the real value'''
    def __repr__(self):
        return '<not instantiated>'


def _get_union_params(union):
    '''Return Union elements for all python'''
    try:
        return union.__args__
    except AttributeError:
        return union.__union_params__


def _get_list_params(a_list):
    '''Return List elements for all python'''
    try:
        return a_list.__args__
    except AttributeError:
        return a_list.__parameters__


class AttrOf(object):
    '''Create an object with self.is_positional(Bool) and self.fn(Callable) that will be used
    to create an attr.ib by invoking Callable. is_positional signifies that attribute will have
    no default value and will appear in class init method as positional argument else it will
    be kwarg.

    This is needed so that @attributes decorator can create the attr.ib's in order
    because they have a counter inside that is used to order them.
    '''

    def __init__(self, type_, optional=Ellipsis, default=Ellipsis, validators=None):
        if validators is None:
            validators = []

        def instance_of(type_):
            '''instance_of'''
            return _NotInstatiatedValidator(instance_of_validator(type_))

        def optional_of(type_):
            '''optional_of'''
            return optional_validator(instance_of(type_))

        if (hasattr(type_, '__origin__') and issubclass(type_.__origin__, typing.List)):
            # the collection was explicitly specified in attr.ib
            # like typing.List[Distribution]
            list_element_type = _get_list_params(type_)[0]
            if (hasattr(list_element_type, '__args__') or
                    hasattr(list_element_type, '__union_params__')):
                types = _get_union_params(list_element_type)
                validator = _list_of(types, default)
            else:
                validator = _list_of(list_element_type, default)
        else:
            if optional is Ellipsis:
                if default is None:  # default explicitly provided as None
                    validator = optional_of(type_)
                else:  # default either not provided -> mandatory, or initialized with value
                    validator = instance_of(type_)
            else:
                if optional is False:
                    validator = instance_of(type_)
                else:
                    validator = optional_of(type_)
        self.is_positional = default is Ellipsis

        validators = [validator] + validators if isinstance(validators, list) else [validators]
        if default is Ellipsis:  # no default value -> positional arg
            self.fn = lambda: attr.ib(type=type_, validator=validators, repr=False)
        else:
            self.fn = lambda: attr.ib(type=type_, default=default, validator=validators, repr=False)

    def __call__(self):
        return self.fn()


def _attrs_clone(cls, check_default):
    '''Clone all mandatory/positional(check_default=eq) or optional/keyword(check_default=ne)
    attr fields of the cls including parents. Return dictionary with name as key and as value
    new attribute with cloned properties
    '''
    fields = {}
    # reverse mro to override fields correctly
    for parent_cls in reversed(getmro(cls)):
        if attr.has(parent_cls):
            for field in attr.fields(parent_cls):
                if field.init and check_default(field.default, attr.NOTHING):
                    # clone field with name as dictionary key => skip it from slots
                    fields[field.name] = attr.ib(**{slot: getattr(field, slot)
                                                    for slot in field.__slots__ if slot != 'name'})
    return fields


def _merge(pos_inherited, pos_new, kw_new, kw_inherited):
    '''Merge dictionaries using update from left to right'''
    result = {}
    # remove keys, so they can be overridden
    for key in pos_new.keys():
        kw_inherited.pop(key, None)
    result.update(pos_inherited)
    result.update(pos_new)
    result.update(kw_inherited)
    result.update(kw_new)
    return result


def _clean_up_dict(d):
    '''Produce new dictionary without json-ld attrs which start with @'''
    return {k: v for k, v in six.iteritems(d) if not k.startswith('@')}


def quote(url):
    '''Helper function for urllib.parse.quote with safe="".'''
    return parse_quote(url, safe='')


class PP(object):
    '''Lazy pretty printer with pformat from devtools.'''
    def __init__(self, value, highlight=True):
        self.value = value
        self.highlight = highlight

    def __str__(self):
        return pformat(self.value, highlight=self.highlight)
