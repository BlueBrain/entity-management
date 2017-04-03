import collections
import copy

import nose.tools as nt


def deep_update(dict_a, dict_b):
    assert(isinstance(dict_a, collections.Mapping))
    assert(isinstance(dict_a, collections.Mapping))

    for key, value_a in dict_a.iteritems():
        if key in dict_b:
            value_b = dict_b[key]
            assert(type(value_a) == type(value_b))
            if isinstance(value_a, collections.Mapping):
                deep_update(value_a, value_b)
            else:
                dict_a[key] = copy.deepcopy(value_b)

    for key, value_b in dict_b.iteritems():
        if key not in dict_a:
            dict_a[key] = copy.deepcopy(value_b)


def test_deep_update():
    dict_a = {
        'a': 1,
        'b': {
            'c': 2,
            'd': 3,
        }
    }
    dict_b = {
        'a': 11,
        'b': {
            'c': 22,
            'e': 44,
        },
        'f': {
            'g': 55
        },
    }
    dict_ab = {
        'a': 11,
        'b': {
            'c': 22,
            'd': 3,
            'e': 44,
        },
        'f': {
            'g': 55
        },
    }
    deep_update(dict_a, dict_b)
    nt.assert_equal(dict_a, dict_ab)
