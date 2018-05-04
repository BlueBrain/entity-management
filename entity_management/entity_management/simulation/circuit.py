'''Circuit related entities'''
from entity_management.util import attributes, AttrOf
from entity_management.base import Distribution
from entity_management.sim import Entity, ModelInstance, ModelReleaseIndex
from entity_management.simulation.cell import MEModelRelease, SynapseRelease


@attributes({'distribution': AttrOf(Distribution)})
class CircuitCellProperties(Entity):
    '''Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution(Distribution): Location of the cell placement file.
    '''
    pass


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'circuitCellProperties': AttrOf(CircuitCellProperties)})
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)

    Args:
        memodelRelease(MEModelRelease): MEModel release this node collection is using.
        circuitCellProperties(CircuitCellProperties): Cell properties which are used in this node
                                                      collection.
    '''
    _url_version = 'v0.1.1'


@attributes({'edgePopulation': AttrOf(ModelReleaseIndex), # FIXME make it work for now, check schema
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)

    Args:
        edgePopulation(Distribution): Distribution providing path to the collection of nrn
            files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution)})
class Target(Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution(Distribution): Location of the target file.
    '''
    pass


@attributes({'nodeCollection': AttrOf(NodeCollection),
             'edgeCollection': AttrOf(EdgeCollection),
             'target': AttrOf(Target, default=None)})
class DetailedCircuit(ModelInstance):
    '''Detailed circuit

    Args:
        nodeCollection(NodeCollection): Node collection.
        edgeCollection(EdgeCollection): Edge collection.
        target(Target): Target.
    '''
    _url_version = 'v0.1.1'
