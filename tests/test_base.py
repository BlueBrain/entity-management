# pylint: disable=missing-docstring,no-member
import io
import sys
import json
from datetime import datetime
from typing import List, Dict
from dateutil.parser import parse
from unittest.mock import patch

from typing import Dict, List, Union

import pytest

import attr
import requests
from SPARQLWrapper import Wrapper

from entity_management.settings import JSLD_ID, JSLD_REV, JSLD_TYPE, JSLD_LINK_REV
from entity_management.state import set_proj, get_base_resources, set_base, get_base_url
from entity_management.base import (
    Identifiable,
    OntologyTerm,
    _deserialize_list,
    _deserialize_frozen,
    _deserialize_json_to_datatype,
    _serialize_obj,
    Unconstrained,
    NotInstantiated,
    Frozen,
    BlankNode,
    attributes,
    AttrOf,
    Subject,
    Derivation,
    BrainLocation,
)
from entity_management import state
from entity_management.state import get_org, get_proj
from entity_management.core import ModelRuntimeParameters
from entity_management.morphology import ReconstructedPatchedCell
import entity_management.nexus as nexus
from entity_management.typing import MaybeList


state.ACCESS_TOKEN = "foo"


def test_id_type(monkeypatch):
    class Dummy(Identifiable):
        """A dummy class"""

    dummy = Dummy()
    monkeypatch.setattr(
        nexus, "create", lambda *args, **kwargs: {JSLD_ID: "id", JSLD_REV: 1, JSLD_TYPE: "Dummy"}
    )
    dummy = dummy.publish()
    assert dummy._id == "id"
    assert dummy._type == "Dummy"


def test_id_type__nexus_expanded_response(monkeypatch):
    class Dummy(Identifiable):
        """A dummy class"""

    dummy = Dummy()
    monkeypatch.setattr(
        nexus,
        "create",
        lambda *args, **kwargs: {JSLD_ID: "id", JSLD_REV: 1, JSLD_TYPE: "expanded/Dummy"},
    )
    dummy = dummy.publish()
    assert dummy._id == "id"
    assert dummy._type == "Dummy"


def test_serialize():
    assert _serialize_obj(datetime(2018, 12, 23)) == "2018-12-23T00:00:00"

    assert _serialize_obj(OntologyTerm(url="A", label="B")) == {"@id": "A", "label": "B"}

    @attr.s
    class Dummy(object):
        a = attr.ib(default=42)
        b = attr.ib(default=None)

    dummy = Dummy(a=33, b=Dummy(a=12))
    assert _serialize_obj(dummy) == {"a": 33, "b": {"a": 12}}

    dummy = Dummy(a={1: 2}, b=[OntologyTerm(url="A", label="B")])
    assert _serialize_obj(dummy) == {"a": {1: 2}, "b": [{"@id": "A", "label": "B"}]}

    assert _serialize_obj(42) == 42


def test_serialize__derivation():

    @attributes(
        {
            "a": AttrOf(int),
            "b": AttrOf(float),
        }
    )
    class A(Identifiable):
        pass

    resp = _make_valid_resp({"@id": "my-id", "@type": "A", "a": 1, "b": 2.0})

    with patch("entity_management.nexus.load_by_id", return_value=resp):
        a = A.from_id("my-id")

    derivation = Derivation(entity=a)

    res = _serialize_obj(derivation)

    assert res == {"entity": {"@id": "my-id", "@type": "A"}, "@type": "Derivation"}


def test_serialize__brain_location():

    brain_location = BrainLocation(brainRegion=OntologyTerm(url="foo"))

    res = _serialize_obj(brain_location)

    assert res == {"brainRegion": {"@id": "foo", "label": None}, "@type": "BrainLocation"}


def test_serialize_obj__include_rev__instantiated_with_revision():

    class A(Identifiable):
        pass

    a = A._lazy_init(resource_id="foo", type_="A", rev=5)

    res = _serialize_obj(a, include_rev=False)
    assert res == {JSLD_ID: "foo", JSLD_TYPE: "A"}

    res = _serialize_obj(a, include_rev=True)
    assert res == {JSLD_ID: "foo", JSLD_TYPE: "A", JSLD_LINK_REV: 5}

    d = Derivation(entity=a)
    res = _serialize_obj(d, include_rev=True)
    assert res == {
        "entity": {JSLD_ID: "foo", JSLD_TYPE: "A", JSLD_LINK_REV: 5},
        JSLD_TYPE: "Derivation",
    }


def test_serialize_obj__include_rev__instantiated_wout_revision(monkeypatch):

    monkeypatch.setattr(nexus, "load_by_url", lambda *args, **kwargs: {"@type": "A", "_rev": 8})

    class A(Identifiable):
        pass

    a = A._lazy_init(resource_id="foo", type_="A")

    res = _serialize_obj(a, include_rev=False)
    assert res == {JSLD_ID: "foo", JSLD_TYPE: "A"}

    res = _serialize_obj(a, include_rev=True)
    assert res == {JSLD_ID: "foo", JSLD_TYPE: "A", JSLD_LINK_REV: 8}


@attr.s
class Dummy:
    a = attr.ib(default=42)
    b = attr.ib(default=None)


@attributes(
    {
        "a": AttrOf(int, default=42),
        "b": AttrOf(str, default=None),
    }
)
class FrozenDummy(Frozen):
    pass


@attributes(
    {
        "a": AttrOf(int),
        "b": AttrOf(float),
    }
)
class BlankNode1(BlankNode):
    pass


@attributes(
    {
        "c": AttrOf(int),
        "d": AttrOf(float),
    }
)
class BlankNode2(BlankNode):
    pass


def _skip(*args, min_version):
    return pytest.param(
        *args,
        marks=pytest.mark.skipif(
            sys.version_info < min_version,
            reason=f"Test requres {min_version} or higher.",
        ),
    )


def _eval(string_or_type):
    if isinstance(string_or_type, str):
        return eval(string_or_type)
    return string_or_type


@pytest.mark.parametrize(
    "data_type, data_raw, expected",
    [
        (str, None, None),
        (list, [], None),
        (List, [], None),
        (dict, {}, None),
        (Dict, {}, None),
        (datetime, {"@value": "2024-01-22T10:07:16.052123Z"}, parse("2024-01-22T10:07:16.052123Z")),
        (dict, {"a": "b"}, {"a": "b"}),
        (Dict, {"a": "b"}, {"a": "b"}),
        (dict, [{"a": "b"}], {"a": "b"}),
        (Dict, [{"a": "b"}], {"a": "b"}),
        (list, [{"a": "b"}], [{"a": "b"}]),
        (List, [{"a": "b"}], [{"a": "b"}]),
        _skip("list[dict]", [{"a": "b"}], [{"a": "b"}], min_version=(3, 9)),
        _skip("list[dict]", [], None, min_version=(3, 9)),
        (List[dict], [{"a": "b"}], [{"a": "b"}]),
        (List[Dict], [{"a": "b"}], [{"a": "b"}]),
        _skip("list[Dict]", [{"a": "b"}], [{"a": "b"}], min_version=(3, 9)),
        _skip("list[dict]", {"a": "b"}, [{"a": "b"}], min_version=(3, 9)),
        (List[str], "Ringo", ["Ringo"]),
        _skip("list[str]", "Ringo", ["Ringo"], min_version=(3, 9)),
        _skip("list[str]", [], None, min_version=(3, 9)),
        _skip("list[str]", ["a", "b"], ["a", "b"], min_version=(3, 9)),
        (List[int], 2, [2]),
        _skip("list[int]", 2, [2], min_version=(3, 9)),
        (List[float], 2.0, [2.0]),
        _skip("list[float]", 2.0, [2.0], min_version=(3, 9)),
        (List[bool], True, [True]),
        _skip("list[bool]", False, [False], min_version=(3, 9)),
        (Dummy, {"a": 1, "b": 2}, Dummy(a=1, b=2)),
        (List[Dummy], [{"a": 1, "b": 2}], [Dummy(a=1, b=2)]),
        _skip("list[Dummy]", [{"a": 1, "b": 2}], [Dummy(a=1, b=2)], min_version=(3, 9)),
        _skip("list[Dummy]", [], None, min_version=(3, 9)),
        (List[Dummy], {"a": 1, "b": 2}, [Dummy(a=1, b=2)]),
        _skip("list[Dummy]", {"a": 1, "b": 2}, [Dummy(a=1, b=2)], min_version=(3, 9)),
        _skip(
            "list[Dummy]",
            [{"a": 1, "b": 2}, {"a": 2, "b": 3}],
            [Dummy(a=1, b=2), Dummy(a=2, b=3)],
            min_version=(3, 9),
        ),
        (FrozenDummy, {"a": 1, "b": "2"}, FrozenDummy(a=1, b="2")),
        (List[FrozenDummy], {"a": 1, "b": "2"}, [FrozenDummy(a=1, b="2")]),
        _skip(
            "list[FrozenDummy]", {"a": 1, "b": "2"}, [FrozenDummy(a=1, b="2")], min_version=(3, 9)
        ),
        _skip("list[FrozenDummy]", [], None, min_version=(3, 9)),
        _skip("dict[str, str]", {"foo": "bar"}, {"foo": "bar"}, min_version=(3, 9)),
        _skip(
            "dict[str, Dummy]",
            {"foo": {"a": 1, "b": "2"}},
            {"foo": Dummy(a=1, b="2")},
            min_version=(3, 9),
        ),
        _skip(
            "dict[str, FrozenDummy]",
            {"foo": {"a": 1, "b": "2"}},
            {"foo": FrozenDummy(a=1, b="2")},
            min_version=(3, 9),
        ),
        _skip(
            "dict[str, list[Dummy]]",
            {"foo": {"a": 1, "b": "2"}},
            {"foo": [Dummy(a=1, b="2")]},
            min_version=(3, 9),
        ),
        (
            OntologyTerm,
            {"@id": "foo", "label": "bar", "@type": "zee"},
            OntologyTerm(url="foo", label="bar"),
        ),
        (datetime, "2024-02-21T18:03:18.804172", datetime(2024, 2, 21, 18, 3, 18, 804172)),
        (datetime, {"@type": "xsd:date", "@value": "2024-02-14"}, datetime(2024, 2, 14, 0, 0)),
        (Union[int, float], 2, 2),
        _skip("int | float", 2, 2, min_version=(3, 10)),
        (Union[int, float], 1.0, 1.0),
        _skip("int | float", 1.0, 1.0, min_version=(3, 10)),
        (Union[int, dict], {"a": 1, "b": 2}, {"a": 1, "b": 2}),
        _skip("int | dict", {"a": 1, "b": 2}, {"a": 1, "b": 2}, min_version=(3, 10)),
        (Union[int, dict], 2, 2),
        _skip("int | dict", 2, 2, min_version=(3, 10)),
        (
            Union[BlankNode1, BlankNode2],
            {"@type": "BlankNode1", "a": 2, "b": 3.0},
            BlankNode1(a=2, b=3.0),
        ),
        _skip(
            "BlankNode1 | BlankNode2",
            {"@type": "BlankNode1", "a": 2, "b": 3.0},
            BlankNode1(a=2, b=3.0),
            min_version=(3, 10),
        ),
        (
            Union[BlankNode1, BlankNode2],
            {"@type": "BlankNode2", "c": 2, "d": 3.0},
            BlankNode2(c=2, d=3.0),
        ),
        _skip(
            "BlankNode1 | BlankNode2",
            {"@type": "BlankNode2", "c": 2, "d": 3.0},
            BlankNode2(c=2, d=3.0),
            min_version=(3, 10),
        ),
        (MaybeList[int], 1, 1),
        (MaybeList[int], [1, 2], [1, 2]),
        (MaybeList[Dummy], {"a": 1, "b": "2"}, Dummy(a=1, b="2")),
        (
            MaybeList[Dummy],
            [{"a": 1, "b": "2"}, {"a": 2, "b": "3"}],
            [Dummy(a=1, b="2"), Dummy(a=2, b="3")],
        ),
    ],
)
def test_deserialize_json_to_datatype(data_type, data_raw, expected):
    assert _deserialize_json_to_datatype(_eval(data_type), data_raw) == expected


def test_deserialize_frozen():
    # test that a frozen deserialized as BlankNode works for backward compatibility
    res = _deserialize_frozen(BlankNode1, {"a": 2, "b": 3.0}, None, None, None, None, None)
    assert res == BlankNode1(a=2, b=3.0)


def _make_valid_resp(data):
    res = {
        "@context": [
            "https://bluebrain.github.io/nexus/contexts/metadata.json",
            "https://bbp.neuroshapes.org",
        ],
        "_rev": 1,
        "_project": "my-project",
        "_self": "my-self",
        "_constrainedBy": "https://bluebrain.github.io/nexus/schemas/unconstrained.json",
        "_createdAt": "2024-01-22T10:07:16.052123Z",
        "_createdBy": "https://bbp.epfl.ch/nexus/v1/realms/bbp/users/zisis",
        "_deprecated": False,
        "_updatedAt": "2024-01-22T10:07:16.052123Z",
        "_updatedBy": "https://bbp.epfl.ch/nexus/v1/realms/bbp/users/zisis",
    }
    res.update(data)
    return res


def test_deserialize_json_to_datatype__union(monkeypatch):

    @attributes(
        {
            "a": AttrOf(int, default=42),
            "b": AttrOf(str, default=None),
        }
    )
    class T1(Identifiable):
        pass

    @attributes(
        {
            "c": AttrOf(int, default=42),
            "d": AttrOf(str, default=None),
        }
    )
    class T2(Identifiable):
        pass

    data_raw_t1 = _make_valid_resp(
        {
            "@id": "t1-id",
            "@type": "T1",
            "a": 1,
            "b": "2",
        }
    )

    monkeypatch.setattr(nexus, "load_by_id", lambda *args, **kwargs: data_raw_t1)

    res = _deserialize_json_to_datatype(Union[T1, T2], data_raw_t1)
    assert res == T1(a=1, b="2")

    data_raw_t2 = _make_valid_resp(
        {
            "@id": "t2-id",
            "@type": "T2",
            "c": 1,
            "d": "2",
        }
    )

    monkeypatch.setattr(nexus, "load_by_id", lambda *args, **kwargs: data_raw_t2)

    res = _deserialize_json_to_datatype(Union[T1, T2], data_raw_t2)
    assert res == T2(c=1, d="2")


def test_deserialize_json_to_datatype__list_union(monkeypatch):

    @attributes(
        {
            "a": AttrOf(int, default=42),
            "b": AttrOf(str, default=None),
        }
    )
    class T1(Identifiable):
        pass

    @attributes(
        {
            "c": AttrOf(int, default=42),
            "d": AttrOf(str, default=None),
        }
    )
    class T2(Identifiable):
        pass

    @attributes(
        {
            "e": AttrOf(int, default=42),
            "f": AttrOf(str, default=None),
        }
    )
    class T3(Identifiable):
        pass

    data_raw_t1 = _make_valid_resp(
        {
            "@id": "t1-id",
            "@type": "T1",
            "a": 2,
            "b": "3",
        }
    )
    data_raw_t3 = _make_valid_resp(
        {
            "@id": "t3-id",
            "@type": "T3",
            "e": 4,
            "f": "5",
        }
    )

    def mock_load_by_id(resource_id, *args, **kwargs):
        if resource_id == "t1-id?rev=1":
            return data_raw_t1
        if resource_id == "t3-id?rev=1":
            return data_raw_t3
        raise

    monkeypatch.setattr(nexus, "load_by_id", mock_load_by_id)
    res = _deserialize_json_to_datatype(List[Union[T1, T2, T3]], [data_raw_t3, data_raw_t1])
    assert res == [T3(e=4, f="5"), T1(a=2, b="3")]


@pytest.fixture(name="unconstrained_resp", scope="session")
def fixture_unconstrained():
    with open("tests/data/unconstrained_resp.json") as f:
        return json.load(f)


def test_unconstrained(monkeypatch, unconstrained_resp):
    monkeypatch.setattr(nexus, "create", lambda *args, **kwargs: unconstrained_resp)
    obj = Unconstrained(json=dict(key1="value1", key2="value2"))
    assert get_base_url() == "%s/%s/%s/_" % (get_base_resources(), get_org(), get_proj())
    obj = obj.publish()
    assert obj._constrainedBy == "https://bluebrain.github.io/nexus/schemas/unconstrained.json"
    assert obj.json["key1"] == "value1"
    assert obj.json["key2"] == "value2"


def test_project_change():
    obj = Unconstrained(json=dict(key1="value1", key2="value2"))
    assert get_base_url() == "%s/%s/%s/_" % (get_base_resources(), get_org(), get_proj())
    set_proj("test")
    assert get_base_url() == "%s/%s/%s/_" % (get_base_resources(), get_org(), "test")


def test_env_change():
    assert get_base_resources() == "https://bbp.epfl.ch/nexus/v1/resources"
    set_base("https://dev.nexus.ocp.bbp.epfl.ch/v1")
    assert get_base_resources() == "https://dev.nexus.ocp.bbp.epfl.ch/v1/resources"


@pytest.fixture(name="cells_page1_resp", scope="session")
def fixture_reconstructed_patched_cells_page1():
    with open("tests/data/cells_page1_resp.json") as f:
        return f.read()


@pytest.fixture(name="cells_page2_resp", scope="session")
def fixture_reconstructed_patched_cells_page2():
    with open("tests/data/cells_page2_resp.json") as f:
        return f.read()


def test_list_by_schema(monkeypatch, cells_page1_resp, cells_page2_resp):
    class MockResponsePage1:
        status_code = 200
        content = cells_page1_resp

        @staticmethod
        def raise_for_status():
            pass

    class MockResponsePage2:
        status_code = 200
        content = cells_page2_resp

        @staticmethod
        def raise_for_status():
            pass

    with monkeypatch.context() as m:
        m.setattr(requests, "get", lambda *args, **kwargs: MockResponsePage1)
        cells = ReconstructedPatchedCell.list_by_schema(page_size=2)
        cell = next(cells)
        assert cells.total_items == 3
        ids = [
            "https://bbp.epfl.ch/neurosciencegraph/data/0d3f11ac-2c85-43d5-becd-4a248a7010da",
            "https://bbp.epfl.ch/neurosciencegraph/data/1ad83c37-b3b3-4f0e-b729-f6f7bc07ea52",
        ]
        assert cell.get_id() in ids
        assert next(cells).get_id() in ids

    with monkeypatch.context() as m:
        m.setattr(requests, "get", lambda *args, **kwargs: MockResponsePage2)
        assert (
            next(cells).get_id()
            == "https://bbp.epfl.ch/neurosciencegraph/data/20bdaa94-41e0-4ccf-b5c2-920b95b136ed"
        )


def test_list_by_sparql(monkeypatch):

    with monkeypatch.context() as m:
        m.setattr(
            Wrapper, "urlopener", lambda *args, **kwargs: io.FileIO("tests/data/sparql_resp.json")
        )
        params = ModelRuntimeParameters.list_by_model("dummy_model_resource_id")
        param = next(params)
        assert param.get_id().endswith("org/proj/_/fdc9b964-5737-4d58-8d18-cb9af0a1ef38")


def test_instantiate__wout_rev(monkeypatch):

    def load_by_id(resource_id, *args, **kwargs):
        if resource_id == "foo":
            return {"_rev": 1}
        raise

    monkeypatch.setattr(nexus, "load_by_id", load_by_id)

    r = Identifiable._lazy_init(resource_id="foo", type_="Foo")

    # check that _rev is not set before instantiation
    assert object.__getattribute__(r, "_rev") is NotInstantiated

    r._instantiate()

    # after instantation the _rev should be 1
    assert r.get_rev() == 1


def test_instantiate__with_rev(monkeypatch):

    def load_by_id(resource_id, *args, **kwargs):
        if resource_id == "foo?rev=3":
            return {"_rev": 3}
        raise

    monkeypatch.setattr(nexus, "load_by_id", load_by_id)

    r = Identifiable._lazy_init(resource_id="foo", type_="Foo", rev=3)

    # check that before instantiation the _rev is set
    assert object.__getattribute__(r, "_rev") == 3
    r._instantiate()
    # and that after instantiation the correct rev is fetched
    assert r.get_rev() == 3


def test_instantiate__with_tag(monkeypatch):
    def load_by_id(resource_id, *args, **kwargs):
        if resource_id == "foo?tag=v1.1":
            return {"_rev": 3}
        raise

    monkeypatch.setattr(nexus, "load_by_id", load_by_id)

    r = Identifiable._lazy_init(resource_id="foo", type_="Foo", tag="v1.1")

    # check that before instantiation the _rev is set
    assert object.__getattribute__(r, "_tag") == "v1.1"
    r._instantiate()
    # and that after instantiation the correct rev is fetched
    assert r.get_rev() == 3


def test_instantiate__precedence(monkeypatch):
    def load_by_id(resource_id, *args, **kwargs):
        if resource_id == "foo?rev=2":
            return {"_rev": 2}
        if resource_id == "foo?tag=v1.1":
            return {"_rev": 3}
        raise

    monkeypatch.setattr(nexus, "load_by_id", load_by_id)

    r = Identifiable._lazy_init(resource_id="foo", type_="Foo", tag="v1.1", rev=2)

    # check that before instantiation the _rev is set
    assert object.__getattribute__(r, "_tag") == "v1.1"
    r._instantiate()
    # and that after instantiation the correct rev is fetched
    assert r.get_rev() == 3


@pytest.mark.parametrize(
    "payload",
    [
        {
            "@id": "t1-id",
            "_self": "t1-url",
            "@type": "Test",
            "subject": {
                "@id": "subject-id",
                "@type": "Subject",
                "species": {"@id": "NCBITaxon:10090", "label": "Mus musculus"},
            },
        },
        {
            "@id": "t1-id",
            "_self": "t1-url",
            "@type": "Test",
            "subject": {
                "@type": "Subject",
                "species": {"@id": "NCBITaxon:10090", "label": "Mus musculus"},
            },
        },
        {
            "@id": "t1-id",
            "_self": "t1-url",
            "@type": "Test",
            "subject": {"@id": "subject-id", "@type": "https://neuroshapes.org/Subject"},
        },
    ],
)
def test_subject(payload):
    """Test Subject loading and pyblishing with old and new metadata."""

    def _mock_load_by_id(resource_id, *args, **kwargs):
        if resource_id == "subject-id":
            return _make_valid_resp(
                {
                    "@id": "subject-id",
                    "@type": "Subject",
                    "species": {"@id": "NCBITaxon:10090", "label": "Mus musculus"},
                }
            )

        if resource_id == "t1-id":
            return _make_valid_resp(payload)

        raise ValueError(resource_id)

    @attributes({"subject": AttrOf(Subject)})
    class Test(Identifiable):
        pass

    with patch("entity_management.nexus.load_by_id", side_effect=_mock_load_by_id):
        res = Test.from_id("t1-id")

    # Ensure that a Frozen structure is initialized with an ontology term in both cases.
    assert isinstance(res.subject, Frozen)
    assert res.subject.species.url == "NCBITaxon:10090"
    assert res.subject.species.label == "Mus musculus"

    # Ensure that we are writing the Subject without and @id in both cases.
    with patch("entity_management.nexus.update") as patched:
        res.publish()
        patched.assert_called_once_with(
            "t1-url",
            1,
            {
                "subject": {
                    "species": {"@id": "NCBITaxon:10090", "label": "Mus musculus"},
                    "@type": "Subject",
                },
                "@context": [
                    "https://bluebrain.github.io/nexus/contexts/metadata.json",
                    "https://bbp.neuroshapes.org",
                ],
                "@type": "Test",
            },
            sync_index=False,
            token=None,
        )


def test_Identifiable_clone():

    @attributes(
        {
            "a": AttrOf(int),
            "b": AttrOf(float),
        }
    )
    class A(Identifiable):
        pass

    resp = _make_valid_resp({"@id": "my-id", "@type": "A", "a": 1, "b": 2.0})

    with patch("entity_management.nexus.load_by_id", return_value=resp):
        a = A.from_id("my-id")

    assert a.get_id() is not None

    b = a.clone(a=2, b=3.0)

    assert b is not a
    assert isinstance(b, A)
    assert b.get_id() is None
