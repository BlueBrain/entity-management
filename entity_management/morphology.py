'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.Entity
   :parts: 1
'''
from typing import List

from entity_management.base import Identifiable, BrainLocation, attributes, Distribution
from entity_management.util import AttrOf
from entity_management.mixins import DistributionMixin
from entity_management.core import ProvenanceMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for morphology Enitities.'''
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
class ReconstructedPatchedCell(ReconstructedCell):
    '''Reconstructed patched cell.

    Args:
        name(str): Name of the reconstructed patched cell.
    '''
    _url_version = 'v0.1.1'


@attributes()
class ReconstructedWholeBrainCell(ReconstructedCell):
    '''Reconstructed wholeBrain cell.'''
    _url_version = 'v0.1.1'


@attributes({'morphology': AttrOf(Entity),
             'distribution': AttrOf(List[Distribution])})
class CutPlane(Entity, ProvenanceMixin):
    '''Reconstructed wholeBrain cell.'''
    _url_version = 'v0.1.2'
