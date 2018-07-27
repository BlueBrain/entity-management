'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.electrophysiology
   :top-classes: entity_management.electrophysiology.Entity
   :parts: 1
'''
from datetime import datetime

from entity_management.base import Frozen, Identifiable, OntologyTerm
from entity_management.util import attributes, AttrOf
from entity_management.mixins import DistributionMixin
from entity_management.core import Activity
from entity_management.experiment import PatchedCell


@attributes()
class Entity(Identifiable):
    '''Base class for electrophysiology Enitities'''
    _type_namespace = 'nsg'
    _url_domain = 'electrophysiology'


@attributes({'stimulusType': AttrOf(OntologyTerm)})
class StimulusType(Frozen):
    '''StimulusExperiment

    Args:
        stimulusType(OntologyTerm): Stimulus type ontology term.
    '''
    pass


@attributes({'stimulus': AttrOf(StimulusType),
             'used': AttrOf(PatchedCell)})
class StimulusExperiment(Activity):
    '''StimulusExperiment

    Args:
        stimulus(OntologyTerm): doc.
        used(PatchedCell): doc.
    '''
    pass


@attributes({'activity': AttrOf(StimulusExperiment),
             'sweep': AttrOf(int),
             'providerExperimentId': AttrOf(str, default=None),
             'providerExperimentName': AttrOf(str, default=None)})
class TraceGeneration(Entity):
    '''TraceGeneration

    Args:
        activity(StimulusExperiment): Points at stimulus experiment activity that generated trace.
        sweep(int): Sweep number of the trace.
        providerExperimentId(str): Points at stimulus experiment activity that generated trace.
        providerExperimentName(str): Laboratory name of the experiment.
    '''
    pass


@attributes({'channel': AttrOf(int),
             'qualifiedGeneration': AttrOf(TraceGeneration),
             'wasGeneratedBy': AttrOf(StimulusExperiment),
             'projectName': AttrOf(str, default=None),
             'retrievalDate': AttrOf(datetime, default=None)})
class Trace(DistributionMixin, Entity):
    '''Trace

    Args:
        projectName(str): Name of the project that the trace was recorded for.
        channel(int): Channel number of trace.
        retrievalDate(datetime): Retrieval date of binary.
        qualifiedGeneration(TraceGeneration): Qualified trace generation.
        wasGeneratedBy(StimulusExperiment): Stimulus experiment that generated trace.
    '''
    _url_version = 'v1.0.0'