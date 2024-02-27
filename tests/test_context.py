import json
import pytest
from pathlib import Path
from unittest.mock import patch

from entity_management import context as test_module


DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def context_neuroshapes_resp():
    return [
        {
            "mba": {
                "@id": "http://api.brain-map.org/api/v2/data/Structure/",
                "@prefix": True,
            },
            "NCBITaxon": {
                "@id": "http://purl.obolibrary.org/obo/NCBITaxon_",
                "@prefix": True,
            },
        }
    ]


@pytest.fixture
def context_bbp_neuroshapes_resp():
    return {
        "@context": [
            {"@vocab": "https://bbp.epfl.ch/ontologies/core/bmo/"},
            "https://bluebrain.github.io/nexus/contexts/metadata.json",
            "https://neuroshapes.org",
        ],
        "@id": "https://bbp.neuroshapes.org",
    }


def test_resolve_context(context_neuroshapes_resp, context_bbp_neuroshapes_resp):

    def mock_load_by_id(resource_id, *args, **kwargs):

        if "bbp.neuroshapes.org" in resource_id:
            return context_bbp_neuroshapes_resp

        if "neuroshapes.org" in resource_id:
            return context_neuroshapes_resp

        raise ValueError(resource_id)

    with patch("entity_management.nexus.load_by_id", side_effect=mock_load_by_id):
        res = test_module._resolve_context(
            [
                "https://bluebrain.github.io/nexus/contexts/metadata.json",
                "https://bbp.neuroshapes.org",
            ],
            visited=set(),
        )
        assert res == {
            "@vocab": "https://bbp.epfl.ch/ontologies/core/bmo/",
            "mba": {"@id": "http://api.brain-map.org/api/v2/data/Structure/", "@prefix": True},
            "NCBITaxon": {
                "@id": "http://purl.obolibrary.org/obo/NCBITaxon_",
                "@prefix": True,
            },
        }


def test_get_resolved_context(context_neuroshapes_resp, context_bbp_neuroshapes_resp):

    def mock_load_by_id(resource_id, *args, **kwargs):

        if "bbp.neuroshapes.org" in resource_id:
            return context_bbp_neuroshapes_resp

        if "neuroshapes.org" in resource_id:
            return context_neuroshapes_resp

        raise ValueError(resource_id)

    with patch("entity_management.nexus.load_by_id", side_effect=mock_load_by_id):
        res = test_module.get_resolved_context(
            [
                "https://bluebrain.github.io/nexus/contexts/metadata.json",
                "https://bbp.neuroshapes.org",
            ]
        )

        assert res.terms.keys() == {"mba", "NCBITaxon"}

        # check that both terms are prefixes
        assert res.terms["mba"].prefix
        assert res.terms["NCBITaxon"].prefix

        # check that resolving works wrt these common terms
        assert res.resolve("mba:997") == "http://api.brain-map.org/api/v2/data/Structure/997"
        assert res.resolve("NCBITaxon:1030") == "http://purl.obolibrary.org/obo/NCBITaxon_1030"


@pytest.fixture
def context_bbp_neuroshapes_cyclic_resp():
    return {
        "@context": [
            {"@vocab": "https://bbp.epfl.ch/ontologies/core/bmo/"},
            "https://bbp.neuroshapes.org",
            "https://neuroshapes.org",
        ],
        "@id": "https://bbp.neuroshapes.org",
    }


def test_get_resolved_context__cycle(context_bbp_neuroshapes_cyclic_resp, context_neuroshapes_resp):
    def mock_load_by_id(resource_id, *args, **kwargs):

        if "bbp.neuroshapes.org" in resource_id:
            return context_bbp_neuroshapes_cyclic_resp

        if "neuroshapes.org" in resource_id:
            return context_neuroshapes_resp

        raise ValueError(resource_id)

    with patch("entity_management.nexus.load_by_id", side_effect=mock_load_by_id):
        res = test_module.get_resolved_context(
            [
                "https://bluebrain.github.io/nexus/contexts/metadata.json",
                "https://bbp.neuroshapes.org",
            ]
        )
