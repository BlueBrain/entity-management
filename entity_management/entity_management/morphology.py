'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.Entity
   :parts: 2
'''
from entity_management.base import Distribution
from entity_management.base import Identifiable
from entity_management.util import attributes, AttrOf
from entity_management.mixins import DistributionMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for morphology Enitities'''
    _type_namespace = 'nsg'
    _url_domain = 'morphology'


@attributes({'name': AttrOf(str),
             'distribution': AttrOf(Distribution)})
class ReconstructedPatchedCell(Entity):
    '''ReconstructedPatchedCell

    Args:
        name(str): Name of the agent.
        distribution(Distribution): Attached morphology file.
    '''
    pass
