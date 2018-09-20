from datetime import datetime
import operator
import attr
from six.moves.urllib.parse import urlsplit  # pylint: disable=import-error,no-name-in-module
from nose.tools import assert_raises, ok_, assert_equal
import sys

from itertools import repeat
from mock import patch
import responses

from entity_management import util, from_url
from entity_management.base import Identifiable, _serialize_obj, OntologyTerm
import entity_management.nexus as nx
from entity_management.nexus import _type_hint_from
import entity_management.core as core

from entity_management.settings import BASE, USERINFO

AGENT_JSON = {'email': 'James@Bond', 'given_name': 'James', 'family_name': 'Bond'}
PERSON_JSLD = {
        '@id': 'http://url/to/core/person/v/id',
        '@type': [
            'nsg:Person',
            'prov:Person'
            ],
        'email': 'James@Bond',
        'familyName': 'Bond',
        'givenName': 'James',
        'nxv:deprecated': False,
        'nxv:rev': 1
}

def test_dict_merg():
    assert {} == util._merge()
    assert {} == util._merge({})
    assert {1: 2} == util._merge({1: 2})
    assert {1: 2, 'a': 'b'} == util._merge({'a': 'b'}, {1: 2})
    assert {1: 2, 'a': 'c'} == util._merge({'a': 'b'}, {1: 2}, {'a': 'c'})


def test_attrs_utils():
    # define attrs class
    @attr.s
    class Abc(object):
        a = attr.ib()  # mandatory positional attribute
        b = attr.ib(default=None)  # optional keyword attribute with default value

    # split attributes defined on the class into mandatory/optional
    pos = util._attrs_clone(Abc, operator.eq)
    kw = util._attrs_clone(Abc, operator.ne)

    assert len(pos) == 1
    assert len(kw) == 1
    assert 'a' in pos
    assert 'b' in kw


def test_resolve_path():
    assert util.resolve_path('') == 'nsg:'
    assert util.resolve_path('a') == 'nsg:a'
    assert util.resolve_path('a_b') == 'a:b'
    assert util.resolve_path('a__b') == 'nsg:a / nsg:b'
    assert util.resolve_path('a_b__c_d') == 'a:b / c:d'


def test_url_to_type():
    id_url = 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/0c7d5e80-c275-4187-897e-946da433b642'
    assert _type_hint_from(id_url) == 'simulation/morphologyrelease'

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

@responses.activate
def test_nexus_find_by():
    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/a-good-query',
                  status=303,
                  headers={'Location': 'https://query-location-url'})

    assert_equal(nx.find_by(collection_address='/a-good-query'),
                 'https://query-location-url')

    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/no-redirection',
                  status=200)

    assert_equal(nx.find_by(collection_address='/no-redirection'), None)

def test_from_url():
    assert_raises(Exception, from_url, 'https://no-python-class-at-this-url')

@responses.activate
def test_Identifiable_find_by():
    class Dummy(Identifiable):
        # if not set, query url will depend on env var NEXUS_ORG
        _url_org = 'dummy_org'
        _url_version = 'v0.1.0'

    responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/dummy_org/simulation/dummy/v0.1.0',
                  status=303,
                  headers={'Location': 'https://query-location-url?from=0&size=10'})


    ok_(Dummy.find_by(collection_address='/a-good-query') is not None)


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

def test_types():
    class Dummy(Identifiable):
        '''A dummy class'''
    dummy = Dummy()
    assert_equal(dummy.meta.types, ['prov:Entity', ':Dummy'])

    dummy.meta.types = 'value changed'
    assert_equal(dummy.evolve().meta.types, 'value changed')

@responses.activate
def test_get_current_agent():
    responses.add(responses.GET, USERINFO, json=AGENT_JSON)
    responses.add(responses.POST,
                  '%s/queries/neurosciencegraph/core/person/v0.1.0' % BASE,
                  status=303,
                  headers={'Location': 'http://url/to/query/result?from=0&size=1'})
    responses.add(responses.GET,
                  'http://url/to/query/result',
                  json={'results': [{'resultId': 'http://url/to/core/person/v/id'}], 'total': 1})
    responses.add(responses.GET,
                  'http://url/to/core/person/v/id',
                  json=PERSON_JSLD)

    assert_equal(core.Person.get_current(use_auth='token').email, 'James@Bond')
