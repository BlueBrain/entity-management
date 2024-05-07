"""Type checking related utils."""

import collections.abc
import types
import typing


def get_type_root_class(data_type):
    """Get type class. First try if it's `typing` type class then fallback to regular type."""
    root_type = typing.get_origin(data_type) or data_type

    # Return types.UnionType instead of typing.Union because it works with issubclass
    if root_type is typing.Union:
        return types.UnionType

    return root_type


def is_type_sequence(data_type):
    """Return True if the data_type is a sequence."""
    return data_type is not str and issubclass(
        get_type_root_class(data_type), collections.abc.Sequence
    )


def is_data_sequence(data_raw):
    """Return True if the data_raw is a sequence."""
    return not isinstance(data_raw, str) and isinstance(data_raw, collections.abc.Sequence)


def is_type_mapping(data_type):
    """Return True if the data_type is a mapping."""
    return issubclass(get_type_root_class(data_type), collections.abc.Mapping)


def is_data_mapping(data_raw):
    """Return True if the data_raw is a mapping."""
    return isinstance(data_raw, collections.abc.Mapping)


def is_type_union(data_type):
    """Return True if the data_type is a union."""
    return get_type_root_class(data_type) in {typing.Union, types.UnionType}


def is_type_single_or_list_union(data_type):
    """Return True for unions of the form T | list[T]"""
    type_args = typing.get_args(data_type)

    if len(type_args) != 2:
        return False

    arg1, arg2 = type_args
    # check that arg2 is a list generic e.g. list[int]
    # and that arg1 has the same type as arg2's element
    arg2_origin = typing.get_origin(arg2)
    return (
        arg2_origin is not None
        and issubclass(arg2_origin, list)
        and arg1 is typing.get_args(arg2)[0]
    )
