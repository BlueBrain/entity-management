'''
Provenance entities

.. inheritance-diagram:: entity_management.core
   :top-classes: entity_management.core.Entity
   :parts: 1
'''
from datetime import datetime

import attr

from entity_management import nexus
from entity_management.base import Identifiable
from entity_management.util import attributes, AttrOf
from entity_management.settings import JSLD_ID, JSLD_REV, CORE_ORG
from entity_management.mixins import DistributionMixin


@attributes({'name': AttrOf(str)})
class Entity(DistributionMixin, Identifiable):
    '''Base class for core Enitities. No provenance data is attached to the core entities with
    publish/deprecate.'''

    _type_namespace = 'nsg'
    _url_domain = 'core'
    # in hbp we don't have access to neurosciencegraph only to brainsimulation, so allow
    # overriding the in which org core instances will be located
    _url_org = CORE_ORG

    def __attrs_post_init__(self):
        super(Entity, self).__attrs_post_init__()
        self._type.append('prov:%s' % type(self).__name__)

    def publish(self, use_auth=None):
        '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes.

        Args:
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if hasattr(self, '_id') and self._id:
            js = nexus.update(self._id, self._rev, self.as_json_ld(), token=use_auth)
        else:
            js = nexus.create(self._base_url, self.as_json_ld(), token=use_auth)
        return self.evolve(_id=js[JSLD_ID], _rev=js[JSLD_REV])

    def deprecate(self, use_auth=None):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.

        Args:
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        js = nexus.deprecate(self._id, self._rev, token=use_auth)
        return self.evolve(_rev=js[JSLD_REV], _deprecated=True)


class Agent(Entity):
    '''Agent

    Args:
        name(str): Name of the agent.
    '''
    pass


@attributes({'email': AttrOf(str),
             'name': AttrOf(str, default=None),
             'givenName': AttrOf(str, default=None),
             'familyName': AttrOf(str, default=None)})
class Person(Agent):
    '''Person

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

        email = js['email']
        given_name = js['given_name']
        family_name = js['family_name']

        agents = Person.find_by(email=email, use_auth=use_auth)
        person = next(agents, None)
        if person is None:
            person = Person(email=email,
                            givenName=given_name,
                            familyName=family_name)
            person = person.publish(use_auth=use_auth)

        return person


@attributes({'version': AttrOf(str)})
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
class Activity(Entity):
    '''Base class for provenance activity.

    Args:
        name(str): Activity name.
        used(Identifiable): Entity used by this activity.
        generated(Identifiable): Entity generated by this activity.
        startedAtTime(datetime): Activity start time.
        wasStartedBy(Agent): Agent which started the activity.
    '''

    _url_version = 'v0.1.3'
    _vocab = 'http://schema.org/'

    def __attrs_post_init__(self):
        super(Activity, self).__attrs_post_init__()
        if self.startedAtTime is None:
            self._force_attr('startedAtTime', datetime.utcnow())


@attributes({'wasAttributedTo': AttrOf(Person, default=None),
             'dateCreated': AttrOf(datetime, default=None)})
@attr.s
class ProvenanceMixin(object):
    '''Enables provenance metadata when publishing/deprecating entities'''

    def publish(self, activity=None, use_auth=None):
        '''Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes. If ``use_auth`` token is provided user agent will be extracted
        from it and corresponding activity with ``createdBy`` field will be created.

        Args:
            activity(Activity): Provide custom activity to link with
                generated entity new revision otherwise default activity will be created.
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if activity is not None:
            assert isinstance(self, Activity)

        if hasattr(self, '_id') and self._id:
            js = nexus.update(self._id, self._rev, self.as_json_ld(), token=use_auth)
        else:
            self = self.evolve(wasAttributedTo=Person.get_current(use_auth),
                               dateCreated=datetime.utcnow())
            js = nexus.create(self._base_url, self.as_json_ld(), token=use_auth)
        entity_id = js[JSLD_ID]
        entity_revision = js[JSLD_REV]

        if activity is not None:
            activity = activity.evolve(generated=Identifiable.from_url(entity_id, use_auth),
                                       wasStartedBy=Person.get_current(use_auth))
            activity.publish(use_auth)

        return self.evolve(_id=entity_id, _rev=entity_revision)

    def deprecate(self, activity=None, use_auth=None):
        '''Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.

        Args:
            use_auth(str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        '''
        print(activity)
        js = nexus.deprecate(self._id, self._rev, token=use_auth)
        return self.evolve(_rev=js[JSLD_REV], _deprecated=True)
