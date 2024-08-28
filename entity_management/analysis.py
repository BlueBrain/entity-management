# SPDX-License-Identifier: Apache-2.0

"""Analysis related entities."""

from typing import List

from entity_management.base import BlankNode, Derivation, Identifiable, attributes
from entity_management.core import Agent, Entity
from entity_management.util import AttrOf
from entity_management.workflow import BbpWorkflowActivity


@attributes(
    {
        "wasAssociatedWith": AttrOf(Identifiable, default=None),
    }
)
class AnalysisReportGenerationActivity(BlankNode):
    """AnalysisReportGenerationActivity."""

    def __attrs_post_init__(self):
        self._force_attr("_type", "Activity")


@attributes(
    {
        "activity": AttrOf(AnalysisReportGenerationActivity),
    }
)
class AnalysisReportGeneration(BlankNode):
    """AnalysisReportGeneration."""

    def __attrs_post_init__(self):
        self._force_attr("_type", "Generation")


@attributes()
class MultiCumulativeSimulationCampaignAnalysis(BbpWorkflowActivity):
    """Activity generating multiple analyses of a Simulation Campaign."""


@attributes()
class MultiEModelAnalysis(BbpWorkflowActivity):
    """Activity generating multiple analyses of an EModel."""


@attributes(
    {
        "name": AttrOf(str, default=None),
        "description": AttrOf(str, default=None),
        "codeRepository": AttrOf(str, default=None),
        "subdirectory": AttrOf(str, default=None),
        "command": AttrOf(str, default=None),
    }
)
class AnalysisSoftwareSourceCode(Agent):
    """AnalysisSoftwareSourceCode."""


@attributes(
    {
        "derivation": AttrOf(Derivation),
        "categories": AttrOf(List[str], default=None),
        "types": AttrOf(List[str], default=None),
    }
)
class AnalysisReport(Entity):
    """AnalysisReport."""


@attributes(
    {
        "derivation": AttrOf(Derivation),
        "categories": AttrOf(List[str], default=None),
        "types": AttrOf(List[str], default=None),
        "hasPart": AttrOf(List[AnalysisReport], default=None),
        "index": AttrOf(int, default=None),
        "generation": AttrOf(List[AnalysisReportGeneration], default=None),
    }
)
class CumulativeAnalysisReport(Entity):
    """CumulativeAnalysisReport."""


@attributes(
    {
        "hasPart": AttrOf(List[CumulativeAnalysisReport], default=None),
    }
)
class MultiCumulativeAnalysisReport(Entity):
    """MultiCumulativeAnalysisReport."""
