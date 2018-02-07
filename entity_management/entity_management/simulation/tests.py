import responses

from mock import patch, Mock
from nose.tools import raises

from pprint import pprint

import entity_management.nexus as nexus

from entity_management import base
from entity_management.simulation.circuit import (DetailedCircuit, NodeCollection,
        SynapseRelease, EdgeCollection, Target, CellPlacement)
from entity_management.simulation.cell import (MEModelRelease, EModelRelease, MorphologyRelease)

UUID = '0c7d5e80-c275-4187-897e-946da433b642'

MORPHOLOGY_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
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
        "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID
    },
    "morphologyIndex": {
        "downloadURL": "file:///morphology/index/url",
        "mediaType": "media type"
    },
    "name": "Morphology Release",
    "nxv:deprecated": False,
    "nxv:rev": 1,
    "types": [
        "nsg:Entity",
        "nsg:MorphologyRelease"
    ]}

MORPHOLOGY_RELEASE_JSLD_UPDATE = {
    "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
    "nxv:rev": 2
    }

MORPHOLOGY_RELEASE_JSLD_DELETE = {
    "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0",
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
    "nxv:rev": 2
    }

MORPHOLOGY_RELEASE_JSLD_FILTER = {
    "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/search/v0.1.0",
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/links/v0.2.0",
        "self": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0?filter=%7B%22op%22%3A%22and%22%2C%22value%22%3A%5B%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22nxv%3Adeprecated%22%2C%22value%22%3Afalse%7D%2C%7B%22op%22%3A%22eq%22%2C%22path%22%3A%22schema%3Aname%22%2C%22value%22%3A%22test+name%22%7D%5D%7D"
    },
    "results": [
        {
            "resultId": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
            "source": {
                "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
                "links": {
                    "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/links/v0.2.0",
                    "incoming": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID + "/incoming",
                    "outgoing": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID + "/outgoing",
                    "schema": "https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0",
                    "self": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID
                }
            }
        }
    ],
    "total": 1
}

EMODEL_RELEASE_JSLD_CREATE = {
    '@context': 'https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0',
    'nxv:rev': 1,
    '@id': 'https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/' + UUID
}

EMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/" + UUID,
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
        "downloadURL": "file:///emodelIndex",
        "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml"
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/" + UUID + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/" + UUID + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/emodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/" + UUID
    },
    "name": "EModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1
}

MEMODEL_RELEASE_JSLD = {
    "@context": [
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/core/entity/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/bbp/neurosciencegraph/core/v0.1.0",
        "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/resource/v0.3.0"
    ],
    "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/memodelrelease/v0.1.0/" + UUID,
    "@type": [
        "nsg:Entity",
        "nsg:MEModelRelease"
    ],
    "emodelRelease": {
        "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/emodelrelease/v0.1.0/" + UUID,
        "@type": [
            "nsg:Entity",
            "nsg:EModelRelease"
        ]
    },
    "links": {
        "@context": "https://bbp-nexus.epfl.ch/dev/v0/contexts/nexus/core/links/v0.2.0",
        "incoming": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/memodelrelease/v0.1.0/" + UUID + "/incoming",
        "outgoing": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/memodelrelease/v0.1.0/" + UUID + "/outgoing",
        "schema": "https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/memodelrelease/v0.1.0",
        "self": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/memodelrelease/v0.1.0/" + UUID
    },
    "memodelIndex": {
        "downloadURL": "file:///memodelIndex",
        "mediaType": "application/swc,application/neurolucida,application/h5,application/neuroml"
    },
    "morphologyRelease": {
        "@id": "https://bbp-nexus.epfl.ch/dev/v0/data/hbphackaton/simulation/morphologyrelease/v0.1.0/" + UUID,
        "@type": [
            "nsg:Entity",
            "nsg:MorphologyRelease"
        ]
    },
    "name": "MEModel Release",
    "nxv:deprecated": False,
    "nxv:rev": 1
}


@responses.activate
def test_load_morphology_release_by_uuid():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.description == 'test description'
    assert morphology_release.distribution.downloadURL == 'file:///distribution/url'
    assert morphology_release.morphologyIndex.downloadURL == 'file:///morphology/index/url'
    assert morphology_release.morphologyIndex.mediaType == 'media type'


@responses.activate
def test_load_morphology_release_by_name():
    responses.add(responses.GET, MorphologyRelease.base_url,
            json=MORPHOLOGY_RELEASE_JSLD_FILTER)
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease.from_name(UUID)

    assert morphology_release.description == 'test description'
    assert morphology_release.distribution.downloadURL == 'file:///distribution/url'
    assert morphology_release.morphologyIndex.downloadURL == 'file:///morphology/index/url'
    assert morphology_release.morphologyIndex.mediaType == 'media type'


@responses.activate
def test_update_morphology_release():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.PUT, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD_UPDATE)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.name == 'Morphology Release'
    assert morphology_release.rev == 1

    new_url =  'file:///distribution/newUrl'

    new_distribution = morphology_release.distribution.evolve(downloadURL=new_url)
    morphology_release = morphology_release.evolve(distribution=new_distribution)

    morphology_release = morphology_release.save()

    assert morphology_release.uuid == UUID
    assert morphology_release.name == 'Morphology Release'
    assert morphology_release.distribution.downloadURL == new_url
    assert morphology_release.rev == 2


@responses.activate
def test_save_morphology_release():
    responses.add(responses.POST, '%s' % MorphologyRelease.base_url,
            json=MORPHOLOGY_RELEASE_JSLD)

    morphology_release = MorphologyRelease(name='MorphologyRelease',
                                          distribution=base.Distribution(downloadURL='url'),
                                          morphologyIndex=base.Distribution(downloadURL='url'))
    morphology_release = morphology_release.save()

    assert morphology_release.uuid is not None
    assert morphology_release.rev is not None


@responses.activate
def test_deprecate_morphology_release():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.DELETE, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD_DELETE)

    morphology_release = MorphologyRelease.from_uuid(UUID)

    assert morphology_release.name == 'Morphology Release'
    assert morphology_release.rev == 1
    assert morphology_release.deprecated == False

    morphology_release = morphology_release.deprecate()

    assert morphology_release.uuid is not None
    assert morphology_release.name == 'Morphology Release'
    assert morphology_release.rev == 2
    assert morphology_release.deprecated == True


@responses.activate
def test_create_emodel_release():
    responses.add(responses.POST, EModelRelease.base_url,
            json=EMODEL_RELEASE_JSLD_CREATE)

    emodel_release = EModelRelease(
            name='EModelRelease',
            distribution=base.Distribution(downloadURL='url'),
            emodelIndex=base.Distribution(downloadURL='url'))
    emodel_release = emodel_release.save()

    assert emodel_release.uuid is not None
    assert emodel_release.name == 'EModelRelease'
    assert emodel_release.rev == 1


def test_create_detailed_circuit():
    morphology_release = MorphologyRelease(
            name='MorphologyRelease',
            distribution=base.Distribution(downloadURL='distr url'),
            morphologyIndex=base.Distribution(downloadURL='url'))

    emodelRelease = EModelRelease(
            name='EModelRelease',
            distribution=base.Distribution(downloadURL='url'),
            emodelIndex=base.Distribution(downloadURL='url'))

    memodelRelease = MEModelRelease(
            name='MEModelRelease',
            morphologyRelease=morphology_release,
            emodelRelease=emodelRelease,
            memodelIndex=base.Distribution(downloadURL='url'))

    cellPlacement = CellPlacement(
            name='CellPlacement',
            distribution=base.Distribution(downloadURL='url'))

    nodeCollection = NodeCollection(
            name='NodeCollection',
            memodelRelease=memodelRelease,
            cellPlacement=cellPlacement)

    synapseRelease = SynapseRelease(
            name='SynapseRelease',
            distribution=base.Distribution(downloadURL='url'))
    edgeCollection = EdgeCollection(
            name='EdgeCollection',
            property_=base.Distribution(accessURL='url'),
            synapseRelease=synapseRelease)

    target = Target(name='Target', distribution=base.Distribution(downloadURL='url'))

    circuit = DetailedCircuit(
            name='DetailedCircuit',
            modelOf=None,
            nodeCollection=nodeCollection,
            edgeCollection=edgeCollection,
            target=target)

    assert circuit is not None


def test_dict_merg():
    assert {} == base._merge()
    assert {} == base._merge({})
    assert {1: 2} == base._merge({1: 2})
    assert {1: 2, 'a': 'b'} == base._merge({'a': 'b'}, {1: 2})
    assert {1: 2, 'a': 'c'} == base._merge({'a': 'b'}, {1: 2}, {'a': 'c'})


@responses.activate
def test_lazy_load_memodel_release_by_uuid():
    responses.add(responses.GET, '%s/%s' % (MorphologyRelease.base_url, UUID),
            json=MORPHOLOGY_RELEASE_JSLD)
    responses.add(responses.GET, '%s/%s' % (EModelRelease.base_url, UUID),
            json=EMODEL_RELEASE_JSLD)
    responses.add(responses.GET, '%s/%s' % (MEModelRelease.base_url, UUID),
            json=MEMODEL_RELEASE_JSLD)

    memodel_release = MEModelRelease.from_uuid(UUID)

    assert memodel_release.name == 'MEModel Release'
    assert memodel_release.memodelIndex.downloadURL == 'file:///memodelIndex'
    assert memodel_release.emodelRelease.name == 'EModel Release'
    assert memodel_release.morphologyRelease.name == 'Morphology Release'
