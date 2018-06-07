#!/usr/bin/env python
'''Upload data to nexus'''
import os

from entity_management.base import Distribution, OntologyTerm
from entity_management.simulation import (MorphologyRelease, EModelRelease, MEModelRelease,
                                          SynapseRelease, ModelReleaseIndex, CircuitCellProperties,
                                          EdgeCollection, NodeCollection, Target, DetailedCircuit)

TOKEN = os.getenv('NEXUS_TOKEN')

BASE = 'file:///gpfs/bbp.cscs.ch/project/proj55/oreilly/releases/2018-04-19/%s'

# BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
#                             label='field CA1 of the hippocampus')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10088',
                       label='Mouse')

morphology_index_name = 'thalamus morphology release index'
morphology_index = ModelReleaseIndex.from_name(morphology_index_name, use_auth=TOKEN)
if morphology_index is None:
    morphology_index = ModelReleaseIndex(name=morphology_index_name,
                                         distribution=Distribution(
                                             downloadURL=BASE % 'bioname/extNeuronDB.dat',
                                             mediaType='text/plain'))
    morphology_index = morphology_index.publish(use_auth=TOKEN)
# else:
#     morphology_index = morphology_index.evolve(distribution=Distribution(
#         downloadURL=BASE % 'bioname/extNeuronDB.dat',
#         mediaType='text/plain'))
#     morphology_index = morphology_index.publish(use_auth=TOKEN)


morphology_release_name = 'thalamus morphology release'
morphology_release = MorphologyRelease.from_name(morphology_release_name, use_auth=TOKEN)
if morphology_release is None:
    morphology_release = MorphologyRelease(
            name=morphology_release_name,
            distribution=Distribution(downloadURL=BASE % 'morph_release/ascii'),
            morphologyIndex=morphology_index)
    morphology_release = morphology_release.publish(use_auth=TOKEN)


circuit_cell_properties_name = 'thalamus cell properties'
circuit_cell_properties = CircuitCellProperties.from_name(circuit_cell_properties_name,
                                                          use_auth=TOKEN)
if circuit_cell_properties is None:
    circuit_cell_properties = CircuitCellProperties(
            name=circuit_cell_properties_name,
            distribution=Distribution(downloadURL=BASE % 'circuit.mvd3',
                                      mediaType='application/mvd3'))
    circuit_cell_properties = circuit_cell_properties.publish(use_auth=TOKEN)


emodel_index_name = 'thalamus emodel release index'
emodel_index = ModelReleaseIndex.from_name(emodel_index_name, use_auth=TOKEN)
if emodel_index is None:
    emodel_index = ModelReleaseIndex(
            name=emodel_index_name,
            distribution=Distribution(
                downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/home/vangeit/modelmanagement/'
                            'prod.20171103/mm_runs/run/1810912/output/final.json',
                mediaType='application/json'))
    emodel_index = emodel_index.publish(use_auth=TOKEN)


emodel_release_name = 'thalamus emodel release'
emodel_release = EModelRelease.from_name(emodel_release_name, use_auth=TOKEN)
if emodel_release is None:
    emodel_release = EModelRelease(
            name=emodel_release_name,
            distribution=Distribution(
                downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/entities/'
                            'emodels/2017.11.03/hoc'),
            emodelIndex=emodel_index)
    emodel_release = emodel_release.publish(use_auth=TOKEN)


memodel_index_name = 'thalamus memodel release index'
memodel_index = ModelReleaseIndex.from_name(memodel_index_name, use_auth=TOKEN)
if memodel_index is None:
    memodel_index = ModelReleaseIndex(name=memodel_index_name,
                                      distribution=Distribution(
                                          downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/'
                                          'entities/emodels/2017.11.03/mecombo_emodel.tsv',
                                          mediaType='text/plain'))
    memodel_index = memodel_index.publish(use_auth=TOKEN)


memodel_name = 'thalamus memodel release'
memodel_release = MEModelRelease.from_name(memodel_name, use_auth=TOKEN)
if memodel_release is None:
    memodel_release = MEModelRelease(
        name=memodel_name,
        morphologyRelease=morphology_release,
        emodelRelease=emodel_release,
        memodelIndex=memodel_index)
    memodel_release = memodel_release.publish(use_auth=TOKEN)


synapse_release_name = 'thalamus synapse release'
synapse_release = SynapseRelease.from_name(synapse_release_name, use_auth=TOKEN)
if synapse_release is None:
    synapse_release = SynapseRelease(
            name=synapse_release_name,
            distribution=Distribution(
                downloadURL='https://bbpcode.epfl.ch/browse/code/sim/neurodamus/bbp/commit/'
                            '?id=035728dd3474970721399e1906270359b7fa9bb2', # FIXME
                mediaType='text/plain'))
    synapse_release = synapse_release.publish(use_auth=TOKEN)


edge_population_name = 'thalamus edge population1'
edge_population = ModelReleaseIndex.from_name(edge_population_name, use_auth=TOKEN)
if edge_population is None:
    edge_population = ModelReleaseIndex(name=edge_population_name,
                                        distribution=Distribution(accessURL=BASE)) # FIXME
    edge_population.types.append('nsg:Entity')
    edge_population = edge_population.publish(use_auth=TOKEN)


edge_collection_name = 'thalamus edge collection'
edge_collection = EdgeCollection.from_name(edge_collection_name, use_auth=TOKEN)
if edge_collection is None:
    edge_collection = EdgeCollection(
            name=edge_collection_name,
            edgePopulation=edge_population,
            synapseRelease=synapse_release)
    edge_collection = edge_collection.publish(use_auth=TOKEN)


node_collection_name = 'thalamus node collection'
node_collection = NodeCollection.from_name(node_collection_name, use_auth=TOKEN)
if node_collection is None:
    node_collection = NodeCollection(
            name=node_collection_name,
            memodelRelease=memodel_release,
            circuitCellProperties=circuit_cell_properties)
    node_collection = node_collection.publish(use_auth=TOKEN)


target_name = 'thalamus target'
target = Target.from_name(target_name, use_auth=TOKEN)
if target is None:
    target = Target(name=target_name, distribution=Distribution(accessURL=BASE % 'start.target'))
    target = target.publish(use_auth=TOKEN)


circuit_name = 'thalamus detailed circuit'
circuit = DetailedCircuit.from_name(circuit_name, use_auth=TOKEN)
if circuit is None:
    circuit = DetailedCircuit(
            name=circuit_name,
            description='test thalamus circuit',
            species=SPECIES,
            nodeCollection=node_collection,
            edgeCollection=edge_collection,
            target=target)
    circuit = circuit.publish(use_auth=TOKEN)
