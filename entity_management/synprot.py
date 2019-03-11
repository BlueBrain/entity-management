'''Synprot domain entities'''

from typing import List

from entity_management.base import (Distribution, Identifiable, attributes)
from entity_management.core import ProvenanceMixin
from entity_management.mixins import DistributionMixin
from entity_management.util import AttrOf


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(List[Distribution], default=None),
})
class Entity(ProvenanceMixin, DistributionMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
        wasDerivedFrom(List[Identifiable]): List of associated provenance entities.
    '''
    _url_domain = 'synprot'


@attributes({
    'reference': AttrOf(str),
})
class CellProteinConcExperiment(Entity):
    """Cell Protein Concontration Experiment

    Args:
        distribution: attached file
        reference: reference paper or source
    """
    _url_version = 'v0.1.5'


@attributes({
    'distribution': AttrOf(List[Distribution], default=None),
    'reference': AttrOf(str),
})
class SynapticProteinConcExperiment(Entity):
    """Synaptic Protein Concontration Experiment

    Args:
        distribution: attached file
        reference: reference paper or source
    """


@attributes({
    'distribution': AttrOf(List[Distribution], default=None),
    'reference': AttrOf(str),
})
class TranscriptomeExperiment(Entity):
    """Transcriptome Experiment

    Args:
        distribution: attached file
        reference: reference paper or source
    """


@attributes({
    'distribution': AttrOf(List[Distribution], default=None),
    'reference': AttrOf(str),
})
class MtypeTaxonomy(Entity):
    """Cell Mtype Taxonomy

    Args:
        distribution: attached file
        mtypeTaxonomyReference: reference paper or source
    """
