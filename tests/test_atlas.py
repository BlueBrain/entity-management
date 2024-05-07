import json
import pytest
from entity_management import nexus
from unittest.mock import patch
from pathlib import Path

from entity_management import atlas as test_module

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def atlas_release_metadata():
    return json.loads(Path(DATA_DIR, "atlas_release_resp.json").read_bytes())


def test_atlas_release(monkeypatch, atlas_release_metadata):

    monkeypatch.setattr(nexus, "load_by_url", lambda *args, **kwargs: atlas_release_metadata)

    res = test_module.AtlasRelease.from_id(None)

    assert res.get_id() is not None
    assert res.brainTemplateDataLayer.get_id() is not None
    assert res.hemisphereVolume.get_id() is not None
    assert res.parcellationOntology.get_id() is not None
    assert res.parcellationVolume.get_id() is not None
    assert res.spatialReferenceSystem.get_id() is not None
    assert res.subject.species.url == "NCBITaxon:10090"
    assert res.subject.species.label == "Mus musculus"
