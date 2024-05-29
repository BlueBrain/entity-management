import sys
import pytest
import types
import typing
from typing import List, Union, Tuple, Dict

from entity_management import typecheck as test_module


def _skip(*args, min_version):
    return pytest.param(
        *args,
        marks=pytest.mark.skipif(
            sys.version_info < min_version,
            reason=f"Test requres {min_version} or higher.",
        ),
    )


def _eval(string_or_type):
    if isinstance(string_or_type, str):
        return eval(string_or_type)
    return string_or_type


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int, int),
        (list, list),
        (List[int], list),
        _skip("list[int]", list, min_version=(3, 9)),
        (tuple, tuple),
        (Tuple[float], tuple),
        _skip("tuple[int]", tuple, min_version=(3, 9)),
        (Dict[float, int], dict),
        _skip("dict[float, int]", dict, min_version=(3, 9)),
        (Union[int, float], Union),
        _skip("int | float", Union, min_version=(3, 10)),
    ],
)
def test_get_type_root_class(type_, expected):
    res = test_module.get_type_root_class(_eval(type_))
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (List[int], (int,)),
        _skip("list[int]", (int,), min_version=(3, 9)),
        (List[List], (list,)),
        _skip("list[list]", (list,), min_version=(3, 9)),
        _skip("list[List]", (list,), min_version=(3, 9)),
        (Dict[int, float], (int, float)),
        (Dict[list, dict], (list, dict)),
        (Dict[List, dict], (list, dict)),
        _skip("dict[int, float]", (int, float), min_version=(3, 9)),
        _skip("dict[List, Dict]", (list, dict), min_version=(3, 9)),
        (Union[int, float], (int, float)),
        _skip("int | float", (int, float), min_version=(3, 10)),
        (Union[List, Dict], (list, dict)),
        _skip("List | Dict", (list, dict), min_version=(3, 10)),
        (Union[list, dict], (list, dict)),
        _skip("list | dict", (list, dict), min_version=(3, 10)),
    ],
)
def test_get_type_root_args(type_, expected):
    res = test_module.get_type_root_args(_eval(type_))
    assert res == expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        (int, False),
        (str, False),
        (list, True),
        (tuple, True),
        (List[int], True),
        _skip("list[int]", True, min_version=(3, 9)),
        (Tuple[int], True),
        _skip("tuple[int]", True, min_version=(3, 9)),
        (dict, False),
        (Dict[int, float], False),
        _skip("dict[int, float]", False, min_version=(3, 9)),
        _skip("int | float", False, min_version=(3, 10)),
        (Union[int, float], False),
    ],
)
def test_is_type_sequence(type_, expected):
    res = test_module.is_type_sequence(_eval(type_))
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
        (Dict[int, float], True),
        _skip("dict[int, float]", True, min_version=(3, 9)),
        (int, False),
        (str, False),
        (list, False),
        _skip("list[int]", False, min_version=(3, 9)),
        (tuple, False),
        (Tuple[int, float], False),
        _skip("tuple[int, float]", False, min_version=(3, 9)),
        (Union[int, float], False),
        _skip("int | float", False, min_version=(3, 10)),
        (Union[dict, list], False),
        _skip("dict | list", False, min_version=(3, 10)),
    ],
)
def test_is_type_mapping(type_, expected):
    res = test_module.is_type_mapping(_eval(type_))
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
        _skip("int | float", True, min_version=(3, 10)),
        (Union[int, float], True),
        (int, False),
        (list, False),
        (List[int], False),
        _skip("list[int]", False, min_version=(3, 9)),
        (Union[List[int], List[float]], True),
        _skip("list[int] | list[float]", True, min_version=(3, 10)),
    ],
)
def test_is_type_union(type_, expected):
    res = test_module.is_type_union(_eval(type_))
    assert res is expected


@pytest.mark.parametrize(
    "type_,expected",
    [
        _skip("int | float", False, min_version=(3, 10)),
        (Union[int, float], False),
        (Union[int, List[int]], True),
        _skip("int | list[int]", True, min_version=(3, 10)),
        _skip("Union[int, list[int]]", True, min_version=(3, 9)),
        _skip("list[int] | int", False, min_version=(3, 10)),
        _skip("int | list[float]", False, min_version=(3, 10)),
        _skip("list[float] | int", False, min_version=(3, 10)),
        _skip("dict | list[dict]", True, min_version=(3, 10)),
        (Union[List[Dict], Dict], False),
        (Union[List[dict], dict], False),
        _skip("list[dict] | dict", False, min_version=(3, 10)),
        (Union[dict, list], False),
        _skip("dict | list", False, min_version=(3, 10)),
    ],
)
def test_is_type_single_or_list_union(type_, expected):
    res = test_module.is_type_single_or_list_union(_eval(type_))
    assert res is expected
