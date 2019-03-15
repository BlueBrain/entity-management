'''
Provenance entities

.. inheritance-diagram:: entity_management.core
   :top-classes: entity_management.core.Entity
   :parts: 1
'''
from datetime import datetime
from typing import List

import attr

from entity_management import nexus
from entity_management.base import Identifiable, attributes
from entity_management.util import AttrOf
from entity_management.settings import JSLD_ID, JSLD_REV, AGENT
from entity_management.mixins import DistributionMixin


@attributes()
class Agent(Identifiable):
    '''Agent.

    Args:
        name(str): Name of the agent.
    '''
    _url_domain = 'core'


@attributes({'email': AttrOf(str),
             'name': AttrOf(str, default=None),
             'givenName': AttrOf(str, default=None),
             'familyName': AttrOf(str, default=None)})
class Person(Agent):
    '''Person.

    Args:
        email(str): Email.
        givenName(str): Given name.
        familyName(str): Family name.
    '''
    _vocab = 'http://schema.org/'

    @classmethod
    def get_current(cls, use_auth=None):
        '''
        Get current person-agent. If doesn't exist creates one and returns it.

        Args:
            use_auth(str): OAuth token from which agent will be identified.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        js = nexus.get_current_agent(token=use_auth)

        if js is None:
            return None

        def publish_person():
            '''Create and publish a Person entity'''
            person = Person(email=js['email'],
                            givenName=js['given_name'],
                            familyName=js['family_name'])
            return person.publish(use_auth=use_auth)

        return Person.find_unique(email=js['email'],
                                  use_auth=use_auth,
                                  on_no_result=publish_person,
                                  poll_until_exists=True)


@attributes({
    'version': AttrOf(str)
})
class SoftwareAgent(Agent):
    '''Software agent

    Args:
        version(str): Version of the software used.
    '''
    pass


@attributes({
    'name': AttrOf(str, default=None),
    'used': AttrOf(Identifiable, default=None),
    'generated': AttrOf(Identifiable, default=None),
    'startedAtTime': AttrOf(datetime, default=None),
    'wasStartedBy': AttrOf(Agent, default=None),
})
class Activity(Identifiable):
    '''Base class for provenance activity.

    Args:
        name(str): Activity name.
        used(Identifiable): Entity used by this activity.
        generated(Identifiable): Entity generated by this activity.
        startedAtTime(datetime): Activity start time.
        wasStartedBy(Agent): Agent which started the activity.
    '''
    _url_domain = 'core'
    _url_version = 'v0.1.3'
    _vocab = 'http://schema.org/'

    def __attrs_post_init__(self):
        # only init for newly created entities
        if self.id is None and self.startedAtTime is None:  # pylint: disable=no-member
            self._force_attr('startedAtTime', datetime.utcnow())


@attributes({
    'wasAttributedTo': AttrOf(List[Agent], default=None),
    'wasDerivedFrom': AttrOf(List[Identifiable], default=None),
    'dateCreated': AttrOf(datetime, default=None)
})
class ProvenanceMixin(object):
    '''Enables provenance metadata when publishing/deprecating entities'''

    def publish(self, activity=None, person=None, use_auth=None):
        '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes. If ``use_auth`` token is provided user agent will be extracted
        from it and corresponding activity with ``createdBy`` field will be created.

        Args:
            activity(Activity): Provide custom activity to link with
                generated entity new revision otherwise default activity will be created.
            person(Person): Override the agent with person to link with, otherwise identity will
                be taken from the token if token is present or form env var AGENT.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if activity is not None:
            assert isinstance(activity, Activity)

        if AGENT is not None:
            # in case running in the context of externally provided agent
            agent = Agent.from_url(AGENT)
        elif person is None:
            agent = Person.get_current(use_auth)
        else:
            agent = person

        if self.id:
            js = nexus.update(self.id, self.meta.rev,
                              self.as_json_ld(), token=use_auth)
        else:
            self.meta.types = ['prov:Entity', self.get_type()]
            if self.wasAttributedTo:
                self = self.evolve(dateCreated=datetime.utcnow())
            else:
                self = self.evolve(wasAttributedTo=[agent], dateCreated=datetime.utcnow())
            js = nexus.create(
                self.base_url, self.as_json_ld(), token=use_auth)

        self = self.evolve(id=js[JSLD_ID], meta=attr.evolve(self.meta, rev=js[JSLD_REV]))

        if activity is not None:
            if agent and 'prov:Agent' not in agent.meta.types:  # fix v0 nexus activity schema bug
                agent.meta.types.append('prov:Agent')
            activity = activity.evolve(generated=self, wasStartedBy=agent)
            if activity.meta.types is None:
                activity.meta.types = ['prov:Activity', activity.get_type()]
            activity.publish(use_auth)

        return self


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
})
class Entity(ProvenanceMixin, DistributionMixin, Identifiable):
    '''Generic class for core Entities.'''
    _url_domain = 'core'
    _url_version = 'v1.0.0'


@attributes()
class Workflow(Agent, Entity):
    '''Workflow agent'''
    _url_name = 'entity'
    _type_name = 'Entity'
