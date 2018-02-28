#!/usr/bin/env python
'''Upload data to nexus'''

from pprint import pprint

from entity_management.base import Distribution
from entity_management.simulation.cell import (MorphologyRelease, EModelRelease, MEModelRelease,
                                               SynapseRelease)
from entity_management.simulation.circuit import (CellPlacement, EdgeCollection, NodeCollection,
                                                  Target, DetailedCircuit)


# Skip v5 at the moment
# morphology_release = MorphologyRelease.from_name('2012 Morphology release')
# if morphology_release is None:
#     pprint('MorphologyRelease creating...')
#     morphology_release = MorphologyRelease(
#         name='2012 Morphology release',
#         description='Morphology release used for the O1.V5 microcircuit',
#         distribution=Distribution(
#             # FIXME
#             # accessURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
#             #           'morphology_release/release_20120531'),
#             downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
#                       'morphology_release/release_20120531',
#             mediaType='application/neuroml'),
#         morphologyIndex=Distribution(
#             downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
#                         'morphology_release/release_20120531/neuronDB.dat',
#             mediaType='text/plain'))
#
#     morphology_release = morphology_release.save()
#     pprint('MorphologyRelease created: 2012 Morphology release')
#
# cell_placement_name = 'O1.v5 cell placement'
# cell_placement = CellPlacement.from_name(cell_placement_name)
# if cell_placement is None:
#     pprint('CellPlacement creating...')
#     cell_placement = CellPlacement(
#             name=cell_placement_name,
#             description=cell_placement_name + ' description',
#             distribution=Distribution(
#                 downloadURL='file:///gpfs/bbp.cscs.ch/project/proj1/circuits/'
#                             'SomatosensoryCxS1-v5.r0/O1/merged_circuit/circuit.mvd2',
#                 mediaType='application/mvd2'))
#     cell_placement = cell_placement.save()
#     pprint('CellPlacement created: ' + cell_placement_name)
#
#
# emodel_release_name = 'O1.v5 emodel release'
# emodel_release = EModelRelease.from_name(emodel_release_name)
# if emodel_release is None:
#     pprint('EModelRelease creating...')
#     emodel_release = EModelRelease(
#         name=emodel_release_name,
#         description=emodel_release_name,
#         distribution=Distribution(
#             accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/home/vangeit/modelmanagement/'
#                       'prod.20171103/mm_runs/run/1810912/output/emodels_hoc/'),
#         emodelIndex=Distribution(
#             downloadURL='file:///gpfs/bbp.cscs.ch/project/proj38/singlecell/optimization/'
#                         'releases/2c80837/final.json',
#             mediaType='text/plain'))
#     emodel_release = emodel_release.save()
#     pprint('EModelRelease created: EModel release')
#
#
# memodel_name = 'O1.v5 memodel release'
# memodel_release = MEModelRelease.from_name(memodel_name)
# if memodel_release is None:
#     pprint('MEModelRelease creating...')
#     memodel_release = MEModelRelease(
#         name=memodel_name,
#         description='MEModel Release description',
#         morphologyRelease=morphology_release,
#         emodelRelease=emodel_release,
#         memodelIndex=Distribution(
#             downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/home/vangeit/modelmanagement/'
#                         'prod.20171103/megate_runs/run/6c6d611/output_select/mecombo_emodel.tsv',
#             mediaType='text/plain'))
#     memodel_release = memodel_release.save()
#     pprint('MEModelRelease created: MEModel Release')
#
#
# synapse_release_name = 'O1.v5 synapse release'
# synapse_release = SynapseRelease.from_name(synapse_release_name)
# if synapse_release is None:
#     pprint('SynapseRelease creating...')
#     synapse_release = SynapseRelease(
#             name=synapse_release_name,
#             distribution=Distribution(
#                 downloadURL='https://bbpcode.epfl.ch/browse/code/sim/neurodamus/bbp/commit/'
#                             '?id=035728dd3474970721399e1906270359b7fa9bb2',
#                 mediaType='text/plain'))
#     synapse_release = synapse_release.save()
#     pprint('SynapseRelease created: ' + synapse_release_name)
#
#
# edge_collection_name = 'O1.v5 edge collection'
# edge_collection = EdgeCollection.from_name(edge_collection_name)
# if edge_collection is None:
#     pprint('EdgeCollection creating...')
#     edge_collection = EdgeCollection(
#             name=edge_collection_name,
#             edgePopulation=Distribution(
#                 accessURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23'),
#             synapseRelease=synapse_release)
#     edge_collection = edge_collection.save()
#     pprint('EdgeCollection created: ' + edge_collection_name)
#
#
# node_collection_name = 'O1.v5 node collection'
# node_collection = NodeCollection.from_name(node_collection_name)
# if node_collection is None:
#     pprint('NodeCollection creating...')
#     node_collection = NodeCollection(
#             name=node_collection_name,
#             description=node_collection_name,
#             memodelRelease=memodel_release,
#             cellPlacement=cell_placement)
#     node_collection = node_collection.save()
#     pprint('NodeCollection created' + node_collection_name)
#
#
# target_name = 'O1.v5 target'
# target = Target.from_name(target_name)
# if target is None:
#     pprint('Target creating...')
#     target = Target(name=target_name, distribution=Distribution(
#         accessURL='file:///gpfs/bbp.cscs.ch/project/proj1/circuits/SomatosensoryCxS1-v5.r0/'
#                   'O1/merged_circuit/default_user.target'))
#     target = target.save()
#     pprint('Target created: ' + target_name)
#
#
# circuit_name = 'O1.v5 detailed circuit'
# circuit = DetailedCircuit.from_name(circuit_name)
# if circuit is None:
#     pprint('DetailedCircuit creating...')
#     circuit = DetailedCircuit(
#             name=circuit_name,
#             description='O1.v5 created in 2014',
#             nodeCollection=node_collection,
#             edgeCollection=edge_collection,
#             target=target)
#     circuit = circuit.save()
#     pprint('DetailedCircuit created: ' + circuit_name)

# -------------------------------------------------------------------------------------------------

morphology_release = MorphologyRelease.from_name('2017 Morphology release')

if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name='2017 Morphology release',
        description='Morphology release used for the O1.V6 and S1.V6',
        distribution=Distribution(
            # FIXME
            # accessURL='file:///gpfs/bbp.cscs.ch/project/proj59/entities/morphologies/2017.10.31'),
            downloadURL='file:///gpfs/bbp.cscs.ch/project/proj59/entities/morphologies/2017.10.31',
            mediaType='application/neuroml'),
        morphologyIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/'
                        'proj59/entities/morphologies/2017.10.31/neurondb.dat',
            mediaType='text/plain'))
    morphology_release = morphology_release.save()
    pprint('MorphologyRelease created: 2017 Morphology release')


cell_placement_name = 'O1.V6a cell placement'
cell_placement = CellPlacement.from_name(cell_placement_name)
if cell_placement is None:
    pprint('CellPlacement creating...')
    cell_placement = CellPlacement(
            name=cell_placement_name,
            description=cell_placement_name + ' description',
            distribution=Distribution(
                downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/'
                            '20171212/circuit.mvd3',
                mediaType='application/mvd3'))
    cell_placement = cell_placement.save()
    pprint('CellPlacement created: ' + cell_placement_name)


emodel_release_name = 'O1.V6a emodel release'
emodel_release = EModelRelease.from_name(emodel_release_name)
if emodel_release is None:
    pprint('EModelRelease creating...')
    emodel_release = EModelRelease(
        name=emodel_release_name,
        description=emodel_release_name,
        distribution=Distribution(
            accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/home/vangeit/modelmanagement/'
                      'prod.20171103/mm_runs/run/1810912/output/emodels_hoc/'),
        emodelIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/proj38/singlecell/optimization/'
                        'releases/2c80837/final.json',
            mediaType='text/plain'))
    emodel_release = emodel_release.save()
    pprint('EModelRelease created: EModel release')


memodel_name = 'O1.V6a memodel release'
memodel_release = MEModelRelease.from_name(memodel_name)
if memodel_release is None:
    pprint('MEModelRelease creating...')
    memodel_release = MEModelRelease(
        name=memodel_name,
        description='MEModel Release description',
        morphologyRelease=morphology_release,
        emodelRelease=emodel_release,
        memodelIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/home/vangeit/modelmanagement/'
                        'prod.20171103/megate_runs/run/6c6d611/output_select/mecombo_emodel.tsv',
            mediaType='text/plain'))
    memodel_release = memodel_release.save()
    pprint('MEModelRelease created: MEModel Release')


synapse_release_name = 'O1.V6a synapse release'
synapse_release = SynapseRelease.from_name(synapse_release_name)
if synapse_release is None:
    pprint('SynapseRelease creating...')
    synapse_release = SynapseRelease(
            name=synapse_release_name,
            distribution=Distribution(
                downloadURL='https://bbpcode.epfl.ch/browse/code/sim/neurodamus/bbp/commit/'
                            '?id=035728dd3474970721399e1906270359b7fa9bb2',
                mediaType='text/plain'))
    synapse_release = synapse_release.save()
    pprint('SynapseRelease created: ' + synapse_release_name)


edge_collection_name = 'O1.V6a edge collection'
edge_collection = EdgeCollection.from_name(edge_collection_name)
if edge_collection is None:
    pprint('EdgeCollection creating...')
    edge_collection = EdgeCollection(
            name=edge_collection_name,
            edgePopulation=Distribution(
                accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/'
                          'ncsFunctionalAllRecipePathways'),
            synapseRelease=synapse_release)
    edge_collection = edge_collection.save()
    pprint('EdgeCollection created: ' + edge_collection_name)


node_collection_name = 'O1.V6a node collection'
node_collection = NodeCollection.from_name(node_collection_name)
if node_collection is None:
    pprint('NodeCollection creating...')
    node_collection = NodeCollection(
            name=node_collection_name,
            description=node_collection_name,
            memodelRelease=memodel_release,
            cellPlacement=cell_placement)
    node_collection = node_collection.save()
    pprint('NodeCollection created' + node_collection_name)


target_name = 'target'
target = Target.from_name(target_name)
if target is None:
    pprint('Target creating...')
    target = Target(name=target_name, distribution=Distribution(
        accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/'
                  'default_user.target'))
    target = target.save()
    pprint('Target created: ' + target_name)


circuit_name = 'O1.V6a detailed circuit'
circuit = DetailedCircuit.from_name(circuit_name)
if circuit is None:
    pprint('DetailedCircuit creating...')
    circuit = DetailedCircuit(
            name=circuit_name,
            description='O1.V6 microcircuit created in 2017',
            nodeCollection=node_collection,
            edgeCollection=edge_collection,
            target=target)
    circuit = circuit.save()
    pprint('DetailedCircuit created: ' + circuit_name)

# -------------------------------------------------------------------------------------------------

cell_placement_name = 'S1.V6a cell placement'
cell_placement = CellPlacement.from_name(cell_placement_name)
if cell_placement is None:
    pprint('CellPlacement creating...')
    cell_placement = CellPlacement(
            name=cell_placement_name,
            description=cell_placement_name + ' description',
            distribution=Distribution(
                downloadURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/'
                            'circuit.mvd3',
                mediaType='application/mvd3'))
    cell_placement = cell_placement.save()
    pprint('CellPlacement created: ' + cell_placement_name)


edge_collection_name = 'S1.V6a edge collection'
edge_collection = EdgeCollection.from_name(edge_collection_name)
if edge_collection is None:
    pprint('EdgeCollection creating...')
    edge_collection = EdgeCollection(
            name=edge_collection_name,
            description=edge_collection_name,
            edgePopulation=Distribution(
                accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/'
                          'ncsFunctionalAllRecipePathways'),
            synapseRelease=synapse_release)
    edge_collection = edge_collection.save()
    pprint('EdgeCollection created: ' + edge_collection_name)


node_collection_name = 'S1.V6a node collection'
node_collection = NodeCollection.from_name(node_collection_name)
if node_collection is None:
    pprint('NodeCollection creating...')
    node_collection = NodeCollection(
            name=node_collection_name,
            description=node_collection_name,
            memodelRelease=memodel_release,
            cellPlacement=cell_placement)
    node_collection = node_collection.save()
    pprint('NodeCollection created' + node_collection_name)


target_name = 'S1.V6a target'
target = Target.from_name(target_name)
if target is None:
    pprint('Target creating...')
    target = Target(name=target_name, distribution=Distribution(
        accessURL='file:///gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/20171206/'
                  'default_user.target'))
    target = target.save()
    pprint('Target created: ' + target_name)


circuit_name = 'S1.V6a detailed circuit'
circuit = DetailedCircuit.from_name(circuit_name)
if circuit is None:
    pprint('DetailedCircuit creating...')
    circuit = DetailedCircuit(
            name=circuit_name,
            description='S1.V6a microcircuit created in 2017',
            nodeCollection=node_collection,
            edgeCollection=edge_collection,
            target=target)
    circuit = circuit.save()
    pprint('DetailedCircuit created: ' + circuit_name)
