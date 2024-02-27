"""
Provenance entities

.. inheritance-diagram:: entity_management.core
   :top-classes: entity_management.base.BlankNode,
    entity_management.base.Identifiable
   :parts: 1
"""

import os
import uuid
from datetime import datetime
from io import IOBase, StringIO
from pathlib import Path

import attr
from attr.validators import in_

from entity_management import nexus

# Subject used to be in this module. It is imported for backward compatibility
from entity_management.base import Subject  # noqa pylint: disable=unused-import
from entity_management.base import BlankNode, Identifiable, _NexusBySparqlIterator, attributes
from entity_management.settings import WORKFLOW
from entity_management.util import AttrOf, NotInstantiated, unquote_uri_path


@attributes(
    {
        "name": AttrOf(str, default=None),
        "license": AttrOf(Identifiable, default=None),
        "contentUrl": AttrOf(str, default=None),
        "url": AttrOf(str, default=None),
        "contentSize": AttrOf(dict, default=None),
        "digest": AttrOf(dict, default=None),
        "encodingFormat": AttrOf(str, default=None),
    }
)
class DataDownload(BlankNode):
    """External resource representations, this can be a file or a folder on gpfs.

    Args:
        name (str): The distribution name.
        license (Identifiable): A Link towards the distribution license.
        contentUrl (str): When followed this link leads to the actual data.
        url (str): When followed this link leads to a resource providing further description on
            how to download the attached data.
        contentSize (int): If known in advance size of the resource.
        digest (int): Hash/Checksum of the resource.
        encodingFormat (str): Type of the resource accessible by the contentUrl.

    either `downloadURL` for files or `accessURL` for folders must be provided"""

    _id = None

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if not self.contentUrl and not self.url:  # pylint: disable=no-member
            raise ValueError('"contentUrl" or "url" must be provided!')

    @classmethod
    def from_file(
        cls,
        file_like,
        name=None,
        resource_id=None,
        storage_id=None,
        content_type="application/octet-stream",
        base=None,
        org=None,
        proj=None,
        use_auth=None,
    ):
        """Create DataDownload object form file_like.

        Args:
            file_like (Union[str, Path, BytesIO]): Path to the file or BytesIO buffer with data.
            name (str): Optional name for the DataDownload name property. If not provided
                file name with extension from the `file_like` will be used.
            resource_id (str): Optional file resource identifier. If not provided will be
                generated by Nexus.
            storage_id (str): Optional identifier of the storage backend where the file will
                be stored. If not provided, the project's default storage is used.
            content_type (str): File content type for example: `text/plain`. Default value:
                `application/octet-stream`.
            use_auth (str): Optional OAuth token.
        """
        if isinstance(file_like, (str, Path)):
            file_path = Path(file_like)
            assert file_path.exists(), f'"{file_path}" does not exist!'
            file_name = name if name else file_path.name
            with file_path.open(mode="rb") as f:
                resp = nexus.upload_file(
                    file_name,
                    f,
                    content_type,
                    resource_id=resource_id,
                    storage_id=storage_id,
                    base=base,
                    org=org,
                    proj=proj,
                    token=use_auth,
                )
        else:
            assert isinstance(file_like, IOBase)
            file_name = name if name else str(uuid.uuid4())
            resp = nexus.upload_file(
                file_name,
                file_like,
                content_type,
                resource_id=resource_id,
                storage_id=storage_id,
                base=base,
                org=org,
                proj=proj,
                token=use_auth,
            )
        data = DataDownload(
            name=resp["_filename"],
            contentSize={"unitCode": "bytes", "value": resp["_bytes"]},
            digest={"algorithm": resp["_digest"]["_algorithm"], "value": resp["_digest"]["_value"]},
            encodingFormat=resp["_mediaType"],
            contentUrl=resp["_self"],
        )
        data._force_attr("_id", resp["@id"])
        return data

    @classmethod
    def link_file(
        cls,
        file_path,
        name=None,
        resource_id=None,
        storage_id=None,
        content_type=None,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
    ):
        """Move file to nexus managed folder in gpfs project and return created resource identifier.

        Args:
            file_path (str): Path to the file.
            name (str): Optional name for the DataDownload name property. If not provided
                file name with extension from the `file_path` will be used.
            resource_id (str): Optional file resource identifier. If not provided will be
                generated by Nexus.
            storage_id (str): Optional identifier of the storage backend where the file will
                be stored. If not provided, the project's default storage is used.
            content_type (str): File content type for example: `text/plain`.
            use_auth (str): Optional OAuth token.
        """
        file_name = name if name else os.path.basename(file_path)
        resp = nexus.link_file(
            file_name,
            file_path,
            content_type,
            resource_id=resource_id,
            storage_id=storage_id,
            base=base,
            org=org,
            proj=proj,
            token=use_auth,
        )
        data = DataDownload(
            name=resp["_filename"],
            contentSize={"unitCode": "bytes", "value": resp["_bytes"]},
            digest={"algorithm": resp["_digest"]["_algorithm"], "value": resp["_digest"]["_value"]},
            encodingFormat=resp["_mediaType"],
            contentUrl=resp["_self"],
        )
        data._force_attr("_id", resp["@id"])
        return data

    @classmethod
    def from_json_str(
        cls, json_str, resource_id=None, name=None, base=None, org=None, proj=None, use_auth=None
    ):
        """Create DataDownload object representing json form serialized dict in string.

        Args:
            json_str (str): Dict serialized as json string.
            resource_id (str): Optional file resource identifier. If not provided will be
                generated by Nexus.
            name (str): Optional name for the DataDownload name property. If not provided
                a uuid will be generated.
            use_auth (str): Optional OAuth token.
        """
        buff = StringIO(json_str)
        file_name = name or str(uuid.uuid4())
        resp = nexus.upload_file(
            file_name,
            buff,
            "application/json",
            resource_id=resource_id,
            base=base,
            org=org,
            proj=proj,
            token=use_auth,
        )
        data = DataDownload(
            contentSize={"unitCode": "bytes", "value": resp["_bytes"]},
            digest={"algorithm": resp["_digest"]["_algorithm"], "value": resp["_digest"]["_value"]},
            encodingFormat=resp["_mediaType"],
            contentUrl=resp["_self"],
        )
        data._force_attr("_id", resp["@id"])
        return data

    def download(self, path=None, file_name=None, use_auth=None):
        """Download ``contentUrl``.

        Args:
            path (str): Optional path where to save the file. If not provided current folder will
                be used.
            file_name (str): Optional file name.  If not provided, file name will be taken from
                the name stored in Nexus.
            use_auth (str): Optional OAuth token.
        """
        # pylint: disable=no-member
        assert self.contentUrl is not None, "No contentUrl!"

        if path is None:
            path = os.getcwd()
        return nexus.download_file(self.contentUrl, path, file_name, token=use_auth)

    def get_location(self, use_auth=None):
        """Get file location when applicable.

        For files located on the gpfs storage backend, this will give direct file URI.

        Args:
            use_auth (str): Optional OAuth token.
        """
        # pylint: disable=no-member
        assert self.contentUrl is not None, "No contentUrl!"
        return nexus.get_file_location(self.contentUrl, token=use_auth)

    def get_location_path(self, use_auth=None):
        """Get file path when applicable.

        For files located on the gpfs storage backend, this will give direct filesystem path.

        Args:
            use_auth (str): Optional OAuth token.
        """
        # pylint: disable=no-member
        assert self.contentUrl is not None, "No contentUrl!"
        return nexus.get_unquoted_uri_path(self.contentUrl, token=use_auth)

    def get_url_as_path(self):
        """Get url path when applicable."""
        # pylint: disable=no-member
        assert self.url is not None, "No url!"
        assert self.url.startswith("file://"), f"URL '{self.url}' is not a file URI."
        return unquote_uri_path(self.url)

    def as_dict(self, use_auth=None):
        """Get ``contentUrl`` as dict.

        Args:
            use_auth (str): Optional OAuth token.
        """
        # pylint: disable=no-member
        assert self.contentUrl is not None, "No contentUrl!"
        assert self.encodingFormat == "application/json", (
            "Wrong encodingFormat, " "expecting application/json!"
        )

        return nexus.file_as_dict(self.contentUrl, token=use_auth)

    def get_id(self):
        """Retrieve _id property."""
        return self._id


@attributes({"distribution": AttrOf(list[DataDownload], default=None)})
@attr.s
class DistributionMixin:
    """Provide `distribution` attribute.
    attach/download corresponding operations on the distribution.
    """


@attributes()
class Agent(Identifiable):
    """Agent.

    Args:
        name(str): Name of the agent.
    """


@attributes(
    {
        "email": AttrOf(str),
        "name": AttrOf(str, default=None),
        "givenName": AttrOf(str, default=None),
        "familyName": AttrOf(str, default=None),
    }
)
class Person(Agent):
    """Person.

    Args:
        email(str): Email.
        givenName(str): Given name.
        familyName(str): Family name.
    """


@attributes({"version": AttrOf(str)})
class SoftwareAgent(Agent):
    """Software agent

    Args:
        version(str): Version of the software used.
    """


@attributes(
    {
        "name": AttrOf(str, default=None),
        "status": AttrOf(
            str, default=None, validators=in_([None, "Pending", "Running", "Done", "Failed"])
        ),
        "used": AttrOf(Identifiable, default=None),
        "generated": AttrOf(Identifiable, default=None),
        "startedAtTime": AttrOf(datetime, default=None),
        "endedAtTime": AttrOf(datetime, default=None),
        "wasStartedBy": AttrOf(Identifiable, default=None),
        "wasInformedBy": AttrOf(Identifiable, default=None),
        "wasInfluencedBy": AttrOf(Identifiable, default=None),
    }
)
class Activity(Identifiable):
    """Base class for provenance activity.

    Args:
        name (str): Activity name.
        status (str): Status can be `None`, `Pending`, `Running`, `Done` or `Failed`.
        used (Identifiable): Entity used by this activity.
        generated (Identifiable): Entity generated by this activity.
        startedAtTime (datetime): Activity start time.
        endedAtTime (datetime): Activity end time.
        wasStartedBy (Identifiable): Entity/Agent which started/triggered the activity.
            https://www.w3.org/TR/prov-o/#wasStartedBy
        wasInformedBy (Identifiable): Activity which provided input for the current activity.
            https://www.w3.org/TR/prov-o/#wasInformedBy
        wasInfluencedBy (Identifiable): Entity/Agent/Activity which influenced the activity.
            https://www.w3.org/TR/prov-o/#wasInfluencedBy
    """

    def __attrs_post_init__(self):
        # only init for newly created entities
        attr_value = object.__getattribute__(self, "startedAtTime")
        if (
            attr_value is not NotInstantiated  # skip lazy loaded entities
            and self._id is None
            and self.startedAtTime is None  # pylint: disable=no-member
        ):
            self._force_attr("startedAtTime", datetime.utcnow())

    def publish(
        self,
        resource_id=None,
        sync_index=False,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
        include_rev=False,
        activity=None,
    ):
        """Create or update activity resource in nexus.

        Args:
            resource_id (str): Resource identifier.
            include_rev (bool): Whether to include _rev in the linked entities or not.
            activity (Activity): Optional activity which provided information to the current
                activity.

        Returns:
            New instance of the same class with revision updated.
        """
        if activity is not None and self.wasInformedBy is None:  # pylint: disable=no-member
            assert isinstance(activity, Activity)
            self = self.evolve(wasInformedBy=activity)  # pylint: disable=self-cls-assignment

        if self.wasInfluencedBy is None and WORKFLOW is not None:  # pylint: disable=no-member
            # in case running in the context of workflow execution activity
            workflow = WorkflowExecution.from_id(
                WORKFLOW, base=base, org=org, proj=proj, use_auth=use_auth
            )
            self = self.evolve(wasInfluencedBy=workflow)  # pylint: disable=self-cls-assignment

        return super().publish(
            resource_id=resource_id,
            sync_index=sync_index,
            base=base,
            org=org,
            proj=proj,
            use_auth=use_auth,
            include_rev=include_rev,
        )


@attributes(
    {
        "name": AttrOf(str),
        "module": AttrOf(str),
        "task": AttrOf(str),
        "version": AttrOf(str),
        "parameters": AttrOf(str, default=None),
        "configFileName": AttrOf(str, default=None),
        "output": AttrOf(str, default=None),
        "distribution": AttrOf(DataDownload, default=None),
    }
)
class WorkflowExecution(Activity):
    """Represents activity of a workflow execution.

    Args:
        name (str): The user friendly workflow execution entry point. By convention will contain
            full name of a luigi task which was executed.
        module (str): Python module which was used to launch the luigi task from.
        task (str): Luigi task which was launched for execution.
        version (str): Version of the workflow engine used to execute the workflow.
        parameters (str): Concatenated list of parameters provided on the command line
            when the workflow was launched.
        configFileName (str): Name of the config file if one was explicitly provided.
        output (str): Any string that workflow tasks want to deliver as output to the external
            agents.
        distribution (DataDownload): Zip file of the additional python modules and the configuration
            file used to launch the workflow.
    """


@attributes(
    {
        "agent": AttrOf(Agent),
    }
)
class Contribution(BlankNode):
    """Contribution"""


@attributes(
    {
        "name": AttrOf(str, default=None),
        "description": AttrOf(str, default=None),
        "wasAttributedTo": AttrOf(list[Agent], default=None),
        "wasGeneratedBy": AttrOf(Identifiable, default=None),
        "wasDerivedFrom": AttrOf(list[Identifiable], default=None),
        "dateCreated": AttrOf(datetime, default=None),
    }
)
class EntityMixin:
    """Enables provenance metadata when publishing/deprecating entities."""

    @classmethod
    def was_generated_by(cls, generated_by, **kwargs):
        """List all resources which were generated by specified resource.

        Args:
            generated_by: Resource activity that generated entities.

        Returns:
            Iterator through the generated resources.
        """

        # pylint: disable=consider-using-f-string
        query = """
            PREFIX nsg: <https://neuroshapes.org/>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?entity
            WHERE {{
                ?entity a                   nsg:{} ;
                        prov:wasGeneratedBy ?id .
                FILTER(strEnds(str(?id), "{}"))
            }}
        """.format(
            cls.__name__, generated_by.get_id()
        )

        return _NexusBySparqlIterator(cls, query, **kwargs)

    def publish(
        self,
        resource_id=None,
        sync_index=False,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
        activity=None,
        was_attributed_to=None,
        include_rev=False,
    ):
        """Create or update resource in nexus. Makes a remote call to nexus instance to persist
        resource attributes. If ``use_auth`` token is provided user agent will be extracted
        from it and corresponding activity with ``createdBy`` field will be created.

        Args:
            resource_id (str): Resource identifier.
            activity (Activity): Optionally provide activity which generated this resource.
                Otherwise, when running in the context of a bbp-workflow
                (NEXUS_WORKFLOW env variable is provided), ``activity`` default value will be
                workflow execution activity.
            was_attributed_to (Person): Provide person argument in order to add the Person to the
                set of attribution parameter ``self.wasAttributedTo``.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
            include_rev (bool): Whether to include _rev in the linked entities or not.

        Returns:
            New instance of the same class with revision updated.
        """
        if self.wasGeneratedBy is None and activity is None and WORKFLOW is not None:
            # in case running in the context of workflow execution activity
            activity = WorkflowExecution.from_id(
                WORKFLOW, base=base, org=org, proj=proj, use_auth=use_auth
            )

        if activity is not None:
            assert isinstance(activity, Activity)
            self = self.evolve(wasGeneratedBy=activity)  # pylint: disable=self-cls-assignment

        if was_attributed_to is not None:
            # pylint: disable=self-cls-assignment
            self = self.evolve(
                wasAttributedTo=(
                    self.wasAttributedTo + [was_attributed_to]
                    if self.wasAttributedTo
                    else [was_attributed_to]
                )
            )

        return Identifiable.publish(
            self,
            resource_id=resource_id,
            sync_index=sync_index,
            base=base,
            org=org,
            proj=proj,
            use_auth=use_auth,
            include_rev=include_rev,
        )


@attributes(
    {
        "distribution": AttrOf(DataDownload, default=None),
        "contribution": AttrOf(list[Contribution], default=None),
    }
)
class Entity(EntityMixin, Identifiable):
    """Generic class for core Entities."""


@attributes(
    {
        "model": AttrOf(Identifiable),
        "purpose": AttrOf(str, default=None, validators=in_([None, "sim", "viz"])),
        "modelBuildingSteps": AttrOf(int, default=None),
        "allocationPartition": AttrOf(str, default="prod"),
        "numberOfNodes": AttrOf(int, default=None),
        "nodeConstraint": AttrOf(str, default=None),
        "exclusiveNodeAllocation": AttrOf(bool, default=False),
        "allocationDuration": AttrOf(str, default=None),
        "qualityOfService": AttrOf(
            str, default="", validators=in_(["", "normal", "longjob", "bigjob", "jenkins"])
        ),
        "memoryAmount": AttrOf(str, default=None),
        "numberOfTasksPerNode": AttrOf(int, default=None),
    }
)
class ModelRuntimeParameters(EntityMixin, DistributionMixin, Identifiable):
    """Model runtime parameters.

    Args:
        model (Identifiable): Model reference to which the parameters apply.
        name (str): Name of the parameter collection.
        purpose (str): Purpose of the parameter set. For example parameters for simulation
            or visualization.
        modelBuildingSteps (int): Core neuron model building steps parameter if applicable.
    """

    # FIXME docs

    @classmethod
    def list_by_model(cls, model_resource_id, **kwargs):
        """List all instances belonging to the schema this type defines.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.

        Returns:
            New instance of the same class with changes applied.
        """

        # pylint: disable=consider-using-f-string
        query = (
            """
            PREFIX nsg: <https://neuroshapes.org/>
            SELECT ?entity
            WHERE {
                ?entity a         nsg:ModelRuntimeParameters ;
                        nsg:model <%s> .
            }
        """
            % model_resource_id
        )

        return _NexusBySparqlIterator(cls, query, **kwargs)
