# pylint: disable=missing-docstring,no-member
import tempfile

import responses
from nose.tools import assert_raises, eq_

from entity_management.core import DataDownload, WorkflowExecution
from entity_management.state import get_org, get_proj
from entity_management.settings import BASE_FILES, BASE_RESOURCES


FILE_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': 'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/_/'
           'b00896ef-db8c-4fae-90e4-ae157a306746',
    '@type': 'File',
    '_bytes': 9,
    '_constrainedBy': 'https://bluebrain.github.io/nexus/schemas/file.json',
    '_createdAt': '2019-06-27T12:58:12.717Z',
    '_createdBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous',
    '_deprecated': False,
    '_digest': {
        '_algorithm': 'SHA-256',
        '_value': '1fe638b478f8f0b2c2aab3dbfd3f05d6dfe2191cd7b4482241fe58567e37aef6'},
    '_filename': 'tmp1u6tq_ac.zip',
    '_mediaType': 'application/zip',
    '_project': 'https://bbp-nexus.epfl.ch/staging/v1/projects/myorg/myproj',
    '_rev': 1,
    '_self': 'https://bbp.epfl.ch/nexus/v1/files/myorg/test/b00896ef-db8c-4fae-90e4-ae157a306746',
    '_updatedAt': '2019-06-27T12:58:12.717Z',
    '_updatedBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous'
}

WORKFLOW_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': 'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/_/'
           '487862bf-c682-49da-aed5-151b5a85f4cb',
    '@type': 'https://neuroshapes.org/WorkflowExecution',
    '_constrainedBy': 'https://bluebrain.github.io/nexus/schemas/unconstrained.json',
    '_createdAt': '2019-06-28T09:16:10.487Z',
    '_createdBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous',
    '_deprecated': False,
    '_project': 'https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj',
    '_rev': 1,
    '_self': 'https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/_/'
             '487862bf-c682-49da-aed5-151b5a85f4cb',
    '_updatedAt': '2019-06-28T09:16:10.487Z',
    '_updatedBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous'
}


@responses.activate
def test_workflow_execution():
    responses.add(
        responses.POST,
        '%s/%s/%s' % (BASE_FILES, get_org(), get_proj()),
        json=FILE_RESPONSE)

    responses.add(
        responses.POST,
        '%s/%s/%s/_' % (BASE_RESOURCES, get_org(), get_proj()),
        json=WORKFLOW_RESPONSE)

    with tempfile.NamedTemporaryFile(suffix='.zip') as temp:
        temp.write(b'Some data')  # 9 bytes of data
        temp.flush()
        distribution = DataDownload.from_file(file_path=temp.name, content_type='application/zip')
        workflow = WorkflowExecution(name='module_name.TaskName',
                                     module='module_name',
                                     task='TaskName',
                                     version='0.0.15',
                                     distribution=distribution)

    eq_(workflow.as_json_ld()['distribution']['@type'], 'DataDownload')
    eq_(workflow.distribution.contentSize['value'], 9)
    eq_(workflow.distribution.encodingFormat, 'application/zip')


def test_data_download_no_url_and_content_url_provided():
    assert_raises(Exception, lambda: DataDownload())  # pylint: disable=unnecessary-lambda
