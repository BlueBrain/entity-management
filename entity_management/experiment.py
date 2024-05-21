# SPDX-License-Identifier: Apache-2.0

"""
Experimental morphologies entities

.. inheritance-diagram:: entity_management.experiment
   :top-classes: entity_management.experiment.PatchedCell
   :parts: 1
"""

from entity_management.base import BrainLocation, OntologyTerm, attributes
from entity_management.core import MultiDistributionEntity
from entity_management.util import AttrOf


@attributes(
    {
        "name": AttrOf(str),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "eType": AttrOf(OntologyTerm, default=None),
        "mType": AttrOf(OntologyTerm, default=None),
    }
)
class PatchedCell(MultiDistributionEntity):
    """Patched cell."""
