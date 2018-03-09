#!/usr/bin/env python
'''Upload dummy test data to nexus'''

from io import StringIO

from pprint import pprint

from entity_management.base import Distribution
from entity_management.prov import Agent, Activity
from entity_management.simulation.cell import (MorphologyRelease, EModelRelease, MEModelRelease,
                                               EModel, SubCellularModel, ModelScript, Morphology)
from entity_management.simulation.circuit import (NodeCollection, SynapseRelease, EdgeCollection,
                                                  CellPlacement, Target, DetailedCircuit)


agent_name = 'NSE'
agent = Agent.from_name(agent_name)
if agent is None:
    agent = Agent(name=agent_name)
    agent = agent.save()


# morphology_release_name = 'Test MorphologyRelease'
morphology_release_name = '2012 Morphology release'
morphology_release = MorphologyRelease.from_name(morphology_release_name)
if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name=morphology_release_name,
        description=morphology_release_name + ' description',
        distribution=Distribution(
            downloadURL='file:///distribution',
            mediaType='application/swc'),
        morphologyIndex=Distribution(
            downloadURL='file:///morphologyIndex',
            mediaType='text/plain'))
    morphology_release.save()
    pprint('MorphologyRelease created: ' + morphology_release_name)


activity_name = 'test activity'
activity = Activity.from_name(activity_name)
if activity is None:
    activity = Activity(used=morphology_release)
    activity = activity.save()


emodel_release_name = 'EModel Release'
emodel_release = EModelRelease.from_name(emodel_release_name)
if emodel_release is None:
    pprint('EModelRelease creating...')
    emodel_release = EModelRelease(
        name=emodel_release_name,
        description='EModel Release description',
        distribution=Distribution(
            downloadURL='file:///Emodel/release/distribution',
            mediaType='application/neuroml'),
        emodelIndex=Distribution(
            downloadURL='file:///emodelIndex',
            mediaType='application/neuroml'))
    emodel_release.save()
    pprint('EModelRelease created: EModel release')


name = 'mod files'
mod_files = ModelScript.from_name(name)
if mod_files is None:
    pprint('Mod files creating...')
    mod_files = ModelScript(
        name=name,
        description=name + ' description',
        distribution=Distribution(accessURL='file:///SubCellularModel/mod/files'))
    mod_files.save()
    pprint('Mod files created')


sub_cellular_model_name = 'SubCellularModel'
sub_cellular_model = SubCellularModel.from_name(sub_cellular_model_name)
if sub_cellular_model is None:
    pprint('SubCellularModel creating...')
    sub_cellular_model = SubCellularModel(
        name=sub_cellular_model_name,
        description=sub_cellular_model_name + ' description',
        modelScript=mod_files)
    sub_cellular_model.save()
    pprint('SubCellularModel created: ' + sub_cellular_model_name)


name = 'hoc files'
hoc_files = ModelScript.from_name(name)
if hoc_files is None:
    pprint('Hoc files creating...')
    hoc_files = ModelScript(
        name=name,
        description=name + ' description',
        distribution=Distribution(accessURL='file:///EModel/hoc/files'))
    hoc_files.save()
    pprint('Hoc files created')


emodel_name = 'EModel'
emodel = EModel.from_name(emodel_name)
if emodel is None:
    pprint('EModelRelease creating...')
    emodel = EModel(
        name=emodel_name,
        description=emodel_name + ' description',
        subCellularMechanism=sub_cellular_model,
        modelScript=hoc_files,
        isPartOf=emodel_release)
    emodel.save()
    pprint('EModel created: ' + emodel_name)


memodel_name = 'MEModel Release'
memodel_release = MEModelRelease.from_name(memodel_name)
if memodel_release is None:
    pprint('MEModelRelease creating...')
    memodel_release = MEModelRelease(
        name=memodel_name,
        description='MEModel Release description',
        morphologyRelease=morphology_release,
        emodelRelease=emodel_release,
        memodelIndex=Distribution(
            downloadURL='file:///memodelIndex',
            mediaType='application/neuroml'))
    memodel_release.save()
    pprint('MEModelRelease created: MEModel Release')


cell_placement_name = 'CellPlacement'
cell_placement = CellPlacement.from_name(cell_placement_name)
if cell_placement is None:
    pprint('CellPlacement creating...')
    cell_placement = CellPlacement(
            name=cell_placement_name,
            description=cell_placement_name + ' description',
            distribution=Distribution(
                downloadURL='file:///cell/placement/distribution',
                mediaType='application/neuroml'))
    cell_placement.save()
    pprint('CellPlacement created: ' + cell_placement_name)


node_collection_name = 'NodeCollection'
node_collection = NodeCollection.from_name(node_collection_name)
if node_collection is None:
    pprint('NodeCollection creating...')
    node_collection = NodeCollection(
            name=node_collection_name,
            description='NodeCollection description',
            memodelRelease=memodel_release,
            cellPlacement=cell_placement)
    pprint(node_collection.as_json_ld())
    node_collection.save()
    pprint('NodeCollection created' + node_collection_name)


synapse_release_name = 'SynapseRelease'
synapse_release = SynapseRelease.from_name(synapse_release_name)
if synapse_release is None:
    pprint('SynapseRelease creating...')
    synapse_release = SynapseRelease(
            name=synapse_release_name,
            distribution=Distribution(downloadURL='file:///synapse/release'))
    synapse_release = synapse_release.save()
    pprint('SynapseRelease created: ' + synapse_release_name)


edge_collection_name = 'EdgeCollection'
edge_collection = EdgeCollection.from_name(edge_collection_name)
if edge_collection is None:
    pprint('EdgeCollection creating...')
    edge_collection = EdgeCollection(
            name=edge_collection_name,
            edgePopulation=Distribution(accessURL='file:///edge/collection'),
            synapseRelease=synapse_release)
    edge_collection = edge_collection.save()
    pprint('EdgeCollection created: ' + edge_collection_name)


target_name = 'Target'
target = Target.from_name(target_name)
if target is None:
    pprint('Target creating...')
    target = Target(name=target_name, distribution=Distribution(downloadURL='file:///target'))
    target = target.save()
    pprint('Target created: ', target_name)


update = False

circuit_name = 'DetailedCircuit'
circuit = DetailedCircuit.from_name(circuit_name)
if circuit is None:
    pprint('DetailedCircuit creating...')
    circuit = DetailedCircuit(
            name=circuit_name,
            nodeCollection=node_collection,
            edgeCollection=edge_collection,
            target=target)
    circuit.save()
    pprint('DetailedCircuit created: ' + circuit_name)
elif update:
    pprint('DetailedCircuit updating...')
    circuit = circuit.evolve(description='DetailedCircuit description')
    circuit.save()
    pprint('DetailedCircuit updated')


# create morphology with dummy attachment
morphology_name = 'Morphology'
morphology = Morphology.from_name(morphology_name)
if morphology is None:
    morphology = Morphology(name=morphology_name)
    morphology = morphology.save()

    file_name = 'test.html'
    file_data = StringIO(u'hello')
    file_type = 'text/html'
    morphology = morphology.attach(file_name, file_data, file_type)
