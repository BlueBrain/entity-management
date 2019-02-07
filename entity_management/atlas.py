'''
Atlas entities

.. inheritance-diagram:: entity_management.atlas
   :top-classes: entity_management.atlas.Entity
   :parts: 1
'''
from typing import List

from entity_management.base import (Identifiable, OntologyTerm, attributes,
                                    Distribution)
from entity_management.core import Activity
from entity_management.util import AttrOf
from entity_management.mixins import DistributionMixin


@attributes()
class Entity(DistributionMixin, Identifiable):
    '''Base class for experiment Enitities.'''
    _url_domain = 'experiment'


# @attributes({'name': AttrOf(str),
#              'species': AttrOf(OntologyTerm, default=None),
#              })
# class WholeBrainNisslExperiment(Entity):
#     '''Whole brain nissl experiment.'''


@attributes({
    'name': AttrOf(str),
    'distribution': AttrOf(List[Distribution]),
    'species': AttrOf(OntologyTerm, default=None),
})
class VoxelAtlas(Entity):
    '''Whole brain atlas with assigned properties per voxel.

    Args:
        name (str): Name for the atlas containing version info.
        distribution (List[Distribution]): Collection of density profiles per cell type.
        species (OntologyTerm): Species ontology term.
    '''


@attributes({
    'name': AttrOf(str),
    'distribution': AttrOf(Distribution),
    'species': AttrOf(OntologyTerm, default=None),
})
class CellAtlas(Entity):
    '''Whole brain cell atlas with assigned properties per cell.

    Args:
        name (str): Name for the atlas containing version info.
        distribution (Distribution): File containing positions of cells, types, optional
            orientations.
        species (OntologyTerm): Species ontology term.
    '''


@attributes({
    'used': AttrOf(VoxelAtlas),
    'algorithm': AttrOf(str),
    'generated': AttrOf(CellAtlas),
})
class CellPositioning(Activity):
    '''Generic cell positioning activity.

    Args:
        used (VoxelAtlas): Reference to the voxel atlas.
        algorithm (str): Positioning algorithm.
        generated (CellAtlas): Generated cell atlas reference.
    '''
