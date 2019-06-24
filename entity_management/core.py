'''
Provenance entities

.. inheritance-diagram:: entity_management.core
   :top-classes: entity_management.base.BlankNode,
    entity_management.base.Identifiable
   :parts: 1
'''
import os
from datetime import datetime
from typing import List

import attr

from entity_management import nexus
from entity_management.base import Identifiable, BlankNode, OntologyTerm, attributes
from entity_management.util import AttrOf, NotInstantiated
from entity_management.settings import AGENT, JSLD_ID


@attributes({
    'name': AttrOf(str, default=None),
    'license': AttrOf(Identifiable, default=None),
    'contentUrl': AttrOf(str, default=None),
    'url': AttrOf(str, default=None),
    'contentSize': AttrOf(dict, default=None),
    'digest': AttrOf(dict, default=None),
    'encodingFormat': AttrOf(str, default=None),
})
class DataDownload(BlankNode):
    '''External resource representations,
    this can be a file or a folder on gpfs

    Args:
        name (str): The distribution name.
        license (Identifiable): A Link towards the distribution license.
        contentUrl (str): When followed this link leads to the actual data.
        url (str): When followed this link leads to a resource providing further description on
            how to download the attached data.
        contentSize (int): If known in advance size of the resource.
        digest (int): Hash/Checksum of the resource.
        encodingFormat (str): Type of the resource accessible by the contentUrl.

    either `downloadURL` for files or `accessURL` for folders must be provided'''

    _type = 'DataDownload'

    def __attrs_post_init__(self):
        if not self.contentUrl and not self.url:  # pylint: disable=no-member
            raise ValueError('"contentUrl" or "url" must be provided!')

    def download(self, path=None, file_name=None, use_auth=None):
        '''Download ``contentUrl``.

        Args:
            path(str): Absolute filename or path where to save the file.
                       If path is an existing folder, file name will be taken from
                       distribution originalFileName. Default is current folder.
            use_auth(str): Optional OAuth token.
        '''
        # pylint: disable=no-member
        assert self.contentUrl is not None, 'No contentUrl!'
        if path is None:
            path = os.getcwd()
        return nexus.download_file(self.contentUrl, path, file_name, token=use_auth)


@attributes({'distribution': AttrOf(List[DataDownload], default=None)})
@attr.s
class DistributionMixin(object):
    '''Provide `distribution` attribute.
    attach/download corresponding operations on the distribution.
    '''


@attributes()
class Agent(Identifiable):
    '''Agent.

    Args:
        name(str): Name of the agent.
    '''


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


@attributes({
    'version': AttrOf(str)
})
class SoftwareAgent(Agent):
    '''Software agent

    Args:
        version(str): Version of the software used.
    '''


@attributes({
    'name': AttrOf(str, default=None),
    'used': AttrOf(Identifiable, default=None),
    'generated': AttrOf(Identifiable, default=None),
    'startedAtTime': AttrOf(datetime, default=None),
    'endedAtTime': AttrOf(datetime, default=None),
    'wasStartedBy': AttrOf(Agent, default=None),
})
class Activity(Identifiable):
    '''Base class for provenance activity.

    Args:
        name (str): Activity name.
        used (Identifiable): Entity used by this activity.
        generated (Identifiable): Entity generated by this activity.
        startedAtTime (datetime): Activity start time.
        endedAtTime (datetime): Activity end time.
        wasStartedBy (Agent): Agent which started the activity.
    '''

    def __attrs_post_init__(self):
        # only init for newly created entities
        attr_value = object.__getattribute__(self, 'startedAtTime')
        if (attr_value is not NotInstantiated  # skip lazy loaded entities
                and self._id is None and self.startedAtTime is None):  # pylint: disable=no-member
            self._force_attr('startedAtTime', datetime.utcnow())


@attributes({
    'wasAttributedTo': AttrOf(List[Agent], default=None),
    'wasDerivedFrom': AttrOf(List[Identifiable], default=None),
    'dateCreated': AttrOf(datetime, default=None)
})
class ProvenanceMixin(object):
    '''Enables provenance metadata when publishing/deprecating entities'''

    def publish(self, resource_id=None, activity=None, person=None, use_auth=None):
        '''Create or update resource in nexus. Makes a remote call to nexus instance to persist
        resource attributes. If ``use_auth`` token is provided user agent will be extracted
        from it and corresponding activity with ``createdBy`` field will be created.

        Args:
            resource_id (str): Resource identifier.
            activity (Activity): Provide custom activity to link with
                generated resource new revision otherwise default activity will be created.
            person (Person): Provide person argument in order to set explicitly entity attribution
                parameter ``wasAttributedTo``. If runnning in the context of a workflow(when
                NEXUS_AGENT env variable is provided) resource will be attributted to the
                Workflow agent.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        Returns:
            New instance of the same class with revision updated.
        '''
        if activity is not None:
            assert isinstance(activity, Activity)

        if AGENT is not None:
            # in case running in the context of externally provided agent
            agent = Agent.from_id(AGENT)
        else:
            agent = person

        if self._self:
            js = nexus.update(self._self, self._rev, self.as_json_ld(), token=use_auth)
        else:
            if agent:
                self = self.evolve(wasAttributedTo=[agent])
            js = nexus.create(self._base_url, self.as_json_ld(), resource_id, token=use_auth)

        self._force_attr('_id', js.get(JSLD_ID))
        self._force_attr('_rev', js.get('_rev'))
        self._force_attr('_self', js.get('_self'))

        if activity is not None:
            activity = activity.evolve(generated=self, wasStartedBy=agent)
            activity.publish(use_auth)

        return self


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
})
class Entity(ProvenanceMixin, DistributionMixin, Identifiable):
    '''Generic class for core Entities.'''


@attributes({
    'name': AttrOf(str, default=None),
    'description': AttrOf(str, default=None),
    'version': AttrOf(str, default=None),
    'parameter': AttrOf(str, default=None),
    'configFile': AttrOf(DataDownload, default=None),
    'taskFile': AttrOf(DataDownload, default=None),
})
class WorkflowEngine(Activity):
    '''Workflow engine.

    Args:
        name (str): The distribution name.
        license (Identifiable): A Link towards the distribution license.
        contentUrl (str): When followed this link leads to the actual data.
    '''


@attributes({
    'name': AttrOf(str, default=None),
    'species': AttrOf(OntologyTerm, default=None),
    'strain': AttrOf(OntologyTerm, default=None),
})
class Subject(ProvenanceMixin, DistributionMixin, Identifiable):
    '''Subject.

    Args:
        name (str): Subject name.
        species (OntologyTerm): Species ontology term.
        strain (OntologyTerm): Strain ontology term.
    '''
