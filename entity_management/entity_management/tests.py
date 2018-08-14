import operator
import attr

from entity_management import util


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
        a = attr.ib() # mandatory positional attribute
        b = attr.ib(default=None) # optional keyword attribute with default value

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
