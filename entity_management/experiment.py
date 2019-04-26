'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.experiment
   :top-classes: entity_management.experiment.PatchedCell
   :parts: 1
'''
from entity_management.base import Identifiable, OntologyTerm, BrainLocation, attributes
from entity_management.util import AttrOf
from entity_management.core import DistributionMixin


@attributes()
class _Entity(DistributionMixin, Identifiable):
    '''Base class for experiment Enitities.'''


@attributes({'name': AttrOf(str),
             'brainLocation': AttrOf(BrainLocation, default=None),
             'eType': AttrOf(OntologyTerm, default=None),
             'mType': AttrOf(OntologyTerm, default=None)})
class PatchedCell(_Entity):
    '''Patched cell.'''
