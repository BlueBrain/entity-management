# pylint: disable=missing-docstring,no-member
import json
import os
import tempfile
from datetime import datetime
from itertools import repeat
from typing import List

import attr
import responses
from mock import patch, MagicMock
from nose.tools import assert_raises, ok_, eq_

from entity_management.state import set_proj, get_base_resources, set_base
from entity_management.base import (Identifiable, OntologyTerm,
                                    _deserialize_list, _serialize_obj, Unconstrained)
from entity_management.core import DataDownload, DistributionMixin
from entity_management.state import get_org, get_proj
from entity_management.util import make_context_for_lists


DISTRIBUTION_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': 'nxv:myfile',
    '@type': 'File',
    '_bytes': 2670,
    '_digest': {
        '_algorithm': 'SHA-256',
        '_value': '25fc54fba0beec17a598b5a68420ded1595b2f76f0a0b7c6077792ece828bc2e'
    },
    '_filename': 'myfile2.png',
    '_mediaType': 'image/png',
    '_self': 'https://bbp-nexus.epfl.ch/staging/v1/files/myorg/myproj/nxv:myfile',
    '_constrainedBy': 'https://bluebrain.github.io/nexus/schemas/file.json',
    '_project': 'https://bbp-nexus.epfl.ch/staging/v1/projects/myorg/myproj',
    '_rev': 1,
    '_deprecated': False,
    '_createdAt': '2019-01-28T12:15:33.238Z',
    '_createdBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous',
    '_updatedAt': '2019-12-28T12:15:33.238Z',
    '_updatedBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous'
}

UUID = '03a8d151-0a1a-4735-8b81-2696422e04b8'

UNCONSTRAINED_RESPONSE = {
    '@context': 'https://bluebrain.github.io/nexus/contexts/resource.json',
    '@id': 'https://bbp-nexus.epfl.ch/staging/v1/resources/myorg/myproj/_/%s' % UUID,
    '_self': 'https://bbp-nexus.epfl.ch/staging/v1/resources/myorg/myproj/_/%s' % UUID,
    '_constrainedBy': 'https://bluebrain.github.io/nexus/schemas/unconstrained.json',
    '_project': 'https://bbp-nexus.epfl.ch/staging/v1/projects/myorg/myproj',
    '_rev': 1,
    '_deprecated': False,
    '_createdAt': '2019-01-28T12:15:33.238Z',
    '_createdBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous',
    '_updatedAt': '2019-12-28T12:15:33.238Z',
    '_updatedBy': 'https://bbp-nexus.epfl.ch/staging/v1/anonymous'
}


# def test_types():
#     class Dummy(Identifiable):
#         '''A dummy class'''
#     dummy = Dummy()
#     with patch('entity_management.base.nexus.create', return_value={JSLD_ID: 'id', JSLD_REV: 1}):
#         dummy = dummy.publish()
#         assert_equal(dummy.types, ['prov:Entity', 'nsg:Dummy'])
#
#     dummy.meta.types = 'value changed'
#     assert_equal(dummy.evolve().types, 'value changed')
#
# def test_from_url():
#     assert_raises(Exception, from_url, 'https://no-python-class-at-this-url')
#
# def test_serialize():
#     obj = Identifiable()
#     obj.meta.types = ['changed types']
#     assert_equal(_serialize_obj(obj),
#                  {'@id': None, '@type': ['changed types']})
#
#     id_ = '/entity/v1.0.0'
#     obj = Identifiable(id=id_)
#     obj.meta.types = ['nsg:Entity']
#     obj.meta.rev = 1
#     assert_equal(_serialize_obj(obj, True),
#                  {'@id': id_, '@type': []})
#
#     assert_equal(_serialize_obj(datetime(2018, 12, 23)),
#                  '2018-12-23T00:00:00')
#
#     assert_equal(_serialize_obj(OntologyTerm(url='A', label='B')),
#                  {'@id': 'A', 'label': 'B'})
#
#     @attr.s
#     class Dummy(object):
#         a = attr.ib(default=42)
#         b = attr.ib(default=None)
#
#     dummy = Dummy(a=33, b=Dummy(a=12))
#     assert_equal(_serialize_obj(dummy),
#                  {'a': 33, 'b': {'a': 12}})
#
#     dummy = Dummy(a={1: 2}, b=[OntologyTerm(url='A', label='B')])
#     assert_equal(_serialize_obj(dummy),
#                  {'a': {1: 2}, 'b': [{'@id': 'A', 'label': 'B'}]})
#
#     assert_equal(_serialize_obj(42), 42)


def test_deserialize_list():
    eq_(_deserialize_list(dict, [{'a': 'b'}], token=None), {'a': 'b'})

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)
    eq_(_deserialize_list(List[Dummy], [{'a': 1, 'b': 2}], token=None), [Dummy(a=1, b=2)])


@responses.activate
def test_unconstraint():
    responses.add(
        responses.POST,
        '%s/%s/%s/_' % (get_base_resources(), get_org(), get_proj()),
        json=UNCONSTRAINED_RESPONSE)
    obj = Unconstrained(json=dict(key1='value1', key2='value2'))
    eq_(obj.get_base_url(), '%s/%s/%s/_' % (get_base_resources(), get_org(), get_proj()))
    obj = obj.publish()
    eq_(obj._constrainedBy, 'https://bluebrain.github.io/nexus/schemas/unconstrained.json')


def test_project_change():
    obj = Unconstrained(json=dict(key1='value1', key2='value2'))
    eq_(obj.get_base_url(), '%s/%s/%s/_' % (get_base_resources(), get_org(), get_proj()))
    set_proj('test')
    eq_(obj.get_base_url(), '%s/%s/%s/_' % (get_base_resources(), get_org(), 'test'))


def test_unconstraint_serialization():
    obj = Unconstrained(json=dict(key1=['value1', 'value2'], key2='value3'))
    context = make_context_for_lists(obj.json)
    ok_('key1' in context)
    ok_('key2' not in context)


def test_env_change():
    eq_(get_base_resources(), 'https://bbp.epfl.ch/nexus/v1/resources')
    set_base('https://dev.nexus.ocp.bbp.epfl.ch/v1')
    eq_(get_base_resources(), 'https://dev.nexus.ocp.bbp.epfl.ch/v1/resources')


# @responses.activate
# def test_Identifiable_find_by():
#     class Dummy(Identifiable):
#         # if not set, query url will depend on env var NEXUS_ORG
#         _url_org = 'dummy_org'
#         _url_version = 'v0.1.0'
#
#     with patch('entity_management.base.nexus.find_by', return_value=None):
#         assert_equal(Dummy.find_by(), None)
#
#
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org/simulation/dummy/v0.1.0',
#                   status=303,
#                   headers={'Location': 'https://query-location-url-1?from=0&size=10'})
#     assert_equal(Dummy.find_by(dummy=OntologyTerm(url='A', label='B')).url,
#                  'https://query-location-url-1?from=0&size=10')
#     assert_equal(Dummy.find_by(dummy=('eq', 'A')).url,
#                  'https://query-location-url-1?from=0&size=10')
#     assert_equal(Dummy.find_by(dummy=Identifiable(id='an-awesome-id')).url,
#                  'https://query-location-url-1?from=0&size=10')
#
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org/simulation/dummy',
#                   status=303,
#                   headers={'Location': 'https://query-location-url-2?from=0&size=10'})
#     assert_equal(Dummy.find_by(all_versions=True).url,
#                  'https://query-location-url-2?from=0&size=10')
#
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org',
#                   status=303,
#                   headers={'Location': 'https://query-location-url-3?from=0&size=10'})
#     assert_equal(Dummy.find_by(all_domains=True).url, 'https://query-location-url-3?from=0&size=10')
#
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries',
#                   status=303,
#                   headers={'Location': 'https://query-location-url-4?from=0&size=10'})
#     assert_equal(Dummy.find_by(all_organizations=True).url,
#                  'https://query-location-url-4?from=0&size=10')
#
#
# def test_find_unique():
#     class MockResult:
#         id = 12
#
#     single_result = MockResult()
#     with patch.object(Identifiable, 'find_by', return_value=iter([single_result])):
#         ok_(Identifiable.find_unique(name="whatever") is single_result)
#
#     too_many_result = repeat(MockResult(), 4)
#     with patch.object(Identifiable, 'find_by', return_value=too_many_result):
#         assert_raises(Exception, Identifiable.find_unique, name="whatever")
#
#     no_result = iter(list())
#     with patch.object(Identifiable, 'find_by', return_value=no_result):
#         ok_(not Identifiable.find_unique(name="whatever"))
#
#         assert_raises(Exception, Identifiable.find_unique, name="whatever", throw=True)
#         assert_equal(Identifiable.find_unique(name="whatever", on_no_result=lambda: 7), 7)
#
#     mock_return_on_first_try = MagicMock(return_value=iter([1]))
#     with patch.object(Identifiable, 'find_by', mock_return_on_first_try):
#         assert_equal(Identifiable.find_unique(name="whatever",
#                                               on_no_result=lambda: 7,
#                                               poll_until_exists=True),
#                      1)
#         assert_equal(mock_return_on_first_try.call_count, 1)
#
#
#     mock_return_on_second_try = MagicMock(side_effect=[iter([]), iter([2])])
#     with patch.object(Identifiable, 'find_by', mock_return_on_second_try):
#         assert_equal(Identifiable.find_unique(name="whatever",
#                                               on_no_result=lambda: 7,
#                                               poll_until_exists=True),
#                      7)
#         assert_equal(mock_return_on_second_try.call_count, 2)
#
#     mock_never_finds = MagicMock(return_value=iter([]))
#     with patch.object(Identifiable, 'find_by', mock_never_finds):
#         with patch('entity_management.base.sleep'):
#             assert_raises(Exception,
#                           Identifiable.find_unique,
#                           name="whatever",
#                           on_no_result=lambda: 7,
#                           poll_until_exists=True)
#
#
#
#
#
#
# @responses.activate
# def test_get_attachment():
#     attachment = DistributionMixin(distribution=[
#         Distribution(downloadURL='crap')
#     ]).get_attachment()
#
#     assert_equal(attachment,
#                  None)
#
#     dists = [Distribution(downloadURL='crap'),
#              Distribution(downloadURL='https://bla/attachment',
#                           originalFileName='original.json'),
#              Distribution(downloadURL='file:///gpfs/some-stuff',
#                           storageType='gpfs')]
#
#     assert_equal(DistributionMixin(distribution=dists).get_attachment(),
#                  dists[1])
#
#     assert_equal(DistributionMixin(distribution=dists).get_gpfs_path(),
#                  '/gpfs/some-stuff')
#
#     assert_equal(DistributionMixin(distribution=[]).get_gpfs_path(),
#                  None)
#
#     responses.add(responses.GET, 'https://bla/attachment', json={'Bob': 'Marley'})
#     DistributionMixin(distribution=dists).download(tempfile.gettempdir())
#     with open(os.path.join(tempfile.gettempdir(), 'original.json')) as f:
#         assert_equal(json.load(f), {'Bob': 'Marley'})
