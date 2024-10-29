# Automatically generated, DO NOT EDIT.
# pylint: disable=missing-docstring,no-member,import-outside-toplevel
import json
from unittest.mock import patch

from pytest_httpx import IteratorStream

import entity_management.nexus as nexus
from entity_management.settings import NSG
from entity_management.state import get_token, has_offline_token, set_token
from entity_management.util import quote

FILE_NAME = "myfile"
FILE_NAME_EXT = "%s.jpg" % FILE_NAME
FILE_ID = NSG[FILE_NAME_EXT]
FILE_URL = "https://bbp.epfl.ch/nexus/v1/files/myorg/myproj/nxv:myfile"

FILE_RESPONSE = {
    "@context": "https://bluebrain.github.io/nexus/contexts/resource.json",
    "@id": FILE_ID,
    "@type": "File",
    "_bytes": 2670,
    "_digest": {
        "_algorithm": "SHA-256",
        "_value": "25fc54fba0beec17a598b5a68420ded1595b2f76f0a0b7c6077792ece828bc2e",
    },
    "_filename": "myfile.jpg",
    "_mediaType": "image/png",
    "_self": FILE_URL,
    "_constrainedBy": "https://bluebrain.github.io/nexus/schemas/file.json",
    "_project": "https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj",
    "_rev": 4,
    "_deprecated": True,
    "_createdAt": "2019-01-28T12:15:33.238Z",
    "_createdBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
    "_updatedAt": "2019-12-28T12:15:33.238Z",
    "_updatedBy": "https://bbp.epfl.ch/nexus/v1/anonymous",
}

ACES_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l"
    "IiwidHlwIjoiQmVhcmVyIiwiaWF0IjoxNTE2MjM5MDIyfQ.8xXouRWxnH6gHxUZSAAxplzmUb5OEWy61K6SF0"
    "5Hgi0"
)


def test_download_file(tmp_path, httpx_mock):
    # base64 encode 'myfile.jpg' in content disposition header
    stream = json.dumps(FILE_RESPONSE).encode("utf-8")
    httpx_mock.add_response(
        stream=IteratorStream([stream[: len(stream) // 2], stream[len(stream) // 2 :]]),
        method="GET",
        url=f"{FILE_URL}?tag=&rev=",
        headers={"Content-Disposition": 'attachment; filename="=?UTF-8?B?bXlmaWxlLmpwZw==?="'},
    )

    file_path = nexus.download_file(FILE_URL, path=str(tmp_path))

    expected_path = tmp_path / FILE_NAME_EXT
    assert file_path == str(expected_path)
    assert expected_path.is_file()
    assert expected_path.read_bytes() == stream


def test_download_file_with_name(tmp_path, httpx_mock):
    stream = json.dumps(FILE_RESPONSE).encode("utf-8")
    httpx_mock.add_response(
        stream=IteratorStream([stream[: len(stream) // 2], stream[len(stream) // 2 :]]),
        method="GET",
        url=f"{FILE_URL}?tag=&rev=",
    )

    new_name = "abc.jpg"
    file_path = nexus.download_file(FILE_URL, path=str(tmp_path), file_name=new_name)

    expected_path = tmp_path / new_name
    assert file_path == str(expected_path)
    assert expected_path.is_file()
    assert expected_path.read_bytes() == stream


def test_token():
    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l"
        "IiwidHlwIjoiQmVhcmVyIiwiaWF0IjoxNTE2MjM5MDIyfQ.8xXouRWxnH6gHxUZSAAxplzmUb5OEWy61K6SF0"
        "5Hgi0"
    )
    set_token(token)
    assert token == get_token()
    from entity_management.state import ACCESS_TOKEN

    assert token == ACCESS_TOKEN


def test_offline_token():
    offline = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG"
        "9lIiwidHlwIjoiT2ZmbGluZSIsImlhdCI6MTUxNjIzOTAyMn0.ulLat2ZoDCKcpKtvrTWb1hCRvvHfShU9s"
        "5eZIALS2xo"
    )
    set_token(offline)
    assert has_offline_token()
    assert ACES_TOKEN == get_token()
    from entity_management.state import ACCESS_TOKEN, OFFLINE_TOKEN

    assert ACES_TOKEN == ACCESS_TOKEN
    assert offline == OFFLINE_TOKEN


def test_load_by_id():
    resource_id = "https://bbp.epfl.ch/neurosciencegraph/data/1"
    with patch(f"{nexus.__name__}.load_by_url") as patched:
        nexus.load_by_id(
            resource_id, base="my-base", org="my-org", proj="my-proj", cross_bucket=False
        )
        patched.assert_called_once_with(
            url=f"my-base/resources/my-org/my-proj/_/{quote(resource_id)}",
            params={},
            stream=False,
            token=None,
        )


def test_load_by_id__cross_bucket():
    resource_id = "https://bbp.epfl.ch/neurosciencegraph/data/1"
    with patch(f"{nexus.__name__}.load_by_url") as patched:
        nexus.load_by_id(
            resource_id, base="my-base", org="my-org", proj="my-proj", cross_bucket=True
        )
        patched.assert_called_once_with(
            url=f"my-base/resolvers/my-org/my-proj/_/{quote(resource_id)}",
            params={},
            stream=False,
            token=None,
        )


def test_load_by_id__with_revision():
    resource_id = "https://bbp.epfl.ch/neurosciencegraph/data/1"
    resource_id_with_revision = f"{resource_id}?rev=5"
    with patch(f"{nexus.__name__}.load_by_url") as patched:
        nexus.load_by_id(
            resource_id_with_revision,
            base="my-base",
            org="my-org",
            proj="my-proj",
            cross_bucket=True,
        )
        patched.assert_called_once_with(
            url=f"my-base/resolvers/my-org/my-proj/_/{quote(resource_id)}",
            params={"rev": ["5"]},
            stream=False,
            token=None,
        )


def test_load_by_id__with_tag():
    resource_id = "https://bbp.epfl.ch/neurosciencegraph/data/1"
    resource_id_with_revision = f"{resource_id}?tag=v1.1"
    with patch(f"{nexus.__name__}.load_by_url") as patched:
        nexus.load_by_id(
            resource_id_with_revision,
            base="my-base",
            org="my-org",
            proj="my-proj",
            cross_bucket=True,
        )
        patched.assert_called_once_with(
            url=f"my-base/resolvers/my-org/my-proj/_/{quote(resource_id)}",
            params={"tag": ["v1.1"]},
            stream=False,
            token=None,
        )


def test_es_query(httpx_mock):
    json_response = {
        "hits": {
            "hits": [
                {
                    "_id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/488e70c6-7163-414b-9e91-cae58bad9545",
                    "_index": "nexus_ac626f52-a548-439a-9b4d-913304323ffe_1",
                    "_score": 10.913751,
                },
            ],
            "max_score": 10.913751,
            "total": {"relation": "eq", "value": 1},
        },
        "timed_out": False,
        "took": 1,
        "_shards": {"failed": 0, "skipped": 0, "successful": 1, "total": 1},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://foo/views/bar/zee/documents/_search",
        json=json_response,
        headers={"content-type": "application/json"},
    )

    query = {"query": {"term": {"@type": "Foo"}}}

    res = nexus.es_query(query, base="https://foo", org="bar", proj="zee")

    assert res == json_response
