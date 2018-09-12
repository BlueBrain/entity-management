'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.experiment
   :top-classes: entity_management.experiment.Entity
   :parts: 1
'''
from entity_management.base import Identifiable, OntologyTerm, BrainLocation, attributes
from entity_management.util import AttrOf
from entity_management.mixins import DistributionMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for experiment Enitities.'''
    _type_namespace = 'nsg'
    _url_domain = 'experiment'


@attributes({'name': AttrOf(str),
             'brainLocation': AttrOf(BrainLocation, default=None),
             'eType': AttrOf(OntologyTerm, default=None),
             'mType': AttrOf(OntologyTerm, default=None)})
class PatchedCell(Entity):
    '''Patched cell.'''
    _url_version = 'v0.2.1'
