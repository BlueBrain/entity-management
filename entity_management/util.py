'''Utilities'''

import typing
from urllib.parse import quote as parse_quote

import attr
from attr.validators import instance_of as instance_of_validator, optional as optional_validator

from devtools import pformat

# copied from attrs, their standard way to make validators


@attr.s(repr=False, slots=True, hash=True)
class _ListOfValidator():
    '''Validate list of type'''
    type_ = attr.ib()
    default = attr.ib()

    def __call__(self, inst, attribute, value):
        '''
        We use a callable class to be able to change the ``__repr__``.
        '''
        if self.default is not None and value is None:
            raise TypeError(f"'{attribute.name}' must be provided", attribute, self.type_, value)

        if value is not None:
            if not isinstance(value, list):
                raise TypeError(f"'{attribute.name}' must be a list", attribute, self.type_, value)
            if not all(isinstance(v, self.type_) for v in value):
                raise TypeError(
                    f"'{attribute.name}' must be list of {self.type_!r} (got {value!r} that is a "
                    f'{type(value)!r}).', attribute, self.type_, value,
                )

    def __repr__(self):
        return f'<instance_of validator for list of type {self.type_!r}>'


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
class _NotInstatiatedValidator():
    '''A validator that allows NotInstantiated values.'''
    validator = attr.ib()

    def __call__(self, inst, attribute, value):
        if value is NotInstantiated:
            return

        self.validator(inst, attribute, value)  # pylint: disable=not-callable

    def __repr__(self):
        return f"<not instantiated validator for {repr(self.validator)} or None>"


class NotInstantiated():
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


class AttrOf():
    '''Create an object with self.fn(Callable) that will be used to create an attr.ib by invoking
    Callable.

    .. deprecated:: 1.2.9
        Use regular attrs. This used to do some magic for previous versions of attrs.
    '''

    def __init__(self, type_, default=attr.NOTHING, validators=None):
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
            if default is None:  # default explicitly provided as None
                validator = optional_of(type_)
            else:  # default either not provided -> mandatory, or initialized with value
                validator = instance_of(type_)

        validators = [validator] + validators if isinstance(validators, list) else [validators]
        self.fn = lambda: attr.ib(type=type_,
                                  default=default,
                                  validator=validators,
                                  repr=False,
                                  kw_only=True)

    def __call__(self):
        return self.fn()


def _clean_up_dict(d):
    '''Produce new dictionary without json-ld attrs which start with @'''
    return {k: v for k, v in d.items() if not k.startswith('@')}


def quote(url):
    '''Helper function for urllib.parse.quote with safe="".'''
    return parse_quote(url, safe='')


class PP():
    '''Lazy pretty printer with pformat from devtools.'''
    def __init__(self, value, highlight=True):
        self.value = value
        self.highlight = highlight

    def __str__(self):
        return pformat(self.value, highlight=self.highlight)
