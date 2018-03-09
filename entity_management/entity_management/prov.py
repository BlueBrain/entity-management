'''Provenance entities'''
from entity_management.base import Entity, Identifiable
from entity_management.util import attributes, AttrOf


@attributes({
    'used': AttrOf(Entity),
    })
class Agent(Identifiable):
    '''Base abstract class for many things having `name` and `description`
    '''
    pass


@attributes({
    'used': AttrOf(Entity),
    'generated': AttrOf(Entity, default=None),
    'startedAtTime': AttrOf(Entity, default=None),
    'wasStartedBy': AttrOf(Agent, default=None),
    })
class Activity(Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''
    pass
