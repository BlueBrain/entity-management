'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.Entity
   :parts: 1
'''
from entity_management.base import Identifiable, BrainLocation, attributes
from entity_management.util import AttrOf
from entity_management.mixins import DistributionMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for morphology Enitities.'''
    _type_namespace = 'nsg'
    _url_domain = 'morphology'


@attributes({'name': AttrOf(str),
             'brainLocation': AttrOf(BrainLocation)})
class ReconstructedCell(Entity):
    '''Reconstructed cell.

    Args:
        name(str): Name of the reconstructed cell.
    '''
    _url_version = 'v0.1.2'


@attributes({'name': AttrOf(str)})
class ReconstructedPatchedCell(Entity):
    '''Reconstructed patched cell.

    Args:
        name(str): Name of the reconstructed patched cell.
    '''
    _url_version = 'v0.1.1'


@attributes()
class ReconstructedWholeBrainCell(ReconstructedPatchedCell):
    '''Reconstructed wholeBrain cell.'''
    _url_version = 'v0.1.1'
