'''Provenance entities'''
from datetime import datetime

import entity_management.sim as sim
from entity_management.base import Identifiable
from entity_management.util import attributes, AttrOf


@attributes()
class Entity(Identifiable):
    '''Base abstract class for prov Enitities
    '''
    _url_org_domain = '/nexus/prov'
    _type_namespace = 'prov'


@attributes({
    'name': AttrOf(str),
    })
class Agent(Entity):
    '''Agent

    Args:
        name(str): Name of the agent.
    '''
    pass


@attributes({
    'used': AttrOf(sim.Entity),
    'generated': AttrOf(sim.Entity, default=None),
    'startedAtTime': AttrOf(datetime, default=None),
    'wasStartedBy': AttrOf(Agent, default=None),
    })
class Activity(Entity):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''

    def __attrs_post_init__(self):
        super(Activity, self).__attrs_post_init__()
        if self.startedAtTime is None:
            object.__setattr__(self, 'startedAtTime', datetime.utcnow().isoformat())
