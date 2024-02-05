from entity_management.atlas import AtlasRelease
from entity_management.base import BrainLocation, Frozen, Identifiable
from entity_management.core import Contribution, DataDownload, Entity, attributes, Subject
from entity_management.util import AttrOf


@attributes({
    "contribution": AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    "generates": AttrOf(list[Identifiable], default=None),
    "hasPart": AttrOf(list[Identifiable], default=None),
    "iteration": AttrOf(str),
    "name": AttrOf(str),
    "emodel": AttrOf(str),
    "etype": AttrOf(str),
})
class EModelWorkflow(Identifiable):
    """EModelWorkflow."""

@attributes({"followedWorkflow": AttrOf(EModelWorkflow)})
class FollowedWorkflowActivity(Frozen):
    """FollowedWorkflowActivity."""


@attributes({"activity": AttrOf(FollowedWorkflowActivity)})
class EModelGeneration(Frozen):
    """EModelGeneration."""


@attributes({
    "contribution": AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    "generation": AttrOf(EModelGeneration),
    "emodel": AttrOf(str),
    "etype": AttrOf(str),
    "iteration": AttrOf(str),
    "name": AttrOf(str),
    "objectOfStudy": AttrOf(dict),
})
class FitnessCalculatorConfiguration(Entity):
    """FitnessCalculatorConfiguration."""


class Trace(Entity):
    pass


@attributes({
    "contribution": AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    "generation": AttrOf(EModelGeneration),
    "uses": AttrOf(list[Identifiable]),
    "emodel": AttrOf(str),
    "etype": AttrOf(str),
    "iteration": AttrOf(str),
    "objectOfStudy": AttrOf(dict),
})
class ExtractionTargetsConfiguration(Entity):
    """ExtractionTargetsConfiguration."""


@attributes({
    "contribution": AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    "uses": AttrOf(list[Identifiable]),
    "emodel": AttrOf(str),
    "etype": AttrOf(str),
    "iteration": AttrOf(str),
    "objectOfStudy": AttrOf(dict),
})
class EModelPipelineSettings(Entity):
    """EModelPipelineSettings."""


class SubCellularModelScript(Entity):
    """SubCellularModelScript,"""


class NeuronMorphology(Entity):
    """NeuronMorphology"""


@attributes({
    "contribution": AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    "emodel": AttrOf(str),
    "etype": AttrOf(str),
    "iteration": AttrOf(str),
    "name": AttrOf(str),
    "uses": AttrOf(list[Identifiable]),
})
class EModelConfiguration(Entity):
    """EModelConfiguration."""


class EModelScript(Entity):
    """EModelScript"""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload]),
        "generation": AttrOf(EModelGeneration),
        "contribution": AttrOf(Contribution, default=None),
        "emodel": AttrOf(str),
        "etype": AttrOf(str),
        "iteration": AttrOf(str),
        "score": AttrOf(float),
        "seed": AttrOf(int),
        "name": AttrOf(str),
        "about": AttrOf(str, default=None),
    }
)
class EModel(Identifiable):
    """EModel definition."""


@attributes(
    {
        "hasPart": AttrOf(list[EModel]),
        "brainLocation": AttrOf(BrainLocation),
        "contribution": AttrOf(Contribution, default=None),
        "distribution": AttrOf(DataDownload),
        "hasPart": AttrOf(list[EModel]),
        "subject": AttrOf(dict, default=None),
    }
)
class EModelDataCatalog(Entity):
    pass


@attributes(
    {
        "eModelDataCatalog": AttrOf(EModelDataCatalog),
        "atlasRelease": AttrOf(AtlasRelease),
        "brainLocation": AttrOf(BrainLocation),
        "contribution": AttrOf(Contribution, default=None),
        "releaseDate": AttrOf(dict),
    }
)
class EModelRelease(Entity):
    pass
