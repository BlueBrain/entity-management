#!/usr/bin/env python
'''Upload data to nexus'''

from pprint import pprint

from entity_management.base import Distribution
from entity_management.simulation.cell import MorphologyRelease, EModelRelease, MEModelRelease
from entity_management.simulation.circuit import (NodeCollection, SynapseRelease, EdgeCollection,
                                                  CellPlacement, DetailedCircuit)

# dummyMorphologyRelease = MorphologyRelease(
#     name='test name',
#     description='test description',
#     distribution=[Distribution(
#         accessURL='file:///distribution',
#         mediaType='application/swc,application/neurolucida,application/h5,application/neuroml')],
#     morphologyIndex=Distribution(downloadURL='file:///morphology/index', mediaType='media type'))
#
# dummyEModelRelease = EModelRelease(
#     name='test name',
#     distribution=Distribution(downloadURL='url', contentSize=None),
#     emodelIndex=Distribution(downloadURL='url'))
#
# dummyMEModelRelease = MEModelRelease(
#         name='test name',
#         morphologyRelease=dummyMorphologyRelease,
#         emodelRelease=dummyEModelRelease,
#         memodelIndex=Distribution(downloadURL='url'))
#
#
# pprint(dummyMorphologyRelease.asdict())
# pprint(dummyEModelRelease.asdict())
# pprint(dummyMEModelRelease.asdict())
#
# morphology_release = MorphologyRelease.from_uuid('81d8dc48-9b46-44b4-847d-7b1b8270a262')
# morphology_release.deprecate()
# pprint(morphology_release)

update_morphology_release = False

morphology_release = MorphologyRelease.from_name('2012 Morphology release')
if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name='2012 Morphology release',
        description='Morphology release used for the O1.V5 microcircuit',
        distribution=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531',
            mediaType='application/swc,'
                      'application/neurolucida,'
                      'application/h5,'
                      'application/neuroml'),
        morphologyIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531/neuronDB.dat',
            mediaType='application/mvd3'))

    morphology_release.save()
    pprint('MorphologyRelease created: 2012 Morphology release')

elif update_morphology_release:
    pprint('MorphologyRelease updating...')
    new_distribution = morphology_release.distribution.evolve(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531',
            mediaType='application/swc,application/neurolucida,application/h5,application/neuroml')

    new_index = morphology_release.morphologyIndex.evolve(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531/neuronDB.dat',
            mediaType='application/mvd3')

    morphology_release = morphology_release.evolve(
            name='2012 Morphology release',
            description='Morphology release used for the O1.V5 microcircuit',
            distribution=new_distribution,
            morphologyIndex=new_index)
    morphology_release.save()
    pprint('MorphologyRelease updated: 2012 Morphology release')


morphology_release = MorphologyRelease.from_name('2017 Morphology release')
if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name='2017 Morphology release',
        description='Morphology release used for the O1.V6 and S1.V6',
        distribution=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/proj59/entities/morphologies/'
                        '2017.10.31',
            mediaType='application/swc,'
                      'application/neurolucida,'
                      'application/h5,'
                      'application/neuroml'),
        morphologyIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/'
                        'proj59/entities/morphologies/2017.10.31/neurondb.dat',
            mediaType='application/mvd3'))
    morphology_release.save()
    pprint('MorphologyRelease created: 2017 Morphology release')


update = False

emodel_name = 'EModel Release'
emodel_release = EModelRelease.from_name(emodel_name)
if emodel_release is None:
    pprint('EModelRelease creating...')
    emodel_release = EModelRelease(
        name=emodel_name,
        description='EModel Release description',
        distribution=Distribution(
            downloadURL='file:///Emodel/release/distribution',
            mediaType='application/swc,application/neurolucida,application/h5,'
                      'application/neuroml'),
        emodelIndex=Distribution(
            downloadURL='file:///emodelIndex',
            mediaType='application/swc,application/neurolucida,application/h5,'
                      'application/neuroml'))
    emodel_release.save()
    pprint('EModelRelease created: EModel release')

elif update:
    pprint('EModelRelease updating...')
    emodel_release = emodel_release.evolve(description='EModel Release description')
    emodel_release.save()
    pprint('EModelRelease updated')


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
            mediaType='application/swc,application/neurolucida,application/h5,'
                      'application/neuroml'))
    memodel_release.save()
    pprint('MEModelRelease created: MEModel Release')

elif update:
    pprint('MEModelRelease updating...')
    memodel_release = memodel_release.evolve(description='MEModel Release description')
    memodel_release.save()
    pprint('EModelRelease updated')


cell_placement_name = 'CellPlacement'
cell_placement = CellPlacement.from_name(cell_placement_name)
if cell_placement is None:
    pprint('CellPlacement creating...')
    cell_placement = CellPlacement(
            name=cell_placement_name,
            description='CellPlacement description',
            distribution=Distribution(
                downloadURL='file:///cell/placement/distribution',
                mediaType='application/swc,application/neurolucida,application/h5,'
                          'application/neuroml'))
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
            property_=Distribution(accessURL='file:///edge/collection'),
            synapseRelease=synapse_release)
    edge_collection = edge_collection.save()
    pprint('EdgeCollection created: ' + edge_collection_name)


# target_name = 'Target'
# target = Target.from_name(target_name)
# if target is None:
#     pprint('Target creating...')
#     target = Target(name=target_name, distribution=Distribution(downloadURL='file:///target'))
#     target = target.save()
#     pprint('Target created: ', target_name)


circuit_name = 'DetailedCircuit'
circuit = DetailedCircuit.from_name(circuit_name)
if circuit is None:
    pprint('DetailedCircuit creating...')
    circuit = DetailedCircuit(
            name=circuit_name,
            modelOf=None,
            nodeCollection=node_collection,
            edgeCollection=edge_collection)
            # target=target)
    circuit.save()
    pprint('DetailedCircuit created: ' + circuit_name)
