import pytest

from entity_management import util as test_module


@pytest.mark.parametrize("uri, expected_path", [
    ("/foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/file.txt", "/foo/bar/file.txt"),
    ("file:///foo/bar/%5Bfile%5D1.txt", "/foo/bar/[file]1.txt"),
])
def test_file_uri_to_path(uri, expected_path):
    res = test_module.file_uri_to_path(uri)
    assert res == expected_path
