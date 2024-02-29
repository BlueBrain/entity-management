"""
Experimental morphologies entities

.. inheritance-diagram:: entity_management.experiment
   :top-classes: entity_management.experiment.PatchedCell
   :parts: 1
"""

from entity_management.base import BrainLocation, OntologyTerm, attributes
from entity_management.core import DataDownload, Entity
from entity_management.util import AttrOf


@attributes(
    {
        "name": AttrOf(str),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "eType": AttrOf(OntologyTerm, default=None),
        "mType": AttrOf(OntologyTerm, default=None),
        "distribution": AttrOf(list[DataDownload], default=None),
    }
)
class PatchedCell(Entity):
    """Patched cell."""
