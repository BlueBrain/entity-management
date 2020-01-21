'''
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.ReconstructedCell
   :parts: 1
'''
from entity_management.base import Identifiable, BrainLocation, attributes
from entity_management.util import AttrOf
from entity_management.core import EntityMixin, DistributionMixin, Entity


@attributes({'name': AttrOf(str),
             'brainLocation': AttrOf(BrainLocation)})
class ReconstructedCell(DistributionMixin, Identifiable, EntityMixin):
    '''Reconstructed cell.

    Args:
        name(str): Name of the reconstructed cell.
    '''


class ReconstructedPatchedCell(ReconstructedCell):
    '''Reconstructed patched cell.

    Args:
        name(str): Name of the reconstructed patched cell.
    '''


@attributes()
class ReconstructedWholeBrainCell(ReconstructedCell):
    '''Reconstructed wholeBrain cell.'''


@attributes({'morphology': AttrOf(Entity)})
class CutPlane(DistributionMixin, Identifiable, EntityMixin):
    '''Cut plane.'''


@attributes()
class LabeledCell(DistributionMixin, Identifiable, EntityMixin):
    '''Labeled cell.'''
