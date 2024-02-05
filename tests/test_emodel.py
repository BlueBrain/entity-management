
import json
from pathlib import Path

import pytest

from entity_management import nexus
from entity_management import emodel as test_module


DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def emodel_release_resp():
    return json.loads((DATA_DIR / "emodel_release_resp.json").read_bytes())


def test_EModelRelease(monkeypatch, emodel_release_resp):

    monkeypatch.setattr(nexus, 'load_by_url', lambda *args, **kwargs: emodel_release_resp)

    emodel_release = test_module.EModelRelease.from_id(None)

    assert emodel_release.name is not None
    assert emodel_release.eModelDataCatalog.get_id() is not None
    assert emodel_release.contribution.agent.get_id() is not None
    assert emodel_release.brainLocation.brainRegion.url is not None
    assert emodel_release.atlasRelease.get_id() is not None
    assert emodel_release.atlasRelease.get_rev() is not None
    assert emodel_release.eModelDataCatalog.get_id() is not None


@pytest.fixture(scope="module")
def emodel_data_catalog_resp():
    return json.loads((DATA_DIR / "emodel_data_catalog_resp.json").read_bytes())


def test_EModelDataCatalog(monkeypatch, emodel_data_catalog_resp):

    monkeypatch.setattr(nexus, 'load_by_url', lambda *args, **kwargs: emodel_data_catalog_resp)

    catalog = test_module.EModelDataCatalog.from_id(None)

    assert catalog.name is not None
    assert catalog.distribution.contentUrl is not None
    assert catalog.distribution.encodingFormat == "application/json"
    assert catalog.description is not None
    assert catalog.contribution.agent.get_id() is not None
    assert catalog.brainLocation.brainRegion.url is not None

    assert len(catalog.hasPart) > 0
    for emodel_instance in catalog.hasPart:
        assert isinstance(emodel_instance, test_module.EModel)
        assert emodel_instance.get_id() is not None
