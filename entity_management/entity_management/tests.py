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
    pos = util._attrs_pos(Abc)
    kw = util._attrs_kw(Abc)

    assert len(pos) == 1
    assert len(kw) == 1
    assert 'a' in pos
    assert 'b' in kw
