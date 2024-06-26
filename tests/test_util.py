from unittest.mock import patch
import attr

import sys
import pytest
from typing import Union, List
from entity_management import exception
from entity_management import util as test_module
from entity_management.core import Entity, attributes
from entity_management.util import AttrOf
from entity_management.base import BlankNode
from entity_management.typing import MaybeList


NA = attr.NOTHING


@attributes({"a": AttrOf(int)})
class BN1(BlankNode):
    pass


@attributes({"a": AttrOf(int)})
class BN2(BlankNode):
    pass


@attributes({"a": AttrOf(int)})
class BN3(BlankNode):
    pass


OBN1 = BN1(a=1)
OBN2 = BN2(a=2)
OBN3 = BN3(a=3)


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
    "type_,default,value, should_validation_pass",
    [
        (int, NA, 2, True),
        (int, NA, None, False),
        (int, 2, None, True),
        (int, NA, 2.0, False),
        (BN1, NA, OBN1, True),
        (BN1, OBN1, None, True),
        (BN1, NA, OBN2, False),
        (List[int], NA, [1, 2], True),
        _skip("list[int]", NA, [1, 2], True, min_version=(3, 9)),
        _skip("list[int]", NA, [1.0, 2.0], False, min_version=(3, 9)),
        (List[int], NA, [1.0, 2.0], False),
        _skip("list[int]", NA, [1, 2.0], False, min_version=(3, 9)),
        (List[int], NA, [1, 2.0], False),
        _skip("int | float", NA, 2, True, min_version=(3, 10)),
        (Union[int, float], NA, 2, True),
        _skip("int | float", NA, 2, True, min_version=(3, 10)),
        _skip("int | float", NA, 2.0, True, min_version=(3, 10)),
        _skip("int | float", 2, None, True, min_version=(3, 10)),
        _skip("int | float", 2.0, None, True, min_version=(3, 10)),
        _skip("int | float", NA, {}, False, min_version=(3, 10)),
        _skip("int | float", {}, None, False, min_version=(3, 10)),
        _skip("int | list[int]", NA, 2, True, min_version=(3, 10)),
        _skip("int | list[int]", NA, 2.0, False, min_version=(3, 10)),
        _skip("int | list[int]", NA, [1, 2], True, min_version=(3, 10)),
        _skip("int | list[int]", NA, [1, 2.0], False, min_version=(3, 10)),
        _skip("BN1 | list[BN1]", NA, OBN1, True, min_version=(3, 10)),
        _skip("BN1 | list[BN1]", NA, [OBN1, OBN1], True, min_version=(3, 10)),
        (MaybeList[BN1], NA, OBN1, True),
        (MaybeList[BN1], NA, [OBN1, OBN1], True),
    ],
)
def test_validators(type_, default, value, should_validation_pass):

    @attributes({"test": AttrOf(_eval(type_), default=default)})
    class A(BlankNode):
        pass

    if should_validation_pass:
        if value is None:
            A()
        else:
            A(test=value)
    else:
        with pytest.raises(TypeError):
            if value is None:
                A()
            else:
                A(test=value)


@pytest.mark.parametrize(
    "uri, expected_path",
    [
        ("/foo/bar/file.txt", "/foo/bar/file.txt"),
        ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
        ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
        ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
        ("file:///foo/bar/%5Bfile%5D1.txt", "/foo/bar/[file]1.txt"),
        (
            "file:///sbo/data/project/sbo/nexus/tests/workflow/8/0/6/7/d/9/1/1/2023-08-28_11-39-36.5.zip",
            "/sbo/data/project/sbo/nexus/tests/workflow/8/0/6/7/d/9/1/1/2023-08-28_11-39-36.5.zip",
        ),
    ],
)
def test_unquote_uri_path(uri, expected_path):
    res = test_module.unquote_uri_path(uri)
    assert res == expected_path


@attributes(
    {
        "name": AttrOf(str),
    }
)
class MyEntity(Entity):
    pass


@patch("entity_management.nexus.load_by_id", return_value=None)
def test_get_entity__raises_if_not_found(patched):
    with pytest.raises(
        exception.ResourceNotFoundError, match="Resource id my-id could not be retrieved"
    ):
        test_module.get_entity("my-id", cls=MyEntity)


@patch("entity_management.nexus.load_by_id", return_value={})
def test_get_entity__raises_if_not_instantiated(patched):
    with pytest.raises(
        exception.EntityNotInstantiatedError, match="failed to be instantiated from id my-id"
    ):
        test_module.get_entity("my-id", cls=MyEntity)


def test_url_params():

    url = "https://foo/bar?rev=10"
    res_url, res_params = test_module.split_url_params(url)
    assert res_url == "https://foo/bar"
    assert res_params == {"rev": ["10"]}

    url = "https://foo/bar?tag=v1.1"
    res_url, res_params = test_module.split_url_params(url)
    assert res_url == "https://foo/bar"
    assert res_params == {"tag": ["v1.1"]}
