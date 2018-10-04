'''Utilities'''

import re
import typing
from inspect import getmro

import attr
from attr import validators
import six

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

        if value is not None and not isinstance(value, list):
            raise TypeError(
                "'{name}' must be a list"
                .format(name=attribute.name), attribute, self.type_, value,
            )

        if value is not None and not all(isinstance(v, self.type_) for v in value):
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


class NotInstantiatedType(object):  # pylint: disable=no-init
    '''A class for not instantiated attributes
    Trying to access an attribute with this value will trigger
    the instantiation. A Nexus query will be performed and the attribute
    will be filled with the real value'''
    def __repr__(self):
        return '<not instantiated>'


NotInstantiated = NotInstantiatedType()


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

    def __init__(self, type_, optional=Ellipsis, default=Ellipsis):
        def instance_of(type_):
            '''instance_of'''
            return validators.instance_of((type_, NotInstantiatedType))

        def optional_of(type_):
            '''optional_of'''
            return validators.optional(instance_of(type_))

        if isinstance(type_, typing.GenericMeta):
            # the collection was explicitly specified in attr.ib
            # like typing.List[Distribution]
            list_element_type = _get_list_params(type_)[0]
            if type(list_element_type) is type(typing.Union):  # noqa
                types = _get_union_params(list_element_type)
                validator = _list_of(types, default)
            else:
                validator = _list_of(list_element_type, default)
        else:
            if optional is Ellipsis:
                if default is Ellipsis:
                    validator = instance_of(type_)
                elif default is None:
                    validator = optional_of(type_)
                else:
                    validator = None  # FIXME, what should be put there ?
            else:
                if optional is False:
                    validator = instance_of(type_)
                else:
                    validator = optional_of(type_)
        self.is_positional = default is Ellipsis

        if default is Ellipsis:  # no default value -> positional arg
            self.fn = lambda: attr.ib(type=type_, validator=validator, repr=False)
        else:
            self.fn = lambda: attr.ib(type=type_, default=default, validator=validator, repr=False)

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
    for key in kw_new.keys():
        pos_inherited.pop(key, None)
    result.update(pos_inherited)
    result.update(pos_new)
    result.update(kw_new)
    result.update(kw_inherited)
    return result


def _clean_up_dict(d):
    '''Produce new dictionary without json-ld attrs which start with @'''
    return {k: v for k, v in six.iteritems(d) if not k.startswith('@')}


def resolve_path(key):
    '''Resolve path by convention If ``key`` has words separated by double underscore they
    will be replaced with ``/`` forming deep path for the query. Single underscores
    will be replaced with ``:`` explicitly specifying namespaces(otherwise default
    ``nsg:`` namespace will be used). Also some names from well-known namespaces will be
    resolved(like name->schema:name, email->schema:email, used->prov:used).
    '''

    # args with exactly one underscore separating words, first part denotes namespace
    key = re.sub(r'([^_])_([^_])', r'\1:\2', key)

    path_list = []
    for token in key.split('__'):
        if ':' not in token:  # namespace not resolved by re.sub
            # some default processing with known namespace defaults
            if token in ['name', 'version', 'email']:
                token = 'schema:%s' % token
            elif token in ['activity', 'qualifiedGeneration', 'used', 'generated']:
                token = 'prov:%s' % token
            elif token in ['uuid', 'originalFileName']:
                token = 'nxv:%s' % token
            else:
                token = 'nsg:%s' % token  # use default namespace
        path_list.append(token)

    return path_list[0] if len(path_list) == 1 else ' / '.join(path_list)
