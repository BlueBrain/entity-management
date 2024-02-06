"""
EModel related entities.
"""

from entity_management.atlas import AtlasRelease
from entity_management.base import BrainLocation, Frozen, Identifiable, OntologyTerm
from entity_management.core import DataDownload, Entity, attributes
from entity_management.electrophysiology import Trace
from entity_management.morphology import NeuronMorphology
from entity_management.util import AttrOf


@attributes(
    {
        "emodel": AttrOf(str),
        "etype": AttrOf(str),
        "iteration": AttrOf(str, default=None),
        "score": AttrOf(float, default=None),
        "seed": AttrOf(int, default=None),
        "objectOfStudy": AttrOf(OntologyTerm, default=None),
    }
)
class EModelPropertiesMixin:
    """Mixin for common EModel properties."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "uses": AttrOf(list[Trace]),
    }
)
class ExtractionTargetsConfiguration(EModelPropertiesMixin, Entity):
    """ExtractionTargetsConfiguration."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class EModelPipelineSettings(EModelPropertiesMixin, Entity):
    """EModelPipelineSettings."""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload]),
        "exposesParameter": AttrOf(dict, default=None),
        "modelId": AttrOf(str, default=None),
        "nmodlParameters": AttrOf(dict, default=None),
        "origin": AttrOf(str, default=None),
        "suffix": AttrOf(str, default=None),
    }
)
class SubCellularModelScript(Entity):
    """SubCellularModelScript,"""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "uses": AttrOf(list[NeuronMorphology | SubCellularModelScript], default=None),
    }
)
class EModelConfiguration(EModelPropertiesMixin, Entity):
    """EModelConfiguration."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "generates": AttrOf(list[Identifiable], default=None),
        "hasPart": AttrOf(
            list[ExtractionTargetsConfiguration | EModelPipelineSettings | EModelConfiguration],
            default=None,
        ),
        "state": AttrOf(str, default=None),
    }
)
class EModelWorkflow(EModelPropertiesMixin, Entity):
    """EModelWorkflow."""


@attributes({"followedWorkflow": AttrOf(EModelWorkflow)})
class FollowedWorkflowActivity(Frozen):
    """FollowedWorkflowActivity."""


@attributes({"activity": AttrOf(FollowedWorkflowActivity)})
class EModelGeneration(Frozen):
    """EModelGeneration."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "generation": AttrOf(EModelGeneration),
    }
)
class FitnessCalculatorConfiguration(EModelPropertiesMixin, Entity):
    """FitnessCalculatorConfiguration."""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload]),
        "generation": AttrOf(EModelGeneration),
    }
)
class EModelScript(EModelPropertiesMixin, Entity):
    """EModelScript"""


@attributes(
    {
        "about": AttrOf(str, default=None),
        "generation": AttrOf(EModelGeneration),
        "distribution": AttrOf(list[DataDownload]),
    }
)
class EModel(EModelPropertiesMixin, Entity):
    """EModel definition."""


@attributes(
    {
        "hasPart": AttrOf(list[EModel]),
        "brainLocation": AttrOf(BrainLocation),
        "distribution": AttrOf(DataDownload),
        "subject": AttrOf(dict, default=None),
    }
)
class EModelDataCatalog(Entity):
    """EModel Data Catalog."""


@attributes(
    {
        "eModelDataCatalog": AttrOf(EModelDataCatalog),
        "atlasRelease": AttrOf(AtlasRelease),
        "brainLocation": AttrOf(BrainLocation),
        "releaseDate": AttrOf(dict),
    }
)
class EModelRelease(Entity):
    """EModel Release."""
