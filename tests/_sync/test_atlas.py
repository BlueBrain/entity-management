# Automatically generated, DO NOT EDIT.
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from entity_management import atlas as test_module
from entity_management import nexus
from tests.util import TEST_DATA_DIR as DATA_DIR


@pytest.fixture
def atlas_release_metadata():
    return json.loads(Path(DATA_DIR, "atlas_release_resp.json").read_bytes())


def test_atlas_release(monkeypatch, atlas_release_metadata):

    monkeypatch.setattr(nexus, "load_by_url", MagicMock(return_value=atlas_release_metadata))

    res = test_module.AtlasRelease.from_id(None)

    assert res.get_id() is not None
    assert res.brainTemplateDataLayer.get_id() is not None
    assert res.hemisphereVolume.get_id() is not None
    assert res.parcellationOntology.get_id() is not None
    assert res.parcellationVolume.get_id() is not None
    assert res.spatialReferenceSystem.get_id() is not None
    assert res.subject.species.url == "NCBITaxon:10090"
    assert res.subject.species.label == "Mus musculus"
