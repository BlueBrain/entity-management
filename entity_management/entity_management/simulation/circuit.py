'''Circuit related entities'''
from entity_management.util import attributes, AttrOf
from entity_management.base import (Entity, ModelInstance, Distribution)
from entity_management.simulation.cell import MEModelRelease, SynapseRelease


@attributes({'distribution': AttrOf(Distribution)})
class CellPlacement(Entity):
    '''Cell placement provides locationd of the MVD3 file with cell properties.

    Args
        distribution(Distribution): Location of the cell placement file.
    '''
    pass


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'cellPlacement': AttrOf(CellPlacement)})
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)

    Args:
        memodelRelease(MEModelRelease): MEModel release this node collection is using.
        cellPlacement(CellPlacement): Cell placement which is used in this node collection.
    '''
    pass


@attributes({'edgePopulation': AttrOf(Distribution),
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)

    Args
        edgePopulation(Distribution): Distribution providing path to the collection of nrn
        files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    '''
    pass


@attributes({'distribution': AttrOf(Distribution)})
class Target(Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args
        distribution(Distribution): Location of the target file.
    '''
    pass


@attributes({'nodeCollection': AttrOf(NodeCollection),
             'edgeCollection': AttrOf(EdgeCollection),
             'target': AttrOf(Target, default=None)})
class DetailedCircuit(ModelInstance):
    '''Detailed circuit

    Args
        nodeCollection(NodeCollection): Node collection.
        edgeCollection(EdgeCollection): Edge collection.
        target(Target): Target.
    '''
    pass
