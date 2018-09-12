import operator
import attr
from six.moves.urllib.parse import urlsplit  # pylint: disable=import-error,no-name-in-module
from nose.tools import assert_raises, ok_, assert_equal

from itertools import repeat
from mock import patch

from entity_management import util
from entity_management.base import Identifiable
from entity_management.nexus import _type_hint_from


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
    assert_equal(Dummy()._types, ['prov:Entity', ':Dummy'])
    assert_equal(Dummy(types=['foo', 'bar'])._types, ['foo', 'bar'])
