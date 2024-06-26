# pylint: disable=missing-docstring,no-member,import-outside-toplevel
from six.moves import builtins
from unittest.mock import patch

import responses

import entity_management.nexus as nexus
from entity_management.state import set_token, get_token, has_offline_token
from entity_management.settings import NSG
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


@responses.activate
@patch("%s.open" % builtins.__name__)
def test_download_file(_):
    responses.add(
        responses.POST,
        "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/token",
        json={"access_token": ACES_TOKEN},
    )

    # base64 encode 'myfile.jpg' in content disposition header
    responses.add(
        responses.GET,
        FILE_URL,
        headers={"Content-Disposition": 'attachment; filename="=?UTF-8?B?bXlmaWxlLmpwZw==?="'},
        json=FILE_RESPONSE,
    )

    file_path = nexus.download_file(FILE_URL, path="/tmp")

    assert file_path == "/tmp/%s" % FILE_NAME_EXT


@responses.activate
def test_download_file_with_name():
    responses.add(
        responses.POST,
        "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/token",
        json={"access_token": ACES_TOKEN},
    )

    responses.add(responses.GET, FILE_URL, json=FILE_RESPONSE)

    new_name = "abc.jpg"
    with patch("%s.open" % builtins.__name__):
        file_path = nexus.download_file(FILE_URL, path="/tmp", file_name=new_name)
        assert file_path == "/tmp/%s" % new_name


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


@responses.activate
def test_offline_token():
    responses.add(
        responses.POST,
        "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/token",
        json={"access_token": ACES_TOKEN},
    )

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
    with patch("entity_management.nexus.load_by_url") as patched:
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
    with patch("entity_management.nexus.load_by_url") as patched:
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
    with patch("entity_management.nexus.load_by_url") as patched:
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
    with patch("entity_management.nexus.load_by_url") as patched:
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
