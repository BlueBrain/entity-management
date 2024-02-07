from unittest.mock import patch

import pytest
from entity_management import exception
from entity_management import util as test_module
from entity_management.core import Entity


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


@patch("entity_management.nexus.load_by_id", return_value=None)
def test_get_entity__raises_if_not_found(patched):
    with pytest.raises(
        exception.ResourceNotFoundError, match="Resource id my-id could not be retrieved"
    ):
        test_module.get_entity("my-id", cls=Entity)


@patch("entity_management.nexus.load_by_id", return_value={})
def test_get_entity__raises_if_not_instantiated(patched):
    with pytest.raises(
        exception.EntityNotInstantiatedError, match="failed to be instantiated from id my-id"
    ):
        test_module.get_entity("my-id", cls=Entity)
