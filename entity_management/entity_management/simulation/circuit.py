'''Circuit related entities'''
from entity_management.util import attributes, AttrOf
from entity_management.settings import DATA_SIM, VERSION
from entity_management.base import (Entity, Release, ModelInstance, Distribution)
from entity_management.simulation.cell import MEModelRelease


@attributes({'distribution': AttrOf(Distribution)})
class CellPlacement(Entity):
    '''Cell placement'''
    base_url = DATA_SIM + '/cellplacement/' + VERSION


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'cellPlacement': AttrOf(CellPlacement)})
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)'''
    base_url = DATA_SIM + '/nodecollection/' + VERSION


@attributes({'distribution': AttrOf(Distribution)})
class SynapseRelease(Release):
    '''Edge collection represents circuit connectivity(synapses, projections)'''
    base_url = DATA_SIM + '/synapserelease/' + VERSION


@attributes({'property_': AttrOf(Distribution),
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)'''
    base_url = DATA_SIM + '/edgecollection/' + VERSION


@attributes({'distribution': AttrOf(Distribution)})
class Target(Entity):
    '''Targets'''
    base_url = DATA_SIM + '/target/' + VERSION


@attributes({'nodeCollection': AttrOf(NodeCollection),
             'edgeCollection': AttrOf(EdgeCollection),
             'target': AttrOf(Target, default=None)})
class DetailedCircuit(ModelInstance):
    '''Detailed circuit'''
    base_url = DATA_SIM + '/detailedcircuit/' + VERSION
