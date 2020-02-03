'''Test module for low level code:
 - entity_management.nexus
 - entity_management.util
'''

import operator

import attr
import responses
from mock import patch

import entity_management.core as core
import entity_management.nexus as nx
from entity_management import util
from entity_management.state import get_org, set_org, get_proj, set_proj
from entity_management.settings import USERINFO
from util import assert_substring, captured_output, strip_color_codes


AGENT_JSON = {'email': 'James@Bond', 'given_name': 'James', 'family_name': 'Bond'}
PERSON_JSLD = {
        '@id': 'http://url/to/core/person/v/id',
        '@type': [
            'nsg:Person',
            'nsg:Dummy',
            'prov:Person'
            ],
        'email': 'James@Bond',
        'familyName': 'Bond',
        'givenName': 'James',
        'nxv:deprecated': False,
        'nxv:rev': 1
}

CAT_WOMAN_JSON = {'email': 'cat@woman', 'given_name': 'Cat', 'family_name': 'Woman'}
CAT_WOMAN_JSLD = {
        '@id': 'http://url/to/core/person/v/id/cat_woman',
        '@type': [
            'nsg:Person',
            'prov:Person'
            ],
        'email': 'Cat@Woman',
        'familyName': 'Cat',
        'givenName': 'Woman',
        'nxv:deprecated': False,
        'nxv:rev': 1
}


def test_dict_merg():
    assert {1: 2, 'a': 'c', 3: 4} == util._merge({'a': 'b'}, {1: 2}, {'a': 'c'}, {3: 4})


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


def test_state_proj():
    set_proj('tmp')
    assert get_proj() == 'tmp'


def test_state_org():
    set_org('tmp')
    assert get_org() == 'tmp'


# def test_url_to_type():
#     id_url = 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/0c7d5e80-c275-4187-897e-946da433b642'
#     assert _type_hint_from(id_url) == 'simulation/morphologyrelease'
#
#
# @responses.activate
# def test_get_current_agent():
#     with patch('entity_management.core.nexus.get_current_agent', return_value=None):
#         ok_(core.Person.get_current(use_auth='token') is None)
#
#     responses.add(responses.GET, USERINFO, json=AGENT_JSON)
#     responses.add(responses.POST,
#                   '%s/queries/neurosciencegraph/core/person/v0.1.0' % BASE,
#                   status=303,
#                   headers={'Location': 'http://url/to/query/result?from=0&size=1'})
#     responses.add(responses.GET,
#                   'http://url/to/query/result',
#                   json={'results': [{'resultId': 'http://url/to/core/person/v/id'}], 'total': 1})
#     responses.add(responses.GET,
#                   'http://url/to/core/person/v/id',
#                   json=PERSON_JSLD)
#
#     person = core.Person.get_current(use_auth='token')
#     assert_equal(person.types, ['nsg:Person', 'nsg:Dummy', 'prov:Person'])
#     assert_equal(person.email, 'James@Bond')
#
#
# @responses.activate
# def test_get_current_agent_not_in_nexus():
#     '''Test that a Person entity is created if it does not exist'''
#     responses.add(responses.GET, USERINFO, json=CAT_WOMAN_JSON)
#     responses.add(responses.POST,
#                   '%s/queries/neurosciencegraph/core/person/v0.1.0' % BASE,
#                   status=303,
#                   headers={'Location': 'http://url/to/query/result?from=0&size=1'})
#
#     # Cat woman does not exist in DB
#     responses.add(responses.GET,
#                   'http://url/to/query/result',
#                   json={'results': [], 'total': 0})
#
#     # Creation of Cat Woman
#     responses.add(responses.POST,
#                   '%s/data/neurosciencegraph/core/person/v0.1.0' % BASE,
#                   json=CAT_WOMAN_JSLD)
#
#     # Cat woman now exists in DB
#     responses.add(responses.GET,
#                   'http://url/to/query/result',
#                   json={'results': [{'resultId': 'http://url/to/core/person/v/id'}], 'total': 1})
#
#     assert_equal(core.Person.get_current(use_auth='token').email, 'cat@woman')
#
#
# @responses.activate
# def test_nexus_find_by():
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/a-good-query',
#                   status=303,
#                   headers={'Location': 'https://query-location-url'})
#
#     assert_equal(nx.find_by(collection_address='/a-good-query'),
#                  'https://query-location-url')
#
#     responses.add(responses.POST, 'https://bbp-nexus.epfl.ch/staging/v0/queries/no-redirection',
#                   status=200)
#
#     assert_equal(nx.find_by(collection_address='/no-redirection'), None)
#
#
# def test_print_violation_summary():
#     with captured_output() as (_, err):
#         nx._print_violation_summary({
#             '@context': 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/error/v0.1.0',
#             'violations': [
#                 'Error: Violation Error(<http://www.w3.org/ns/shacl#ShapesFailed>). Node(_:e7df3db3cef74a8be41bfe0a177afa12) Failed property shapes Node: _:e7df3db3cef74a8be41bfe0a177afa12, Constraint: _:5a74392f2c619ed2780d5e6a802772c2, path: PredicatePath(<>)',
#                 "Error: Violation Error(<http://www.w3.org/ns/shacl#classError>). Node(<https://bbp-nexus.epfl.ch/staging/v0/data/thalamusproject/morphology/reconstructedpatchedcell/v0.1.1/04ff7858-088c-49bd-8c1b-14adb5741c60>) Node <https://bbp-nexus.epfl.ch/staging/v0/data/thalamusproject/morphology/reconstructedpatchedcell/v0.1.1/04ff7858-088c-49bd-8c1b-14adb5741c60> doesn't belong to class <http://www.w3.org/ns/prov#Entity> Node: _:e7df3db3cef74a8be41bfe0a177afa12, Constraint: _:66234297346da423c601b6c230b3f04b, path: PredicatePath(<https://bbp-nexus.epfl.ch/vocabs/bbp/neurosciencegraph/core/v0.1.0/morphology>)"],
#             'code': 'ShapeConstraintViolations'}
#         )
#
#     assert_substring('''NEXUS ERROR SUMMARY:
#
# Violation(<http://www.w3.org/ns/shacl#ShapesFailed>):
# Failed property shapes, path: PredicatePath(<>)
#
# Violation(<http://www.w3.org/ns/shacl#classError>):
# Node(<https://bbp-nexus.epfl.ch/staging/v0/data/thalamusproject/morphology/reconstructedpatchedcell/v0.1.1/04ff7858-088c-49bd-8c1b-14adb5741c60>) Node <https://bbp-nexus.epfl.ch/staging/v0/data/thalamusproject/morphology/reconstructedpatchedcell/v0.1.1/04ff7858-088c-49bd-8c1b-14adb5741c60> doesn't belong to class <http://www.w3.org/ns/prov#Entity>, path: PredicatePath(<https://bbp-nexus.epfl.ch/vocabs/bbp/neurosciencegraph/core/v0.1.0/morphology>)
# ''', strip_color_codes(err.getvalue()))
