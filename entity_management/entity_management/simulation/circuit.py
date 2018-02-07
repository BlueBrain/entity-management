'''Circuit related entities'''
import attr
from attr.validators import instance_of

from entity_management.settings import ENTITY_CTX, NSG_CTX, DATA_SIM, VERSION
from entity_management.base import (ModelInstance, Entity, Distribution,
                                    _merge, _attrs_pos, _attrs_kw)
from entity_management.simulation.cell import MEModelRelease


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class CellPlacement(Entity):
    '''Cell placement'''
    base_url = DATA_SIM + '/cellplacement/' + VERSION


@attr.s(these=_merge(
    {'memodelRelease': attr.ib(type=MEModelRelease, validator=instance_of(MEModelRelease)),
     'cellPlacement': attr.ib(type=CellPlacement, validator=instance_of(CellPlacement))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)'''
    base_url = DATA_SIM + '/nodecollection/' + VERSION


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class SynapseRelease(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)'''
    base_url = DATA_SIM + '/synapserelease/' + VERSION


@attr.s(these=_merge(
    {'property_': attr.ib(type=Distribution, validator=instance_of(Distribution)),
     'synapseRelease': attr.ib(type=SynapseRelease, validator=instance_of(SynapseRelease))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)'''
    base_url = DATA_SIM + '/edgecollection/' + VERSION


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class Target(Entity):
    '''Targets'''
    base_url = DATA_SIM + '/target/' + VERSION


@attr.s(these=_merge(
    {'nodeCollection': attr.ib(type=NodeCollection, validator=instance_of(NodeCollection)),
     'edgeCollection': attr.ib(type=EdgeCollection, validator=instance_of(EdgeCollection)),
     'target': attr.ib(type=Target, validator=instance_of(Target))},
    _attrs_pos(ModelInstance),
    _attrs_kw(ModelInstance)))
class DetailedCircuit(ModelInstance):
    '''Detailed circuit'''
    base_url = DATA_SIM + '/detailedcircuit/' + VERSION

    def as_json_ld(self):
        json_ld = {}
        json_ld['@context'] = [ENTITY_CTX, NSG_CTX,
                                {
                                    'accessURL': {'@id': 'schema:accessURL', '@type': '@id'},
                                    'downloadURL': {'@id': 'schema:downloadURL', '@type': '@id'},
                                    'distribution': {'@id': 'schema:distribution', '@type': '@id'},
                                    'mediaType': {'@id': 'schema:mediaType'},
                                }]
        json_ld['@type'] = self.types # pylint: disable=no-member
        json_ld['nodeCollection'] = {
                '@type': self.nodeCollection.types, # pylint: disable=no-member
                '@id': self.nodeCollection.uuid} # pylint: disable=no-member
        json_ld['edgeCollection'] = {
                '@type': self.edgeCollection.types, # pylint: disable=no-member
                '@id': self.edgeCollection.uuid} # pylint: disable=no-member
        json_ld['target'] = {
                '@type': self.target.types, # pylint: disable=no-member
                '@id': self.target.uuid} # pylint: disable=no-member
        return json_ld
