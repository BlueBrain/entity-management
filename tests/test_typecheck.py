import pytest
import types
import typing

from entity_management import typecheck as test_module


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int, int),
        (list[int], list),
        (int | float, types.UnionType),
    ],
)
def test_type_root_class(type_, expected):
    res = test_module.get_type_root_class(type_)
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int, False),
        (str, False),
        (list, True),
        (tuple, True),
        (list[int], True),
        (tuple[int], True),
        (dict, False),
        (dict[int, float], False),
        (int | float, False),
        (typing.Union[int, float], False),
    ],
)
def test_is_type_sequence(type_, expected):
    res = test_module.is_type_sequence(type_)
    assert res is expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ([], True),
        ([1, 2], True),
        ((1, 2), True),
        ({}, False),
        ({1: 2, 3: 4}, False),
        ("foo", False),
    ],
)
def test_is_data_sequence(data, expected):
    res = test_module.is_data_sequence(data)
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (dict, True),
        (dict[int, float], True),
        (int, False),
        (str, False),
        (list, False),
        (list[int], False),
        (tuple, False),
        (tuple[int, float], False),
        (int | float, False),
        (dict | list, False),
        (typing.Union[int, float], False),
    ],
)
def test_is_type_mapping(type_, expected):
    res = test_module.is_type_mapping(type_)
    assert res is expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ([], False),
        ([1, 2], False),
        ((1, 2), False),
        ({}, True),
        ({1: 2, 3: 4}, True),
        ("foo", False),
    ],
)
def test_is_data_mapping(data, expected):
    res = test_module.is_data_mapping(data)
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int | float, True),
        (typing.Union[int, float], True),
        (int, False),
        (list, False),
        (list[int], False),
        (list[int] | list[float], True),
    ],
)
def test_is_type_union(type_, expected):
    res = test_module.is_type_union(type_)
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int | float, False),
        (typing.Union[int, float], False),
        (int | list[int], True),
        (typing.Union[int, list[int]], True),
        (list[int] | int, False),
        (int | list[float], False),
        (list[float] | int, False),
        (dict | list[dict], True),
        (list[dict] | dict, False),
        (dict | list, False),
    ],
)
def test_is_type_single_or_list_union(type_, expected):
    res = test_module.is_type_single_or_list_union(type_)
    assert res is expected
