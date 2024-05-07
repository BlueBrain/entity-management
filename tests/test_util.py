from unittest.mock import patch
import attr

import pytest
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
        (list[int], NA, [1, 2], True),
        (list[int], NA, [1.0, 2.0], False),
        (list[int], NA, [1, 2.0], False),
        (int | float, NA, 2, True),
        (int | float, NA, 2.0, True),
        (int | float, 2, None, True),
        (int | float, 2.0, None, True),
        (int | float, NA, {}, False),
        (int | float, {}, None, False),
        (int | list[int], NA, 2, True),
        (int | list[int], NA, 2.0, False),
        (int | list[int], NA, [1, 2], True),
        (int | list[int], NA, [1, 2.0], False),
        (BN1 | list[BN1], NA, OBN1, True),
        (BN1 | list[BN1], NA, [OBN1, OBN1], True),
        (MaybeList[BN1], NA, OBN1, True),
        (MaybeList[BN1], NA, [OBN1, OBN1], True),
    ],
)
def test_validators(type_, default, value, should_validation_pass):

    @attributes({"test": AttrOf(type_, default=default)})
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
