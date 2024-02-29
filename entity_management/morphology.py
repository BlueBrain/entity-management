"""
Experimental morphologies entities

.. inheritance-diagram:: entity_management.morphology
   :top-classes: entity_management.morphology.ReconstructedCell
   :parts: 1
"""

from entity_management.base import BrainLocation, OntologyTerm, attributes
from entity_management.core import DataDownload, Entity
from entity_management.util import AttrOf


@attributes(
    {
        "distribution": AttrOf(list[DataDownload], default=None),
        "objectOfStudy": AttrOf(OntologyTerm, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
    }
)
class Morphology(Entity):
    """A Morphology."""


class NeuronMorphology(Morphology):
    """A Neuron Morphology."""


class SynthesizedNeuronMorphology(NeuronMorphology):
    """A synthesized neuron morphology."""


class ReconstructedNeuronMorphology(NeuronMorphology):
    """A reconstruced neuron morphology."""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload], default=None),
    }
)
class ReconstructedCell(Entity):
    """Reconstructed cell.

    Args:
        name(str): Name of the reconstructed cell.
    """


class ReconstructedPatchedCell(ReconstructedCell):
    """Reconstructed patched cell.

    Args:
        name(str): Name of the reconstructed patched cell.
    """


@attributes()
class ReconstructedWholeBrainCell(ReconstructedCell):
    """Reconstructed wholeBrain cell."""


@attributes(
    {
        "morphology": AttrOf(Entity),
        "distribution": AttrOf(list[DataDownload], default=None),
    }
)
class CutPlane(Entity):
    """Cut plane."""


@attributes(
    {
        "distribution": AttrOf(list[DataDownload], default=None),
    }
)
class LabeledCell(Entity):
    """Labeled cell."""
