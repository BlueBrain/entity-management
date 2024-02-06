# pylint: disable=missing-docstring,no-member
import json
import responses
from pathlib import Path
from unittest.mock import patch

import pytest

import entity_management.core as core
from entity_management import nexus
from entity_management.state import get_base_url
from entity_management.settings import NSG, JSLD_CTX
from entity_management.core import DataDownload
from entity_management.util import quote
from entity_management.simulation import (
    ModelReleaseIndex,
    MorphologyRelease,
    Morphology,
    IonChannelMechanismRelease,
    Configuration,
    SimulationCampaignConfiguration,
    DetailedCircuit,
)

DATA_DIR = Path(__file__).parent / "data"

UUID = "0c7d5e80-c275-4187-897e-946da433b642"
DUMMY_PERSON = core.Person(email="dummy_email")
DUMMY_PERSON1 = core.Person(email="dummy_email1")
DUMMY_PERSON2 = core.Person(email="dummy_email2")

CFG_NAME = "myid"
CFG_ID = NSG[CFG_NAME]

CFG_JSLD = {
    "@context": [
        "https://bbp.neuroshapes.org",
        "https://bluebrain.github.io/nexus/contexts/resource.json",
    ],
    "@id": CFG_ID,
    "@type": "Configuration",
    "distribution": {
        "@type": "DataDownload",
        "url": "/gpfs/bbp.cscs.ch/project/proj/name/file.json",
    },
    "wasAttributedTo": {
        "@id": "https://bbp.epfl.ch/nexus/v1/resources/myorg/myproj/_/"
        "bd8de6b8-3e81-40ed-8119-67d20a97b837",
        "@type": "WorkflowExecution",
    },
    "_self": "https://bbp.epfl.ch/nexus/v1/resources/nse/test/_/%s" % quote(CFG_ID),
    "_constrainedBy": "https://bluebrain.github.io/nexus/schemas/unconstrained.json",
    "_project": "https://bbp.epfl.ch/nexus/v1/projects/myorg/myproj",
    "_rev": 1,
    "_deprecated": False,
    "_createdAt": "2019-07-02T07:27:14.162Z",
    "_createdBy": "https://bbp-nexus.epfl.ch/staging/v1/anonymous",
    "_updatedAt": "2019-07-02T07:27:14.162Z",
    "_updatedBy": "https://bbp-nexus.epfl.ch/staging/v1/anonymous",
}


MORPHOLOGY_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "%s/%s" % (get_base_url(), UUID),
    "@type": ["nsg:Entity", "nsg:MorphologyRelease"],
    "description": "test description",
    "distribution": [
        {
            "downloadURL": "file:///distribution/url",
            "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml",
        }
    ],
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "%s/%s/incoming" % (get_base_url(), UUID),
        "outgoing": "%s/%s/outgoing" % (get_base_url(), UUID),
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.1",
        "self": "%s/%s" % (get_base_url(), UUID),
    },
    "morphologyIndex": {
        "@id": "%s/%s" % (get_base_url(), UUID),
        "@type": ["nsg:ModelReleaseIndex"],
    },
    "name": "Morphology Release",
    "nxv:deprecated": False,
    "nxv:rev": 1,
}

MORPHOLOGY_RELEASE_JSLD_UPDATE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "%s/%s" % (get_base_url(), UUID),
    "nxv:rev": 2,
}

MORPHOLOGY_RELEASE_JSLD_DELETE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "%s/%s" % (get_base_url(), UUID),
    "nxv:rev": 2,
}

MORPHOLOGY_RELEASE_JSLD_FILTER = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/search/v0.1.0",
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1?filter=%7B%22op%22%3A%22and%22%2C%22value%22%3A%5B%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22nxv%3Adeprecated%22%2C%22value%22%3Afalse%7D%2C%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22schema%3Aname%22%2C%22value%22%3A%22test+name%22%7D%5D%7D",
    },
    "results": [
        {
            "resultId": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/"
            + UUID,
            "source": {
                "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/"
                + UUID,
                "links": {
                    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
                    "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/"
                    + UUID
                    + "/incoming",
                    "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/"
                    + UUID
                    + "/outgoing",
                    "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.1",
                    "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/"
                    + UUID,
                },
            },
        }
    ],
    "total": 1,
}

MORPHOLOGY_DIVERSIFICATION_JSLD_CREATE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "%s/%s" % (get_base_url(), UUID),
    "nxv:rev": 1,
}

EMODEL_RELEASE_JSLD_CREATE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "nxv:rev": 1,
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/"
    + UUID,
}

MODEL_RELEASE_INDEX_JSLD_CREATE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "nxv:rev": 1,
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/modelreleaseindex/v0.1.0/"
    + UUID,
}

EMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "%s/%s" % (get_base_url(), UUID),
    "@type": ["nsg:Entity", "nsg:EModelRelease"],
    "distribution": [
        {
            "downloadURL": "file:///Emodel/release/distribution",
            "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml",
        }
    ],
    "emodelIndex": {
        "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/modelreleaseindex/_/"
        + UUID,
        "@type": ["nsg:ModelReleaseIndex"],
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/"
        + UUID
        + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/"
        + UUID
        + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/emodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/"
        + UUID,
    },
    "name": "EModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1,
}

MEMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/"
    + UUID,
    "@type": ["nsg:Entity", "nsg:MEModelRelease"],
    "emodelRelease": {
        "@id": "%s/%s" % (get_base_url(), UUID),
        "@type": ["nsg:Entity", "nsg:EModelRelease"],
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/"
        + UUID
        + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/"
        + UUID
        + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/memodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/"
        + UUID,
    },
    "memodelIndex": {"@id": "%s/%s" % (get_base_url(), UUID), "@type": ["nsg:ModelReleaseIndex"]},
    "morphologyRelease": {
        "@id": "%s/%s" % (get_base_url(), UUID),
        "@type": ["nsg:Entity", "nsg:MorphologyRelease"],
    },
    "name": "MEModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1,
}

MORPHOLOGY_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "%s/%s" % (get_base_url(), UUID),
    "@type": ["nsg:Entity", "nsg:Morphology"],
    "name": "Morphology",
    "nxv:deprecated": False,
    "nxv:rev": 1,
}

MORPHOLOGY_PUT_JSLD = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/"
    + UUID,
    "distribution": [
        {
            "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/distribution/v0.1.0",
            "contentSize": {"unit": "byte", "value": 121440},
            "digest": {
                "algorithm": "SHA-256",
                "value": "c56a9037f0d0af13a0cffdba4fe974f5e7c342a0a045b2ae4b0831f7d5186feb",
            },
            "downloadURL": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/"
            + UUID
            + "/attachment",
            "mediaType": "text/plain",
            "originalFileName": "file_name",
        }
    ],
    "nxv:rev": 2,
}

MEMODEL_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodel/v0.1.2/"
    + UUID,
    "@type": ["nsg:Entity", "nsg:MEModel"],
    "brainRegion": {
        "@id": "http://uri.interlex.org/paxinos/uris/rat/labels/322",
        "label": "field CA1 of the hippocampus",
    },
    "species": {
        "@id": "http://purl.obolibrary.org/obo/NCBITaxon_10116",
        "label": "Rattus norvegicus",
    },
    "distribution": [None],
    "eModel": {
        "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodel/v0.1.1/9b8e44fa-664c-4490-97bd-91ae19ce596e",
        "@type": ["nsg:Entity", "nsg:EModel"],
        "name": "dummy",
    },
    "mainModelScript": {
        "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelscript/v0.1.0/baeda23e-b868-4bae-a48d-98ff069b3a70",
        "@type": ["nsg:Entity", "nsg:EModelScript"],
        "name": "dummy",
    },
    "morphology": {
        "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/_/baeda23e-b868-4bae-a48d-98ff069b3a70",
        "@type": ["nsg:Entity", "nsg:Morphology"],
        "name": "dummy",
    },
    "name": "name",
    "nxv:deprecated": False,
    "nxv:rev": 1,
}

ACTIVITY_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    ],
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/core/activity/v0.1.0/"
    + UUID,
    "@type": ["nsg:Activity", "prov:Activity"],
    "nxv:deprecated": False,
    "nxv:rev": 1,
    "name": "test activity",
    "startedAtTime": "2018-03-27T16:04:35.886105",
    "used": {"@id": "%s/%s" % (get_base_url(), UUID), "@type": ["nsg:MEModel", "prov:Entity"]},
    "wasStartedBy": {"@id": "%s/%s" % (get_base_url(), UUID), "@type": ["nsg:Agent", "prov:Agent"]},
}


@responses.activate
def test_get_configuration():
    responses.add(responses.GET, "%s/%s" % (get_base_url(), quote(CFG_ID)), json=CFG_JSLD)

    cfg = Configuration.from_id(CFG_ID)
    assert cfg._id == str(CFG_ID)


def test_configuration_serialization():
    cfg = Configuration(distribution=DataDownload(url="test_url"))
    assert cfg.as_json_ld()["distribution"]["url"] == "test_url"


def test_sim_campaign_config_serialization():
    cfg = SimulationCampaignConfiguration(
        name="test", configuration=DataDownload(url="json"), template=DataDownload(url="test")
    )
    json_ld = cfg.as_json_ld()
    assert json_ld[JSLD_CTX][0]


def _mock_circuit_load_by_id(resource_id, *args, **kwargs):
    if resource_id == "circuit-id":
        return json.loads(Path(DATA_DIR, "detailed_circuit_resp.json").read_bytes())

    # Legacy Subject with @id
    if "b9641820-659b-455a-a0ae-98bf3f333805" in resource_id:
        return {
            "@id": "subject-id",
            "@type": "Subject",
            "@context": [
                "https://bluebrain.github.io/nexus/contexts/metadata.json",
                "https://bbp.neuroshapes.org",
            ],
            "species": {"@id": "NCBITaxon:10090", "label": "Mus musculus"},
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

    raise ValuError(resource_id)


def test_detailed_circuit(monkeypatch):
    monkeypatch.setattr(nexus, "load_by_id", _mock_circuit_load_by_id)
    res = DetailedCircuit.from_id("circuit-id")
    assert res.atlasRelease.get_id() is not None

    # revision exists in the linked metadata
    assert res.atlasRelease.get_rev() == 5


def test_detailed_circuit__as_json_ld__include_revision(monkeypatch):
    monkeypatch.setattr(nexus, "load_by_id", _mock_circuit_load_by_id)

    circuit = DetailedCircuit.from_id("circuit-id")

    res = circuit.as_json_ld(include_rev=False)

    assert "_rev" not in res["brainLocation"]
    assert "_rev" not in res["circuitConfigPath"]
    assert "_rev" not in res["atlasRelease"]

    res = circuit.as_json_ld(include_rev=True)

    assert "_rev" not in res["brainLocation"]
    assert "_rev" not in res["circuitConfigPath"]
    assert res["atlasRelease"]["_rev"] == 5


def test_detailed_circuit__publish__wout_revision(monkeypatch):
    monkeypatch.setattr(nexus, "load_by_id", _mock_circuit_load_by_id)

    circuit = DetailedCircuit.from_id("circuit-id")
    circuit._force_attr("_id", None)

    with patch("entity_management.nexus.create") as patched:
        circuit.publish()
        payload = patched.call_args[0][1]
        assert "_rev" not in payload["brainLocation"]
        assert "_rev" not in payload["circuitConfigPath"]
        assert "_rev" not in payload["atlasRelease"]


def test_detailed_circuit__publish__with_revision(monkeypatch):
    monkeypatch.setattr(nexus, "load_by_id", _mock_circuit_load_by_id)

    circuit = DetailedCircuit.from_id("circuit-id")
    circuit._force_attr("_id", None)

    with patch("entity_management.nexus.create") as patched:
        circuit.publish(include_rev=True)
        payload = patched.call_args[0][1]
        assert "_rev" not in payload["brainLocation"]
        assert "_rev" not in payload["circuitConfigPath"]
        assert payload["atlasRelease"]["_rev"] == 5


# @responses.activate
# def test_load_morphology_release_by_url():
#     url = '%s/%s' % (MorphologyRelease.base_url, UUID)
#     responses.add(responses.GET, url, json=MORPHOLOGY_RELEASE_JSLD)
#
#     morphology_release = MorphologyRelease.from_url(url)
#
#     assert_equal(morphology_release.description, 'test description')
#     assert_equal(morphology_release.distribution[0].downloadURL, 'file:///distribution/url')
#
#
# @responses.activate
# def test_load_morphology_release_by_uuid():
#     responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD)
#
#     morphology_release = MorphologyRelease.from_uuid(UUID)
#
#     assert_equal(morphology_release.description, 'test description')
#     assert_equal(morphology_release.distribution[0].downloadURL, 'file:///distribution/url')
#
#
# @responses.activate
# @patch('entity_management.core.nexus.get_current_agent')
# def test_update_morphology_release(get_current_agent):
#     get_current_agent.return_value = None
#     responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD)
#     responses.add(responses.PUT, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD_UPDATE)
#
#     morphology_release = MorphologyRelease.from_uuid(UUID)
#
#     assert_equal(morphology_release.name, 'Morphology Release')
#     assert_equal(morphology_release.meta.rev, 1)
#
#     new_url =  'file:///distribution/newUrl'
#
#     new_distribution = morphology_release.distribution[0].evolve(downloadURL=new_url)
#     morphology_release = morphology_release.evolve(distribution=[new_distribution])
#
#     morphology_release = morphology_release.publish()
#
#     assert_equal(morphology_release.id, '%s/%s' % (MorphologyRelease.base_url, UUID))
#     assert_equal(morphology_release.name, 'Morphology Release')
#     assert_equal(morphology_release.distribution[0].downloadURL, new_url)
#     assert_equal(morphology_release.meta.rev, 2)
#
#
# @responses.activate
# def test_publish_morphology_release():
#     responses.add(responses.POST, '%s' % MorphologyDiversification.base_url,
#             json=MORPHOLOGY_DIVERSIFICATION_JSLD_CREATE)
#     responses.add(responses.POST, '%s' % MorphologyRelease.base_url,
#             json=MORPHOLOGY_RELEASE_JSLD)
#
#     morphology_release = MorphologyRelease(name='MorphologyRelease',
#                                            distribution=[base.Distribution(downloadURL='url')])
#     morphology_release = morphology_release.publish(person=DUMMY_PERSON,
#             activity=MorphologyDiversification(used=[Configuration(name='')]))
#
#     ok_(morphology_release.id is not None)
#     ok_(morphology_release.meta.rev is not None)
#
#
# @responses.activate
# def test_deprecate_morphology_release():
#     responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD)
#     responses.add(responses.DELETE, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD_DELETE)
#
#     morphology_release = MorphologyRelease.from_uuid(UUID)
#
#     assert_equal(morphology_release.name, 'Morphology Release')
#     assert_equal(morphology_release.meta.rev, 1)
#     assert_equal(morphology_release.meta.deprecated, False)
#
#     morphology_release = morphology_release.deprecate()
#
#     assert_equal(morphology_release.name, 'Morphology Release')
#     ok_(morphology_release.id is not None)
#     assert_equal(morphology_release.meta.rev, 2)
#     assert_equal(morphology_release.meta.deprecated, True)
#
#
# @responses.activate
# def test_publish_emodel_release():
#     responses.add(responses.POST, ModelReleaseIndex.base_url,
#                   json=MODEL_RELEASE_INDEX_JSLD_CREATE)
#     responses.add(responses.POST, EModelRelease.base_url,
#                   json=EMODEL_RELEASE_JSLD_CREATE)
#
#     emodel_index = ModelReleaseIndex(
#             name='index',
#             distribution=[base.Distribution(downloadURL='url')],
#             )
#     emodel_index = emodel_index.publish(person=DUMMY_PERSON)
#     assert_equal(emodel_index.wasAttributedTo, [DUMMY_PERSON],
#                  'Attribution was not automatically set to the provided person')
#
#     emodel_release = EModelRelease(
#             name='EModelRelease',
#             distribution=[base.Distribution(downloadURL='url')],
#             emodelIndex=emodel_index,
#             wasAttributedTo=[DUMMY_PERSON1, DUMMY_PERSON2])
#     assert_equal(emodel_release.wasAttributedTo, [DUMMY_PERSON1, DUMMY_PERSON2],
#                  'Explicitly set attribution on the entity was not kept')
#
#     emodel_release = emodel_release.publish(person=DUMMY_PERSON)
#
#     ok_(emodel_release.id is not None)
#     assert_equal(emodel_release.name, 'EModelRelease')
#     assert_equal(emodel_release.meta.rev, 1)
#
#
# def test_create_detailed_circuit():
#     morphology_index = ModelReleaseIndex(name='index',
#                                          distribution=[base.Distribution(downloadURL='url')])
#     morphology_release = MorphologyRelease(
#             name='MorphologyRelease',
#             distribution=[base.Distribution(downloadURL='distr url')],
#             morphologyIndex=morphology_index)
#
#     emodel_index = ModelReleaseIndex(name='index',
#                                      distribution=[base.Distribution(downloadURL='url')])
#     emodelRelease = EModelRelease(
#             name='EModelRelease',
#             distribution=[base.Distribution(downloadURL='url')],
#             emodelIndex=emodel_index)
#
#     memodel_index = ModelReleaseIndex(name='index',
#                                       distribution=[base.Distribution(downloadURL='url')])
#     memodelRelease = MEModelRelease(
#             name='MEModelRelease',
#             morphologyRelease=morphology_release,
#             emodelRelease=emodelRelease,
#             memodelIndex=memodel_index)
#
#     circuitCellProperties = CircuitCellProperties(
#             name='CircuitCellProperties',
#             distribution=[base.Distribution(downloadURL='url')])
#
#     nodeCollection = NodeCollection(
#             name='NodeCollection',
#             memodelRelease=memodelRelease,
#             circuitCellProperties=circuitCellProperties)
#
#     synapseRelease = SynapseRelease(
#             name='SynapseRelease',
#             distribution=[base.Distribution(downloadURL='url')])
#     edgePopulation = core.Entity(name='edges',
#                                  distribution=[base.Distribution(accessURL='url')])
#     edgeCollection = EdgeCollection(
#             name='EdgeCollection',
#             edgePopulation=edgePopulation,
#             synapseRelease=synapseRelease)
#
#     target = Target(name='Target', distribution=[base.Distribution(downloadURL='url')])
#
#     circuit = DetailedCircuit(
#             name='DetailedCircuit',
#             modelOf=None,
#             nodeCollection=nodeCollection,
#             edgeCollection=edgeCollection,
#             target=target)
#
#     assert circuit is not None
#
#
# @responses.activate
# def test_lazy_load_memodel_release_by_uuid():
#     responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
#             json=MORPHOLOGY_RELEASE_JSLD)
#     responses.add(responses.GET, '%s/%s' % (EModelRelease.base_url, UUID),
#             json=EMODEL_RELEASE_JSLD)
#     responses.add(responses.GET, '%s/%s' % (MEModelRelease.base_url, UUID),
#             json=MEMODEL_RELEASE_JSLD)
#
#     memodel_release = MEModelRelease.from_uuid(UUID)
#
#     assert_equal(memodel_release.name, 'MEModel Release')
#     assert_equal(memodel_release.emodelRelease.name, 'EModel Release')
#     assert_equal(memodel_release.morphologyRelease.name, 'Morphology Release')
#
#
# @responses.activate
# def test_morphology_attachment():
#     responses.add(responses.GET, '%s/%s' % (Morphology.base_url, UUID),
#             json=MORPHOLOGY_JSLD)
#     responses.add(responses.PUT, '%s/%s/attachment' % (Morphology.base_url, UUID),
#             json=MORPHOLOGY_PUT_JSLD)
#
#     morphology = Morphology.from_uuid(UUID)
#
#     assert_equal(morphology.name, 'Morphology')
#     assert_equal(morphology.meta.rev, 1)
#
#     morphology = morphology.attach('file_name', StringIO(u'hello'), 'text/plain')
#
#     assert_equal(morphology.name, 'Morphology')
#     assert_equal(morphology.meta.rev, 2)
#     assert_equal(morphology.distribution[0].downloadURL, 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/' + UUID + '/attachment')
#     assert_equal(morphology.distribution[0].contentSize['value'], 121440)
#     assert morphology.distribution[0].contentSize['unit'] == 'byte'
#     assert morphology.distribution[0].digest['value'] == 'c56a9037f0d0af13a0cffdba4fe974f5e7c342a0a045b2ae4b0831f7d5186feb'
#     assert morphology.distribution[0].digest['algorithm'] == 'SHA-256'
#     assert morphology.distribution[0].mediaType == 'text/plain'
#     assert morphology.distribution[0].originalFileName == 'file_name'
#
#
# @responses.activate
# def test_memodel_by_uuid():
#     responses.add(responses.GET, '%s/%s' % (MEModel.base_url, UUID), json=MEMODEL_JSLD)
#     memodel = MEModel.from_uuid(UUID)
#     js = memodel.as_json_ld()
#     assert_equal(set(js.keys()),
#                  {'eModel', 'name', '@type', 'morphology', '@context', 'brainRegion', 'mainModelScript', 'species'})
#     assert_equal(js['species']['@id'], 'http://purl.obolibrary.org/obo/NCBITaxon_10116')
#     assert_equal(js['species']['label'], 'Rattus norvegicus')
#     assert_equal(js['brainRegion']['@id'], 'http://uri.interlex.org/paxinos/uris/rat/labels/322')
#     assert_equal(js['brainRegion']['label'], 'field CA1 of the hippocampus')
#
#
# @responses.activate
# def test_prov_activity_by_uuid():
#     responses.add(responses.GET, '%s/%s' % (core.Activity.base_url, UUID), json=ACTIVITY_JSLD)
#     activity = core.Activity.from_uuid(UUID)
#     assert_equal(activity.startedAtTime.year, 2018)
#     assert_equal(activity.startedAtTime.month, 3)
#     assert_equal(activity.startedAtTime.day, 27)
#     assert_equal(activity.startedAtTime.hour, 16)
#     assert_equal(activity.startedAtTime.minute, 4)
#     assert_equal(activity.startedAtTime.second, 35)
#
#     js = activity.as_json_ld()
#     assert js['startedAtTime'] == '2018-03-27T16:04:35.886105'
#
#
# def test_identifiable_instance():
#     morphology = Morphology(name='dummy', species=base.OntologyTerm(url='url', label='label'))
#     js = morphology.as_json_ld()
#     assert_equal(js['species']['@id'], 'url')
#     assert_equal(js['species']['label'], 'label')
#     assert isinstance(morphology, base.Identifiable)
#
#
# def test_subcellular_model():
#     mod_release = IonChannelMechanismRelease(
#             name='name',
#             distribution=[base.Distribution(accessURL='file:///name')])
#     model_script = SubCellularModelScript(name='name')
#     model = SubCellularModel(name='name', isPartOf=[mod_release], modelScript=model_script)
#
#
# def test_distribution_must_be_list():
#     assert_raises(TypeError, lambda: Morphology(name='name', distribution=base.Distribution(accessURL='file:///name')))
#
#
# def test_mandatory_list_distribution():
#     assert_raises(TypeError, lambda: MorphologyRelease(name='name', distribution=None))
#
#
# def test_distribution_list_same_type():
#     assert_raises(TypeError, lambda: Morphology(name='name',
#                                                 distribution=[base.Distribution(accessURL='file:///name'),
#                                                               Morphology(name='a')]))
#
#
# def test_name_should_be_provided_for_entity():
#     assert_raises(TypeError, lambda: Morphology())
#
#
# @responses.activate
# def test_incomming_outcoming():
#     payload = {"results": [
#         {"resultId": 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/' + UUID},
#         {"resultId": 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/no-python-class/v0.1.0/aaa'},
#         {"resultId": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/" + UUID},
#     ],
#                "total": 3}
#
#     class Dummy(base.Identifiable):
#         # if not set, query url will depend on env var NEXUS_ORG
#         _url_org = 'dummy_org'
#         _url_version = 'v0.1.0'
#     dummy = Dummy('https://blah')
#     dummy.meta.token = None
#
#
#     for coming in ['incoming', 'outcoming']:
#         responses.add(responses.GET, 'https://blah/{}?from=0&size=10'.format(coming),
#                   json=payload)
#
#         results = list(getattr(dummy, coming))
#         assert_equal(len(results), 3)
#         assert_equal(type(results[0]), EModelRelease)
#         assert_equal(results[1], None)
#         assert_equal(type(results[2]), MEModelRelease)
