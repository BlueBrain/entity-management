# SPDX-License-Identifier: Apache-2.0

"""
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.ReconstructedCell
   :parts: 1
"""

from entity_management.base import BrainLocation, OntologyTerm, attributes
from entity_management.core import Entity, MultiDistributionEntity
from entity_management.util import AttrOf


@attributes(
    {
        "objectOfStudy": AttrOf(OntologyTerm, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
    }
)
class Morphology(MultiDistributionEntity):
    """A Morphology."""


class NeuronMorphology(Morphology):
    """A Neuron Morphology."""


class SynthesizedNeuronMorphology(NeuronMorphology):
    """A synthesized neuron morphology."""


class ReconstructedNeuronMorphology(NeuronMorphology):
    """A reconstruced neuron morphology."""


class ReconstructedCell(MultiDistributionEntity):
    """Reconstructed cell.

    Args:
        name(str): Name of the reconstructed cell.
    """


class ReconstructedPatchedCell(ReconstructedCell):
    """Reconstructed patched cell.

    Args:
        name(str): Name of the reconstructed patched cell.
    """


class ReconstructedWholeBrainCell(ReconstructedCell):
    """Reconstructed wholeBrain cell."""


@attributes(
    {
        "morphology": AttrOf(Entity),
    }
)
class CutPlane(MultiDistributionEntity):
    """Cut plane."""


class LabeledCell(MultiDistributionEntity):
    """Labeled cell."""
