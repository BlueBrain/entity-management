import pytest

from entity_management import util as test_module


@pytest.mark.parametrize("uri, expected_path", [
    ("/foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/%5Bfile%5D1.txt", "/foo/bar/[file]1.txt"),
    ("file:///sbo/data/project/sbo/nexus/tests/workflow/8/0/6/7/d/9/1/1/2023-08-28_11-39-36.5.zip", "/sbo/data/project/sbo/nexus/tests/workflow/8/0/6/7/d/9/1/1/2023-08-28_11-39-36.5.zip"),
])
def test_file_uri_to_path(uri, expected_path):
    res = test_module.file_uri_to_path(uri)
    assert res == expected_path
