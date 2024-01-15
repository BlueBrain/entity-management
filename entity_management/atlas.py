"""Atlas related entities."""
import typing

from entity_management.base import Identifiable, attributes, BrainLocation
from entity_management.core import Entity, DataDownload, Contribution
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
        cls, resource_id, on_no_result=None, base=None, org=None, proj=None, use_auth=None,
        cross_bucket=False, **kwargs
    ):
        """
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. It will receive
                `resource_id` as a first argument.
            kwargs: Keyword arguments which will be forwarded to ``on_no_result`` function.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()

        return super(AtlasBrainRegion, cls).from_id(
            resource_id, on_no_result, base, proj, org, use_auth, **kwargs
        )

    @classmethod
    def from_url(cls, url, base=None, org=None, proj=None, use_auth=None):
        """
        Load entity from url.

        Args:
            url (str): Full url to the entity in nexus. ``_self`` content is a valid full URL.
            use_auth (str): OAuth token in case access is restricted.
                token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()
        return super(AtlasBrainRegion, cls).from_url(url, base, org, proj, use_auth)


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class BrainTemplateDataLayer(Entity):
    '''Raster volume of the brain template.'''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class HemisphereAnnotationDataLayer(Entity):
    '''Hemisphere annotation from Allen ccfv3 volume at 25 microns.'''


@attributes(
    {
        "distribution": AttrOf(typing.List[DataDownload]),
    }
)
class ParcellationOntology(Entity):
    '''Raster volume of the brain template. This originaly comes from AIBS CCF (25µm)'''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class BrainParcellationDataLayer(Entity):
    '''Brain region annotation as IDs, including the separation of cortical layers 2 and 3.'''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class AtlasSpatialReferenceSystem(Entity):
    '''This spatial reference system describes the space used by Allen Institute.

    It is shared across CCFv1, CCFv2 and CCFv3 in world coordinates.
    It uses micrometer as a spatial unit.'''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class PlacementHintsDataLayer(Entity):
    '''Placement hints volumes for all the cortical layers.'''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class CellOrientationField(Entity):
    '''Raster volume with cell orientation field as quaternions.'''


@attributes(
    {
        "brainTemplateDataLayer": AttrOf(BrainTemplateDataLayer),
        "parcellationOntology": AttrOf(ParcellationOntology),
        "parcellationVolume": AttrOf(BrainParcellationDataLayer),
        "spatialReferenceSystem": AttrOf(AtlasSpatialReferenceSystem),
        "hemisphereVolume": AttrOf(HemisphereAnnotationDataLayer, default=None),
        "placementHintsDataLayer": AttrOf(PlacementHintsDataLayer, default=None),
        "cellOrientationField": AttrOf(CellOrientationField, default=None),
        "subject": AttrOf(dict),
    }
)
class AtlasRelease(Entity):
    '''AtlasRelease resource representation.'''


@attributes({
    'atlasRelease': AttrOf(AtlasRelease, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'contribution': AttrOf(list[Contribution], default=None),
    "distribution": AttrOf(DataDownload),
    'subject': AttrOf(dict, default=None),
})
class CellCompositionSummary(Entity):
    """CellCompositionSummary"""


@attributes({
    'about': AttrOf(list[str], default=None),
    'atlasRelease': AttrOf(AtlasRelease, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'contribution': AttrOf(list[Contribution], default=None),
    "distribution": AttrOf(DataDownload),
    'subject': AttrOf(dict, default=None),
})
class CellCompositionVolume(Entity):
    """CellCompositionVolume"""


@attributes({
    'about': AttrOf(list[str], default=None),
    'atlasRelease': AttrOf(AtlasRelease),
    'atlasSpatialReferenceSystem': AttrOf(AtlasSpatialReferenceSystem, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'cellCompositionSummary': AttrOf(CellCompositionSummary),
    'cellCompositionVolume': AttrOf(CellCompositionVolume),
    'contribution': AttrOf(list[Contribution], default=None),
})
class CellComposition(Entity):
    """CellComposition"""
