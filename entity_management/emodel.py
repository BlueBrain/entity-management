"""
EModel related entities.
See https://bbpgitlab.epfl.ch/dke/apps/brain-modeling-ontology/-/tree/develop/shapes/
"""

from datetime import datetime

from entity_management.atlas import AtlasRelease
from entity_management.base import (
    BlankNode,
    BrainLocation,
    Frozen,
    Identifiable,
    OntologyTerm,
    Subject,
)
from entity_management.core import DataDownload, Entity, MultiDistributionEntity, attributes
from entity_management.electrophysiology import Trace
from entity_management.morphology import NeuronMorphology
from entity_management.util import AttrOf


@attributes(
    {
        "label": AttrOf(str),
        "prefLabel": AttrOf(str, default=None),
    }
)
class MTypeAnnotationBody(BlankNode):
    """MTypeAnnotationBody."""


@attributes(
    {
        "hasBody": AttrOf(MTypeAnnotationBody),
        "name": AttrOf(str, default=None),
    }
)
class MTypeAnnotation(BlankNode):
    """MTypeAnnotation."""


@attributes(
    {
        "label": AttrOf(str),
        "prefLabel": AttrOf(str, default=None),
    }
)
class ETypeAnnotationBody(BlankNode):
    """ETypeAnnotationBody."""


@attributes(
    {
        "hasBody": AttrOf(ETypeAnnotationBody),
        "name": AttrOf(str, default=None),
    }
)
class ETypeAnnotation(BlankNode):
    """ETypeAnnotation."""


@attributes(
    {
        "eModel": AttrOf(str),
        "eType": AttrOf(str),
        "mType": AttrOf(str, default=None),
        "iteration": AttrOf(str, default=None),
        "score": AttrOf(float, default=None),
        "seed": AttrOf(int, default=None),
        "objectOfStudy": AttrOf(OntologyTerm, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "atlasRelease": AttrOf(AtlasRelease, default=None),
        "subject": AttrOf(Subject, default=None),
        "annotation": AttrOf(list[MTypeAnnotation | ETypeAnnotation], default=None),
    }
)
class EModelEntity(MultiDistributionEntity):
    """EModel entity with common EModel properties."""


@attributes(
    {
        "uses": AttrOf(list[Trace]),
    }
)
class ExtractionTargetsConfiguration(EModelEntity):
    """ExtractionTargetsConfiguration."""


class EModelPipelineSettings(EModelEntity):
    """EModelPipelineSettings."""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload]),
        "exposesParameter": AttrOf(list[dict], default=None),
        "modelId": AttrOf(str, default=None),
        "nmodlParameters": AttrOf(dict, default=None),
        "origin": AttrOf(str, default=None),
        "suffix": AttrOf(str, default=None),
        "temperature": AttrOf(int | dict, default=None),
        "subject": AttrOf(Subject, default=None),
        "identifier": AttrOf(str, default=None),
        "mod": AttrOf(dict, default=None),
        "ion": AttrOf(list[OntologyTerm], default=None),
        "isLjpCorrected": AttrOf(bool, default=None),
        "objectOfStudy": AttrOf(OntologyTerm, default=None),
        "isTemperatureDependent": AttrOf(bool, default=None),
    }
)
class SubCellularModelScript(Entity):
    """SubCellularModelScript,"""


@attributes(
    {
        "uses": AttrOf(list[NeuronMorphology | SubCellularModelScript], default=None),
    }
)
class EModelConfiguration(EModelEntity):
    """EModelConfiguration."""


@attributes(
    {
        "generates": AttrOf(list[Identifiable], default=None),
        "hasPart": AttrOf(
            list[ExtractionTargetsConfiguration | EModelPipelineSettings | EModelConfiguration],
            default=None,
        ),
        "state": AttrOf(str, default=None),
    }
)
class EModelWorkflow(EModelEntity):
    """EModelWorkflow."""


@attributes({"followedWorkflow": AttrOf(EModelWorkflow)})
class FollowedWorkflowActivity(Frozen):
    """FollowedWorkflowActivity."""


@attributes({"activity": AttrOf(FollowedWorkflowActivity)})
class EModelGeneration(Frozen):
    """EModelGeneration."""


@attributes(
    {
        "generation": AttrOf(EModelGeneration),
    }
)
class FitnessCalculatorConfiguration(EModelEntity):
    """FitnessCalculatorConfiguration."""


@attributes(
    {
        "generation": AttrOf(EModelGeneration),
    }
)
class EModelScript(EModelEntity):
    """EModelScript"""


@attributes(
    {
        "about": AttrOf(str, default=None),
        "generation": AttrOf(EModelGeneration),
    }
)
class EModel(EModelEntity):
    """EModel definition."""


@attributes(
    {
        "hasPart": AttrOf(list[EModel]),
        "brainLocation": AttrOf(BrainLocation),
        "distribution": AttrOf(DataDownload),
        "subject": AttrOf(Subject, default=None),
    }
)
class EModelDataCatalog(Entity):
    """EModel Data Catalog."""


@attributes(
    {
        "eModelDataCatalog": AttrOf(EModelDataCatalog),
        "atlasRelease": AttrOf(AtlasRelease),
        "brainLocation": AttrOf(BrainLocation),
        "releaseDate": AttrOf(datetime),
    }
)
class EModelRelease(Entity):
    """EModel Release."""
