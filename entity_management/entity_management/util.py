'''Utilities'''

from attr.validators import instance_of, optional


def optional_of(type_):
    '''Composition of optional and instance_of'''
    return optional(instance_of(type_))
