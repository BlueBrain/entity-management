from datetime import datetime
from itertools import repeat
from typing import List
import attr
import responses
from mock import patch
from nose.tools import assert_equal, assert_raises, ok_

from entity_management.base import (Identifiable, OntologyTerm, _serialize_obj,
                                    _deserialize_list, from_url)


def test_types():
    class Dummy(Identifiable):
        '''A dummy class'''
    dummy = Dummy()
    assert_equal(dummy.meta.types, ['prov:Entity', 'nsg:Dummy'])

    dummy.meta.types = 'value changed'
    assert_equal(dummy.evolve().meta.types, 'value changed')

def test_from_url():
    assert_raises(Exception, from_url, 'https://no-python-class-at-this-url')

def test_serialize():
    obj = Identifiable()
    obj.meta.types = 'changed types'

    assert_equal(_serialize_obj(obj),
                 {'@id': None, '@type': 'changed types'})

    assert_equal(_serialize_obj(datetime(2018, 12, 23)),
                 '2018-12-23T00:00:00')

    assert_equal(_serialize_obj(OntologyTerm(url='A', label='B')),
                 {'@id': 'A', 'label': 'B'})

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)

    dummy = Dummy(a=33, b=Dummy(a=12))
    assert_equal(_serialize_obj(dummy),
                 {'a': 33, 'b': {'a': 12}})

    assert_equal(_serialize_obj(42), 42)


def test_deserialize_list():
    assert_equal(_deserialize_list(dict, [{'a': 'b'}], token=None),
                 {'a': 'b'})

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)
    assert_equal(_deserialize_list(List[Dummy], [{'a': 1, 'b': 2}], token=None),
                 [Dummy(a=1, b=2)])


@responses.activate
def test_Identifiable_find_by():
    class Dummy(Identifiable):
        # if not set, query url will depend on env var NEXUS_ORG
        _url_org = 'dummy_org'
        _url_version = 'v0.1.0'

    with patch('entity_management.base.nexus.find_by', return_value=None):
        assert_equal(Dummy.find_by(), None)


    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org/simulation/dummy/v0.1.0',
                  status=303,
                  headers={'Location': 'https://query-location-url-1?from=0&size=10'})
    assert_equal(Dummy.find_by(dummy=OntologyTerm(url='A', label='B')).url,
                 'https://query-location-url-1?from=0&size=10')
    assert_equal(Dummy.find_by(dummy=('eq', 'A')).url,
                 'https://query-location-url-1?from=0&size=10')
    assert_equal(Dummy.find_by(dummy=Identifiable(id='an-awesome-id')).url,
                 'https://query-location-url-1?from=0&size=10')


    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org/simulation/dummy',
                  status=303,
                  headers={'Location': 'https://query-location-url-2?from=0&size=10'})
    assert_equal(Dummy.find_by(all_versions=True).url, 'https://query-location-url-2?from=0&size=10')


    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org',
                  status=303,
                  headers={'Location': 'https://query-location-url-3?from=0&size=10'})
    assert_equal(Dummy.find_by(all_domains=True).url, 'https://query-location-url-3?from=0&size=10')


    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries',
                  status=303,
                  headers={'Location': 'https://query-location-url-4?from=0&size=10'})
    assert_equal(Dummy.find_by(all_organizations=True).url, 'https://query-location-url-4?from=0&size=10')



def test_find_unique():
    class MockResult:
        id = 12

    single_result = MockResult()
    with patch.object(Identifiable, 'find_by', return_value=iter([single_result])):
        ok_(Identifiable.find_unique(name="whatever") is single_result)

    too_many_result = repeat(MockResult(), 4)
    with patch.object(Identifiable, 'find_by', return_value=too_many_result):
        assert_raises(Exception, Identifiable.find_unique, name="whatever")

    no_result = iter(list())
    with patch.object(Identifiable, 'find_by', return_value=no_result):
        ok_(not Identifiable.find_unique(name="whatever"))

        assert_raises(Exception, Identifiable.find_unique, name="whatever", throw=True)
        assert_equal(Identifiable.find_unique(name="whatever", on_no_result=lambda: 7), 7)
