import responses

from io import StringIO

from mock import patch, Mock
from nose.tools import raises

from pprint import pprint

import entity_management.nexus as nexus

import entity_management.base as base
import entity_management.core as core
from entity_management.simulation import (DetailedCircuit, NodeCollection, ModelReleaseIndex,
                                          SynapseRelease, EdgeCollection, Target,
                                          CircuitCellProperties, MEModelRelease, EModelRelease,
                                          MorphologyRelease, Morphology, MEModel,
                                          IonChannelMechanismRelease, SubCellularModelScript,
                                          SubCellularModel)

UUID = '0c7d5e80-c275-4187-897e-946da433b642'

MORPHOLOGY_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": '%s/%s' % (MorphologyRelease._base_url, UUID),
    "@type": [
        "nsg:Entity",
        "nsg:MorphologyRelease"
    ],
    "description": "test description",
    "distribution": [
        {
            "downloadURL": "file:///distribution/url",
            "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml"
        }
    ],
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "%s/%s/incoming" % (MorphologyRelease._base_url, UUID),
        "outgoing": "%s/%s/outgoing" % (MorphologyRelease._base_url, UUID),
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.1",
        "self": "%s/%s" % (MorphologyRelease._base_url, UUID)
    },
    "morphologyIndex": {
        '@id': '%s/%s' % (ModelReleaseIndex._base_url, UUID),
        '@type': ['nsg:ModelReleaseIndex']
    },
    "name": "Morphology Release",
    "nxv:deprecated": False,
    "nxv:rev": 1,
    "types": [
        "nsg:Entity",
        "nsg:MorphologyRelease"
    ]}

MORPHOLOGY_RELEASE_JSLD_UPDATE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "%s/%s" % (MorphologyRelease._base_url, UUID),
    "nxv:rev": 2
    }

MORPHOLOGY_RELEASE_JSLD_DELETE = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "%s/%s" % (MorphologyRelease._base_url, UUID),
    "nxv:rev": 2
    }

MORPHOLOGY_RELEASE_JSLD_FILTER = {
    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/search/v0.1.0",
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1?filter=%7B%22op%22%3A%22and%22%2C%22value%22%3A%5B%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22nxv%3Adeprecated%22%2C%22value%22%3Afalse%7D%2C%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22schema%3Aname%22%2C%22value%22%3A%22test+name%22%7D%5D%7D"
    },
    "results": [
        {
            "resultId": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/" + UUID,
            "source": {
                "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/" + UUID,
                "links": {
                    "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
                    "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/" + UUID + "/incoming",
                    "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/" + UUID + "/outgoing",
                    "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.1",
                    "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphologyrelease/v0.1.1/" + UUID
                }
            }
        }
    ],
    "total": 1
}

EMODEL_RELEASE_JSLD_CREATE = {
    '@context': 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0',
    'nxv:rev': 1,
    '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/' + UUID
}

MODEL_RELEASE_INDEX_JSLD_CREATE = {
    '@context': 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0',
    'nxv:rev': 1,
    '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/modelreleaseindex/v0.1.0/' + UUID
}

EMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "%s/%s" % (EModelRelease._base_url, UUID),
    "@type": [
        "nsg:Entity",
        "nsg:EModelRelease"
    ],
    "distribution": [
        {
            "downloadURL": "file:///Emodel/release/distribution",
            "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml"
        }
    ],
    "emodelIndex": {
        '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/modelreleaseindex/' + ModelReleaseIndex._url_version + '/' + UUID,
        '@type': ['nsg:ModelReleaseIndex']
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/" + UUID + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/" + UUID + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/emodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelrelease/v0.1.0/" + UUID
    },
    "name": "EModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1
}

MEMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/" + UUID,
    "@type": [
        "nsg:Entity",
        "nsg:MEModelRelease"
    ],
    "emodelRelease": {
        "@id": "%s/%s" % (EModelRelease._base_url, UUID),
        "@type": [
            "nsg:Entity",
            "nsg:EModelRelease"
        ]
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/" + UUID + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/" + UUID + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/staging/v0/schemas/neurosciencegraph/simulation/memodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodelrelease/v0.1.0/" + UUID
    },
    "memodelIndex": {
        '@id': '%s/%s' % (ModelReleaseIndex._base_url, UUID),
        '@type': ['nsg:ModelReleaseIndex']
    },
    "morphologyRelease": {
        "@id": "%s/%s" % (MorphologyRelease._base_url, UUID),
        "@type": [
            "nsg:Entity",
            "nsg:MorphologyRelease"
        ]
    },
    "name": "MEModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1
}

MORPHOLOGY_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0",
        "https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "%s/%s" % (Morphology._base_url, UUID),
    "@type": [
        "nsg:Entity",
        "nsg:Morphology"
    ],
    "name": "Morphology",
    "nxv:deprecated": False,
    "nxv:rev": 1
}

MORPHOLOGY_PUT_JSLD = {
    '@context': 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0',
    '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/' + UUID,
    'distribution': [{
        '@context': 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/distribution/v0.1.0',
        'contentSize': {
            'unit': 'byte',
            'value': 121440
        },
        'digest': {
            'algorithm': 'SHA-256',
            'value': 'c56a9037f0d0af13a0cffdba4fe974f5e7c342a0a045b2ae4b0831f7d5186feb'
        },
        'downloadURL': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/' + UUID + '/attachment',
        'mediaType': 'text/plain',
        'originalFileName': 'file_name'}],
    'nxv:rev': 2
}

MEMODEL_JSLD = {
    '@context': ['https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0',
                 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0'],
    '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/memodel/v0.1.2/' + UUID,
    '@type': ['nsg:Entity', 'nsg:MEModel'],
    'brainRegion': {'@id': 'http://uri.interlex.org/paxinos/uris/rat/labels/322',
                    'label': 'field CA1 of the hippocampus'},
    'species': {'@id': 'http://purl.obolibrary.org/obo/NCBITaxon_10116',
                'label': 'Rattus norvegicus'},
    'distribution': [None],
    'eModel': {'@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodel/v0.1.1/9b8e44fa-664c-4490-97bd-91ae19ce596e',
               '@type': ['nsg:Entity', 'nsg:EModel'],
               'name': 'dummy'},
    'mainModelScript': {'@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/emodelscript/v0.1.0/baeda23e-b868-4bae-a48d-98ff069b3a70',
                        '@type': ['nsg:Entity', 'nsg:EModelScript'],
                        'name': 'dummy'},
    'morphology': {'@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/%s/baeda23e-b868-4bae-a48d-98ff069b3a70' % Morphology._url_version,
                   '@type': ['nsg:Entity', 'nsg:Morphology'],
                   'name': 'dummy'},
    'name': 'name',
    'nxv:deprecated': False,
    'nxv:rev': 1
}

ACTIVITY_JSLD = {
    '@context': ['https://bbp-nexus.epfl.ch/staging/v0/contexts/neurosciencegraph/core/data/v0.1.0',
                 'https://bbp-nexus.epfl.ch/staging/v0/contexts/nexus/core/resource/v0.3.0'],
    '@id': 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/core/activity/v0.1.0/' + UUID,
    '@type': ['nsg:Activity', 'prov:Activity'],
    'nxv:deprecated': False,
    'nxv:rev': 1,
    'name': 'test activity',
    'startedAtTime': '2018-03-27T16:04:35.886105',
    'used': {
        '@id': '%s/%s' % (MEModel._base_url, UUID),
        '@type': ['nsg:MEModel', 'prov:Entity']
    },
    'wasStartedBy': {
        '@id': '%s/%s' % (core.Agent._base_url, UUID),
        '@type': ['nsg:Agent', 'prov:Agent']
    }
}


@responses.activate
def test_load_morphology_release_by_url():
    url = '%s/%s' % (MorphologyRelease._base_url, UUID)
    responses.add(responses.GET, url, json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease.from_url(url)

    assert morphology_release.description == 'test description'
    assert morphology_release.distribution[0].downloadURL == 'file:///distribution/url'


@responses.activate
def test_load_morphology_release_by_uuid():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.description == 'test description'
    assert morphology_release.distribution[0].downloadURL == 'file:///distribution/url'


@responses.activate
def test_update_morphology_release():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.PUT, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD_UPDATE)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.name == 'Morphology Release'
    assert morphology_release._rev == 1

    new_url =  'file:///distribution/newUrl'

    new_distribution = morphology_release.distribution[0].evolve(downloadURL=new_url)
    morphology_release = morphology_release.evolve(distribution=[new_distribution])

    morphology_release = morphology_release.publish()

    assert morphology_release._id == '%s/%s' % (MorphologyRelease._base_url, UUID)
    assert morphology_release.name == 'Morphology Release'
    assert morphology_release.distribution[0].downloadURL == new_url
    assert morphology_release._rev == 2


@responses.activate
def test_publish_morphology_release():
    responses.add(responses.POST, '%s' % MorphologyRelease._base_url,
            json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease(name='MorphologyRelease',
                                           distribution=[base.Distribution(downloadURL='url')])
    morphology_release = morphology_release.publish()

    assert morphology_release._id is not None
    assert morphology_release._rev is not None


@responses.activate
def test_deprecate_morphology_release():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.DELETE, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD_DELETE)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.name == 'Morphology Release'
    assert morphology_release._rev == 1
    assert morphology_release._deprecated == False

    morphology_release = morphology_release.deprecate()

    assert morphology_release.name == 'Morphology Release'
    assert morphology_release._id is not None
    assert morphology_release._rev == 2
    assert morphology_release._deprecated == True


@responses.activate
def test_publish_emodel_release():
    responses.add(responses.POST, ModelReleaseIndex._base_url,
                  json=MODEL_RELEASE_INDEX_JSLD_CREATE)
    responses.add(responses.POST, EModelRelease._base_url,
                  json=EMODEL_RELEASE_JSLD_CREATE)

    emodel_index = ModelReleaseIndex(
            name='index',
            distribution=[base.Distribution(downloadURL='url')])
    emodel_index = emodel_index.publish()

    emodel_release = EModelRelease(
            name='EModelRelease',
            distribution=[base.Distribution(downloadURL='url')],
            emodelIndex=emodel_index)

    emodel_release = emodel_release.publish()

    assert emodel_release._id is not None
    assert emodel_release.name == 'EModelRelease'
    assert emodel_release._rev == 1


def test_create_detailed_circuit():
    morphology_index = ModelReleaseIndex(name='index',
                                         distribution=[base.Distribution(downloadURL='url')])
    morphology_release = MorphologyRelease(
            name='MorphologyRelease',
            distribution=[base.Distribution(downloadURL='distr url')],
            morphologyIndex=morphology_index)

    emodel_index = ModelReleaseIndex(name='index',
                                     distribution=[base.Distribution(downloadURL='url')])
    emodelRelease = EModelRelease(
            name='EModelRelease',
            distribution=[base.Distribution(downloadURL='url')],
            emodelIndex=emodel_index)

    memodel_index = ModelReleaseIndex(name='index',
                                      distribution=[base.Distribution(downloadURL='url')])
    memodelRelease = MEModelRelease(
            name='MEModelRelease',
            morphologyRelease=morphology_release,
            emodelRelease=emodelRelease,
            memodelIndex=memodel_index)

    circuitCellProperties = CircuitCellProperties(
            name='CircuitCellProperties',
            distribution=[base.Distribution(downloadURL='url')])

    nodeCollection = NodeCollection(
            name='NodeCollection',
            memodelRelease=memodelRelease,
            circuitCellProperties=circuitCellProperties)

    synapseRelease = SynapseRelease(
            name='SynapseRelease',
            distribution=[base.Distribution(downloadURL='url')])
    edgePopulation = ModelReleaseIndex(name='index',
                                       distribution=[base.Distribution(accessURL='url')])
    edgeCollection = EdgeCollection(
            name='EdgeCollection',
            edgePopulation=edgePopulation,
            synapseRelease=synapseRelease)

    target = Target(name='Target', distribution=[base.Distribution(downloadURL='url')])

    circuit = DetailedCircuit(
            name='DetailedCircuit',
            modelOf=None,
            nodeCollection=nodeCollection,
            edgeCollection=edgeCollection,
            target=target)

    assert circuit is not None


@responses.activate
def test_lazy_load_memodel_release_by_uuid():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease._base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.GET, '%s/%s' % (EModelRelease._base_url, UUID),
            json=EMODEL_RELEASE_JSLD)
    responses.add(responses.GET, '%s/%s' % (MEModelRelease._base_url, UUID),
            json=MEMODEL_RELEASE_JSLD)

    memodel_release = MEModelRelease.from_uuid(UUID)

    assert memodel_release.name == 'MEModel Release'
    assert memodel_release.emodelRelease.name == 'EModel Release'
    assert memodel_release.morphologyRelease.name == 'Morphology Release'


@responses.activate
def test_morphology_attachment():
    responses.add(responses.GET, '%s/%s' % (Morphology._base_url, UUID),
            json=MORPHOLOGY_JSLD)
    responses.add(responses.PUT, '%s/%s/attachment' % (Morphology._base_url, UUID),
            json=MORPHOLOGY_PUT_JSLD)

    morphology = Morphology.from_uuid(UUID)

    assert morphology.name == 'Morphology'
    assert morphology._rev == 1

    morphology = morphology.attach('file_name', StringIO(u'hello'), 'text/plain')

    assert morphology.name == 'Morphology'
    assert morphology._rev == 2
    assert morphology.distribution[0].downloadURL == 'https://bbp-nexus.epfl.ch/staging/v0/data/neurosciencegraph/simulation/morphology/v0.1.0/' + UUID + '/attachment'
    assert morphology.distribution[0].contentSize['value'] == 121440
    assert morphology.distribution[0].contentSize['unit'] == 'byte'
    assert morphology.distribution[0].digest['value'] == 'c56a9037f0d0af13a0cffdba4fe974f5e7c342a0a045b2ae4b0831f7d5186feb'
    assert morphology.distribution[0].digest['algorithm'] == 'SHA-256'
    assert morphology.distribution[0].mediaType == 'text/plain'
    assert morphology.distribution[0].originalFileName == 'file_name'


@responses.activate
def test_memodel_by_uuid():
    responses.add(responses.GET, '%s/%s' % (MEModel._base_url, UUID), json=MEMODEL_JSLD)
    memodel = MEModel.from_uuid(UUID)
    js = memodel.as_json_ld()
    assert js['species']['@id'] == 'http://purl.obolibrary.org/obo/NCBITaxon_10116'
    assert js['species']['label'] == 'Rattus norvegicus'
    assert js['brainRegion']['@id'] == 'http://uri.interlex.org/paxinos/uris/rat/labels/322'
    assert js['brainRegion']['label'] == 'field CA1 of the hippocampus'


@responses.activate
def test_prov_activity_by_uuid():
    responses.add(responses.GET, '%s/%s' % (core.Activity._base_url, UUID), json=ACTIVITY_JSLD)
    activity = core.Activity.from_uuid(UUID)
    assert activity.startedAtTime.year == 2018
    assert activity.startedAtTime.month == 3
    assert activity.startedAtTime.day == 27
    assert activity.startedAtTime.hour == 16
    assert activity.startedAtTime.minute == 4
    assert activity.startedAtTime.second == 35

    js = activity.as_json_ld()
    assert js['startedAtTime'] == '2018-03-27T16:04:35.886105'


def test_identifiable_instance():
    morphology = Morphology(name='dummy', species=base.OntologyTerm(url='url', label='label'))
    js = morphology.as_json_ld()
    assert js['species']['@id'] == 'url'
    assert js['species']['label'] == 'label'
    assert isinstance(morphology, base.Identifiable)


def test_subcellular_model():
    mod_release = IonChannelMechanismRelease(
            name='name',
            distribution=[base.Distribution(accessURL='file:///name')])
    model_script = SubCellularModelScript(name='name')
    model = SubCellularModel(name='name', isPartOf=[mod_release], modelScript=model_script)
