# pylint: disable=missing-docstring,no-member
from six.moves import builtins
from mock import patch
from nose.tools import assert_equal

import responses

import entity_management.nexus as nexus
from entity_management.util import quote
from entity_management.settings import BASE_FILES, ORG, PROJ, NSG

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
    responses.add(
        responses.GET,
        '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(FILE_ID)),
        headers={'Content-Disposition': "attachment; filename*=UTF-8''myfile.jpg"},
        json=FILE_RESPONSE)

    file_path = nexus.download_file(FILE_ID, path='/tmp')

    assert_equal(file_path, '/tmp/%s' % FILE_NAME_EXT)


@responses.activate
def test_download_file_with_name():
    responses.add(
        responses.GET,
        '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(FILE_ID)),
        headers={'Content-Disposition': "attachment; filename*=UTF-8''myfile.jpg"},
        json=FILE_RESPONSE)

    new_name = 'abc.jpg'
    with patch('%s.open' % builtins.__name__):
        file_path = nexus.download_file(FILE_ID, path='/tmp', file_name=new_name)
        assert_equal(file_path, '/tmp/%s' % new_name)
