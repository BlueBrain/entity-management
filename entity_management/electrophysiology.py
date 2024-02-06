"""
Experimental morphologies entities

.. inheritance-diagram:: entity_management.electrophysiology
   :top-classes: entity_management.electrophysiology._Entity,
    entity_management.electrophysiology.StimulusType, entity_management.core.Activity
   :parts: 1
"""

from datetime import datetime

from entity_management.base import Frozen, Identifiable, OntologyTerm, QuantitativeValue, attributes
from entity_management.core import Activity, DistributionMixin
from entity_management.experiment import PatchedCell
from entity_management.util import AttrOf


@attributes()
class _Entity(Identifiable):
    """Base class for electrophysiology Enitities"""


@attributes({"stimulusType": AttrOf(OntologyTerm)})
class StimulusType(Frozen):
    """Stimulus type wrapper.

    Args:
        stimulusType(OntologyTerm): Stimulus type ontology term.
    """


@attributes({"stimulus": AttrOf(StimulusType), "used": AttrOf(PatchedCell)})
class StimulusExperiment(Activity):
    """Stimulus experiment.

    Args:
        stimulus(OntologyTerm): doc.
        used(PatchedCell): doc.
    """


@attributes(
    {
        "activity": AttrOf(StimulusExperiment),
        "sweep": AttrOf(int),
        "providerExperimentId": AttrOf(str, default=None),
        "providerExperimentName": AttrOf(str, default=None),
        "waveNumberRange": AttrOf(str, default=None),
        "targetHoldingPotential": AttrOf(QuantitativeValue, default=None),
    }
)
class TraceGeneration(_Entity):
    """Trace generation.

    Args:
        activity (StimulusExperiment): Points at stimulus experiment activity that generated trace.
        sweep (int): Sweep number of the trace.
        providerExperimentId (str): Points at stimulus experiment activity that generated trace.
        providerExperimentName (str): Laboratory name of the experiment.
        waveNumberRange (str): Python range expression into which sweep number should fall.
        targetHoldingPotential (QuantitativeValue): Target holding potential.
    """


@attributes(
    {
        "channel": AttrOf(int, default=None),
        "qualifiedGeneration": AttrOf(TraceGeneration, default=None),
        "wasGeneratedBy": AttrOf(StimulusExperiment, default=None),
        "projectName": AttrOf(str, default=None),
        "retrievalDate": AttrOf(datetime, default=None),
    }
)
class Trace(DistributionMixin, _Entity):
    """Trace.

    Args:
        projectName(str): Name of the project that the trace was recorded for.
        channel(int): Channel number of trace.
        retrievalDate(datetime): Retrieval date of binary.
        qualifiedGeneration(TraceGeneration): Qualified trace generation.
        wasGeneratedBy(StimulusExperiment): Stimulus experiment that generated trace.
    """
