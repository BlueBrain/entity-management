# pylint: disable=missing-docstring,no-member
from six.moves import builtins

from mock import patch
from nose.tools import eq_
import responses

from entity_management.settings import BASE_FILES, BASE_RESOURCES, ORG, PROJ
from entity_management.base import NSG, DASH
from entity_management.core import Entity
from entity_management.morphology import ReconstructedPatchedCell
from entity_management.util import quote

from test_nexus import FILE_RESPONSE, FILE_ID, FILE_NAME_EXT

CELL_NAME = 'mycell'
CELL_ID = NSG[CELL_NAME]

IMAGE_NAME = 'myimage'
IMAGE_ID = NSG[IMAGE_NAME]

CELL_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': CELL_ID,
    '@type': [
        'ReconstructedPatchedCell',
        'Entity'
    ],
    '_constrainedBy': 'nsg:dash/reconstructedpatchedcell',
    '_createdAt': '2019-04-26T15:30:21.011Z',
    '_createdBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
    '_deprecated': False,
    '_project': 'https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj',
    '_rev': 1,
    '_self': 'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/%s/%s' % (
             quote(DASH.reconstructedpatchedcell), quote(CELL_ID)),
    '_updatedAt': '2019-04-26T15:30:21.011Z',
    '_updatedBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
    'brainLocation': {
        'brainRegion': {
            '@id': 'http://uri.interlex.org/paxinos/uris/rat/labels/1017',
            'label': 'ventral posterolateral thalamic nucleus'
        }
    },
    'distribution': {
        '@type': 'DataDownload',
        'contentSize': {
            'unitCode': 'bytes',
            'value': 397841
        },
        'contentUrl': FILE_ID,
        'digest': {
            'algorithm': 'SHA-256',
            'value': '1123f4816beea40352612374a1ac5b8bf4fa515a2f98af9793c6f83d2c8080d6'
        },
        'encodingFormat': 'application/octet-stream',
        'name': 'morphology_file_name.asc'
    },
    'wasDerivedFrom': [{
        '@id': IMAGE_ID,  # link to core.Entity to test that type can be recovered.
        '@type': 'Entity'
    }],
    'mType': {
        '@id': 'http://uri.interlex.org/base/ilx_0738236',
        'label': 'VPL_TC',
        'prefLabel': 'VPL_TC'
    },
    'name': 'cell_name'
}

IMAGE_RESPOSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': IMAGE_ID,
    '@type': 'Entity',
    '_constrainedBy': 'nsg:dash/entity',
    '_createdAt': '2019-05-08T14:03:10.196Z',
    '_createdBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
    '_deprecated': False,
    '_project': 'https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj',
    '_rev': 1,
    '_self':
        'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/datashapes:entity/%s' % IMAGE_NAME,
    '_updatedAt': '2019-05-08T14:03:10.196Z',
    '_updatedBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
    'distribution': {
        '@type': 'DataDownload',
        'contentSize': {
            'unitCode': 'bytes',
            'value': 397841
        },
        'contentUrl': FILE_ID,
        'digest': {
            'algorithm': 'SHA-256',
            'value': '1123f4816beea40352612374a1ac5b8bf4fa515a2f98af9793c6f83d2c8080d6'
        },
        'encodingFormat': 'application/octet-stream',
        'name': FILE_NAME_EXT
    },
    'name': IMAGE_NAME
}


CELL_LIST_RESPONSE = {
    '@context': [
        'https://bluebrain.github.io/nexus/contexts/search.json',
        'https://bluebrain.github.io/nexus/contexts/resource.json'
    ],
    '_results': [
        {
            '@id': CELL_ID,
            '@type': [
                'https://neuroshapes.org/ReconstructedPatchedCell',
                'http://www.w3.org/ns/prov#Entity'
            ],
            '_constrainedBy': 'https://neuroshapes.org/dash/reconstructedpatchedcell',
            '_createdAt': '2019-04-26T15:29:33.141Z',
            '_createdBy': 'https://bbp.epfl.ch/nexus/v1/anonymous',
            '_deprecated': False,
            '_project': 'https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj',
            '_rev': 1,
            '_self': 'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/'
                     '%s/%s' % (quote(DASH.reconstructedpatchedcell), quote(CELL_ID)),
            '_updatedAt': '2019-04-26T15:29:33.141Z',
            '_updatedBy': 'https://bbp.epfl.ch/nexus/v1/anonymous'
        }
    ],
    '_total': 1
}


@responses.activate
def test_reconstructed_patched_cell():
    responses.add(  # mock file resource response
        responses.GET,
        '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(FILE_ID)),
        headers={'Content-Disposition': "attachment; filename*=UTF-8''%s" % FILE_NAME_EXT},
        json=FILE_RESPONSE)

    responses.add(  # mock patched cell listing response
        responses.GET,
        ReconstructedPatchedCell._base_url,
        json=CELL_LIST_RESPONSE)

    responses.add(  # mock patched cell detailed response
        responses.GET,
        '%s/%s' % (ReconstructedPatchedCell._base_url, quote(CELL_ID)),
        json=CELL_RESPONSE)

    responses.add(  # mock image response
        responses.GET,
        '%s/%s/%s/_/%s' % (BASE_RESOURCES, ORG, PROJ, quote(IMAGE_ID)),
        json=IMAGE_RESPOSE)

    cells = ReconstructedPatchedCell.list()
    cell = next(cells)
    eq_(cell.name, 'cell_name')
    eq_(type(cell.wasDerivedFrom[0]), Entity)
    with patch('%s.open' % builtins.__name__):
        eq_(cell.distribution[0].download(path='/tmp'), '/tmp/%s' % FILE_NAME_EXT)