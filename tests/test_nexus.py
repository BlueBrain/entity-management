# pylint: disable=missing-docstring,no-member
from six.moves import builtins
from mock import patch

import responses

import entity_management.nexus as nexus
from entity_management.state import (get_base_files, get_org, get_proj, set_token, get_token,
                                     has_offline_token)
from entity_management.util import quote
from entity_management.settings import NSG

FILE_NAME = 'myfile'
FILE_NAME_EXT = '%s.jpg' % FILE_NAME
FILE_ID = NSG[FILE_NAME_EXT]

FILE_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': FILE_ID,
    '@type': 'File',
    '_bytes': 2670,
    '_digest': {
        '_algorithm': 'SHA-256',
        '_value': '25fc54fba0beec17a598b5a68420ded1595b2f76f0a0b7c6077792ece828bc2e'
    },
    '_filename': 'myfile.jpg',
    '_mediaType': 'image/png',
    '_self': 'https://bbp.epfl.ch/nexus/v1/files/myorg/myproj/nxv:myfile',
    '_constrainedBy': 'https://bluebrain.github.io/nexus/schemas/file.json',
    '_project': 'https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj',
    '_rev': 4,
    '_deprecated': True,
    '_createdAt': '2019-01-28T12:15:33.238Z',
    '_createdBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
    '_updatedAt': '2019-12-28T12:15:33.238Z',
    '_updatedBy': 'https://bbp.epfl.ch/nexus/v1/anonymous'
}


@responses.activate
@patch('%s.open' % builtins.__name__)
def test_download_file(_):
    # base64 encode 'myfile.jpg' in content disposition header
    responses.add(
        responses.GET,
        '%s/%s/%s/%s' % (get_base_files(), get_org(), get_proj(), quote(FILE_ID)),
        headers={'Content-Disposition': 'attachment; filename="=?UTF-8?B?bXlmaWxlLmpwZw==?="'},
        json=FILE_RESPONSE)

    file_path = nexus.download_file(FILE_ID, path='/tmp')

    assert file_path == '/tmp/%s' % FILE_NAME_EXT


@responses.activate
def test_download_file_with_name():
    responses.add(
        responses.GET,
        '%s/%s/%s/%s' % (get_base_files(), get_org(), get_proj(), quote(FILE_ID)),
        json=FILE_RESPONSE)

    new_name = 'abc.jpg'
    with patch('%s.open' % builtins.__name__):
        file_path = nexus.download_file(FILE_ID, path='/tmp', file_name=new_name)
        assert file_path == '/tmp/%s' % new_name


def test_token():
    token = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l'
             'IiwidHlwIjoiQmVhcmVyIiwiaWF0IjoxNTE2MjM5MDIyfQ.8xXouRWxnH6gHxUZSAAxplzmUb5OEWy61K6SF0'
             '5Hgi0')
    set_token(token)
    assert token == get_token()
    from entity_management.state import ACCESS_TOKEN
    assert token == ACCESS_TOKEN


@responses.activate
def test_offline_token():
    token = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l'
             'IiwidHlwIjoiQmVhcmVyIiwiaWF0IjoxNTE2MjM5MDIyfQ.8xXouRWxnH6gHxUZSAAxplzmUb5OEWy61K6SF0'
             '5Hgi0')
    responses.add(
        responses.POST,
        'https://bbpteam.epfl.ch/auth/realms/BBP/protocol/openid-connect/token',
        json={'access_token': token})

    offline = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG'
               '9lIiwidHlwIjoiT2ZmbGluZSIsImlhdCI6MTUxNjIzOTAyMn0.ulLat2ZoDCKcpKtvrTWb1hCRvvHfShU9s'
               '5eZIALS2xo')
    set_token(offline)
    assert has_offline_token()
    assert token == get_token()
    from entity_management.state import ACCESS_TOKEN, OFFLINE_TOKEN
    assert token == ACCESS_TOKEN
    assert offline == OFFLINE_TOKEN
