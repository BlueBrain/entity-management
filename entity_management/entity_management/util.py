'''Utilities'''

import attr
from attr import validators


def optional_of(type_):
    '''Composition of optional and instance_of'''
    return validators.optional(validators.instance_of(type_))


class AttrOf(object):
    '''Create an object with self.is_positional(Bool) and self.fn(Callable) that will be used
    to create an attr.ib by invoking Callable. is_positional signifies that attribute will have
    no default value and will appear in class init method as positional argument else it will
    be kwarg

    This is needed so that @attributes decorator can create the attr.ib's in order
    because they have a counter inside that is used to order them
    '''

    def __init__(self, type_, optional=Ellipsis, default=Ellipsis):
        validator = None
        if optional is Ellipsis:
            if default is Ellipsis:
                validator = validators.instance_of(type_)
            elif default is None:
                validator = optional_of(type_)
        else:
            if optional is False:
                validator = validators.instance_of(type_)
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


def attributes(attr_dict):
    '''decorator to simplify creation of classes that have args and kwargs'''
    assert attr_dict is not None # should be called with some dictionary of attributes

    def wrap(cls):
        '''wraps'''
        these = _merge(
            {k: v() for k, v in attr_dict.items() if v.is_positional},
            _attrs_pos(cls),
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
