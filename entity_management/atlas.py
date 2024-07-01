# SPDX-License-Identifier: Apache-2.0

"""Atlas related entities."""

from typing import List

from entity_management.base import BrainLocation, Derivation, Identifiable, Subject, attributes
from entity_management.core import DataDownload, Entity
from entity_management.util import AttrOf


@attributes(
    {
        "label": AttrOf(str),
        "identifier": AttrOf(int),
        "notation": AttrOf(str),
    }
)
class AtlasBrainRegion(Identifiable):
    """Atlas Brain Region as defined by the brain model ontology."""

    @staticmethod
    def _ontology_location():
        """Return org and proj for ontologies."""
        return "neurosciencegraph", "datamodels"

    @classmethod
    def from_id(
        cls,
        resource_id,
        *,
        on_no_result=None,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
        cross_bucket=False,
        resolve_context=False,
        **kwargs,
    ):
        """
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. It will receive
                `resource_id` as a first argument.
            cross_bucket (bool):
                Use the resolvers instead of the resources endpoint. Default False.
            resolve_context (bool):
                Resolve ontological term curies using the resource's context. Default False.
            kwargs: Keyword arguments which will be forwarded to ``on_no_result`` function.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()

        return super().from_id(
            resource_id,
            on_no_result=on_no_result,
            cross_bucket=cross_bucket,
            resolve_context=resolve_context,
            base=base,
            proj=proj,
            org=org,
            use_auth=use_auth,
            **kwargs,
        )

    @classmethod
    def from_url(cls, url, *, resolve_context=False, base=None, org=None, proj=None, use_auth=None):
        """
        Load entity from url.

        Args:
            url (str): Full url to the entity in nexus. ``_self`` content is a valid full URL.
            resolve_context (bool):
                Resolve ontological term curies using the resource's context. Default False.
            use_auth (str): OAuth token in case access is restricted.
                token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()
        return super().from_url(
            url,
            resolve_context=resolve_context,
            base=base,
            org=org,
            proj=proj,
            use_auth=use_auth,
        )


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class BrainTemplateDataLayer(Entity):
    """Raster volume of the brain template."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class HemisphereAnnotationDataLayer(Entity):
    """Hemisphere annotation from Allen ccfv3 volume at 25 microns."""


@attributes(
    {
        "distribution": AttrOf(List[DataDownload]),
    }
)
class ParcellationOntology(Entity):
    """Raster volume of the brain template. This originaly comes from AIBS CCF (25µm)"""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class BrainParcellationDataLayer(Entity):
    """Brain region annotation as IDs, including the separation of cortical layers 2 and 3."""


@attributes(
    {
        "distribution": AttrOf(DataDownload, default=None),
    }
)
class AtlasSpatialReferenceSystem(Entity):
    """This spatial reference system describes the space used by Allen Institute.

    It is shared across CCFv1, CCFv2 and CCFv3 in world coordinates.
    It uses micrometer as a spatial unit."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class CellOrientationField(Entity):
    """Raster volume with cell orientation field as quaternions."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class PlacementHintsDataCatalog(Entity):
    """Placement hint volumes data catalog."""


@attributes(
    {
        "brainTemplateDataLayer": AttrOf(BrainTemplateDataLayer),
        "parcellationOntology": AttrOf(ParcellationOntology),
        "parcellationVolume": AttrOf(BrainParcellationDataLayer),
        "spatialReferenceSystem": AttrOf(AtlasSpatialReferenceSystem),
        "hemisphereVolume": AttrOf(HemisphereAnnotationDataLayer, default=None),
        "placementHintsDataCatalog": AttrOf(PlacementHintsDataCatalog, default=None),
        "cellOrientationField": AttrOf(CellOrientationField, default=None),
        "subject": AttrOf(Subject, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
    }
)
class AtlasRelease(Entity):
    """AtlasRelease resource representation."""


class BrainAtlasRelease(AtlasRelease):
    """BrainAtlasRelease resource representation."""


@attributes(
    {
        "atlasRelease": AttrOf(AtlasRelease, default=None),
        "about": AttrOf(List[str], default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "derivation": AttrOf(Derivation, default=None),
        "distribution": AttrOf(DataDownload),
        "subject": AttrOf(Subject, default=None),
    }
)
class CellCompositionSummary(Entity):
    """CellCompositionSummary"""


@attributes(
    {
        "about": AttrOf(List[str], default=None),
        "atlasRelease": AttrOf(AtlasRelease, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "derivation": AttrOf(Derivation, default=None),
        "distribution": AttrOf(DataDownload),
        "subject": AttrOf(Subject, default=None),
    }
)
class CellCompositionVolume(Entity):
    """CellCompositionVolume"""


@attributes(
    {
        "about": AttrOf(List[str], default=None),
        "atlasRelease": AttrOf(AtlasRelease),
        "atlasSpatialReferenceSystem": AttrOf(AtlasSpatialReferenceSystem, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "cellCompositionSummary": AttrOf(CellCompositionSummary),
        "cellCompositionVolume": AttrOf(CellCompositionVolume),
    }
)
class CellComposition(Entity):
    """CellComposition"""


@attributes(
    {
        "name": AttrOf(str),
        "atlasRelease": AttrOf(AtlasRelease, default=None),
        "brainLocation": AttrOf(BrainLocation),
        "distribution": AttrOf(DataDownload),
        "subject": AttrOf(Subject, default=None),
        "derivation": AttrOf(Derivation, default=None),
    }
)
class METypeDensity(Entity):
    """METypeDensity"""
