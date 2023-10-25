# pylint: disable=missing-docstring,no-member
import io
import json
from datetime import datetime
from typing import List

import pytest

import attr
import requests
from SPARQLWrapper import Wrapper

from entity_management.settings import JSLD_ID, JSLD_REV, JSLD_TYPE
from entity_management.state import set_proj, get_base_resources, set_base, get_base_url
from entity_management.base import (Identifiable, OntologyTerm,
                                    _deserialize_list, _serialize_obj, Unconstrained, _deserialize_dict)
from entity_management import state
from entity_management.state import get_org, get_proj
from entity_management.core import ModelRuntimeParameters
from entity_management.morphology import ReconstructedPatchedCell
import entity_management.nexus as nexus

state.ACCESS_TOKEN = 'foo'


def test_id_type(monkeypatch):
    class Dummy(Identifiable):
        '''A dummy class'''
    dummy = Dummy()
    monkeypatch.setattr(nexus, 'create', lambda *args, **kwargs: {JSLD_ID: 'id',
                                                                  JSLD_REV: 1,
                                                                  JSLD_TYPE: 'Dummy'})
    dummy = dummy.publish()
    assert dummy._id == 'id'
    assert dummy._type == 'Dummy'


def test_serialize():
    assert _serialize_obj(datetime(2018, 12, 23)) == '2018-12-23T00:00:00'

    assert _serialize_obj(OntologyTerm(url='A', label='B')) == {'@id': 'A', 'label': 'B'}

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)

    dummy = Dummy(a=33, b=Dummy(a=12))
    assert _serialize_obj(dummy) == {'a': 33, 'b': {'a': 12}}

    dummy = Dummy(a={1: 2}, b=[OntologyTerm(url='A', label='B')])
    assert _serialize_obj(dummy) == {'a': {1: 2}, 'b': [{'@id': 'A', 'label': 'B'}]}

    assert _serialize_obj(42) == 42


def test_deserialize_list():
    assert _deserialize_list(dict, [{'a': 'b'}], token=None) == {'a': 'b'}

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)
    assert _deserialize_list(List[Dummy], [{'a': 1, 'b': 2}], token=None) == [Dummy(a=1, b=2)]


def test_deserialize_dict__single_type():

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)

    res = _deserialize_dict(dict[str, Dummy], {"foo": {"a": 1, "b": 2}, "bar": {"a": 2, "b": 3}})

    assert res == {"foo": Dummy(a=1, b=2), "bar": Dummy(a=2, b=3)}


def test_deserialize_dict__no_types():
    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)

    res = _deserialize_dict(dict, {"foo": {"a": 1, "b": 2}, "bar": {"a": 2, "b": 3}})

    assert res == {"foo": {"a": 1, "b": 2}, "bar": {"a": 2, "b": 3}}


@pytest.fixture(name='unconstrained_resp', scope='session')
def fixture_unconstrained():
    with open('tests/data/unconstrained_resp.json') as f:
        return json.load(f)


def test_unconstrained(monkeypatch, unconstrained_resp):
    monkeypatch.setattr(nexus, 'create', lambda *args, **kwargs: unconstrained_resp)
    obj = Unconstrained(json=dict(key1='value1', key2='value2'))
    assert get_base_url() == '%s/%s/%s/_' % (get_base_resources(), get_org(), get_proj())
    obj = obj.publish()
    assert obj._constrainedBy == 'https://bluebrain.github.io/nexus/schemas/unconstrained.json'
    assert obj.json['key1'] == 'value1'
    assert obj.json['key2'] == 'value2'


def test_project_change():
    obj = Unconstrained(json=dict(key1='value1', key2='value2'))
    assert get_base_url() == '%s/%s/%s/_' % (get_base_resources(), get_org(), get_proj())
    set_proj('test')
    assert get_base_url() == '%s/%s/%s/_' % (get_base_resources(), get_org(), 'test')


def test_env_change():
    assert get_base_resources() == 'https://bbp.epfl.ch/nexus/v1/resources'
    set_base('https://dev.nexus.ocp.bbp.epfl.ch/v1')
    assert get_base_resources() == 'https://dev.nexus.ocp.bbp.epfl.ch/v1/resources'


@pytest.fixture(name='cells_page1_resp', scope='session')
def fixture_reconstructed_patched_cells_page1():
    with open('tests/data/cells_page1_resp.json') as f:
        return f.read()


@pytest.fixture(name='cells_page2_resp', scope='session')
def fixture_reconstructed_patched_cells_page2():
    with open('tests/data/cells_page2_resp.json') as f:
        return f.read()


def test_list_by_schema(monkeypatch, cells_page1_resp, cells_page2_resp):
    class MockResponsePage1():
        status_code = 200
        content = cells_page1_resp
        @staticmethod
        def raise_for_status():
            pass

    class MockResponsePage2():
        status_code = 200
        content = cells_page2_resp
        @staticmethod
        def raise_for_status():
            pass

    with monkeypatch.context() as m:
        m.setattr(requests, 'get', lambda *args, **kwargs: MockResponsePage1)
        cells = ReconstructedPatchedCell.list_by_schema(page_size=2)
        cell = next(cells)
        assert cells.total_items == 3
        ids = ['https://bbp.epfl.ch/neurosciencegraph/data/0d3f11ac-2c85-43d5-becd-4a248a7010da',
               'https://bbp.epfl.ch/neurosciencegraph/data/1ad83c37-b3b3-4f0e-b729-f6f7bc07ea52']
        assert cell.get_id() in ids
        assert next(cells).get_id() in ids

    with monkeypatch.context() as m:
        m.setattr(requests, 'get', lambda *args, **kwargs: MockResponsePage2)
        assert (next(cells).get_id() ==
                'https://bbp.epfl.ch/neurosciencegraph/data/20bdaa94-41e0-4ccf-b5c2-920b95b136ed')


def test_list_by_sparql(monkeypatch):

    with monkeypatch.context() as m:
        m.setattr(Wrapper,
                  'urlopener',
                  lambda *args, **kwargs: io.FileIO('tests/data/sparql_resp.json'))
        params = ModelRuntimeParameters.list_by_model('dummy_model_resource_id')
        param = next(params)
        assert param.get_id().endswith('org/proj/_/fdc9b964-5737-4d58-8d18-cb9af0a1ef38')
