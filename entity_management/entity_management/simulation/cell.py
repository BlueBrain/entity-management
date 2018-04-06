'''Cell related entities'''
import typing

from entity_management.util import attributes, AttrOf
from entity_management.base import Distribution
from entity_management.sim import ModelRelease, ModelInstance, ModelScript, ModelReleaseIndex


@attributes()
class SubCellularModelScript(ModelScript):
    '''Scripts attached to the model: ``mod`` file.

    Args:
        distribution(Distribution): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    pass


@attributes()
class EModelScript(ModelScript):
    '''Scripts attached to the model: ``hoc``, ``neuroml`` file.

    Args:
        distribution(Distribution): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    pass


@attributes({'distribution': AttrOf(Distribution)})
class SynapseRelease(ModelRelease):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(Distribution): Location of the synapse release/mod files.
    '''
    _url_version = 'v0.1.1'


@attributes({'modelScript': AttrOf(SubCellularModelScript),
             'isPartOf': AttrOf(SynapseRelease, default=None)})
class SubCellularModel(ModelInstance):
    '''SubCellular model

    Args:
        modelScript(SubCellularModelScript): SubCellular model script such as mod file
        isPartOf(SynapseRelease): The synapse release this model is part of.
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution),
             'emodelIndex': AttrOf(ModelReleaseIndex)})
class EModelRelease(ModelRelease):
    '''Electrical model release

    Args:
        distribution(Distribution): EModel release location provides a path to ``hoc`` files.
        emodelIndex(ModelReleaseIndex): EModel release index file.
    '''
    _url_version = 'v0.1.1'


@attributes({'subCellularMechanism': AttrOf(typing.List[SubCellularModel], default=None),
             'modelScript': AttrOf(EModelScript, default=None),
             'isPartOf': AttrOf(EModelRelease, default=None)})
class EModel(ModelInstance):
    '''Electrical model

    Args:
        subCellularMechanism(SubCellularModel): SubCellular mechanism.
        modelScript(EModelScript): Model script. Script defining neuron model, e.g. a ``hoc`` file,
            or a zip file containing multiple ``hoc`` files.
        isPartOf(EModelRelease): The emodel release this emodel is part of.
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution),
             'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class MorphologyRelease(ModelRelease):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    Args:
        distribution(Distribution): If morphology release is provided at the external
            location distribution should provide the path to locate it. It should contain

            * ``v1`` folder with morphologies in H5v1 format
            * ``ascii`` folder with morphologies in ASC format
            * ``annotations`` folder with morphology annotations used for placement

        morphologyIndex(ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None)})
class Morphology(ModelInstance):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution(Distribution): If morphology is stored at the external location distribution
            should provide the path to it.
        isPartOf(MorphologyRelease): Release this morphology is part of.
    '''
    _url_version = 'v0.1.1'


@attributes({'emodelRelease': AttrOf(EModelRelease),
             'morphologyRelease': AttrOf(MorphologyRelease),
             'memodelIndex': AttrOf(ModelReleaseIndex, default=None)})
class MEModelRelease(ModelRelease):
    '''MorphoElectrical model release

    Args:
        emodelRelease(EModelRelease): electrical model release
        morphologyRelease(MorphologyRelease): morphology model release
        memodelIndex(ModelReleaseIndex): optional morpho-electrical model index
    '''
    _url_version = 'v0.1.1'


@attributes({'eModel': AttrOf(EModel, default=None),
             'morphology': AttrOf(Morphology, default=None),
             'modelScript': AttrOf(EModelScript, default=None),
             'isPartOf': AttrOf(MEModelRelease, default=None)})
class MEModel(ModelInstance):
    '''Detailed Neuron model with morphology and electrical models.

    Args:
        eModel(EModel): Electrical model.
        morphology(Morphology): Neuron morphology.
        modelScript(EModelScript): Model script which instantiates neuron with specified morphology
            and electrical model. Expected to have single NEURON template with the first argument
            being the folder where neuron morphology is located. Template is responsible for
            loading that morphology from the folder specified in the first template argument.
        isPartOf(MEModelRelease): The memodel release this memodel is part of.
    '''
    _url_version = 'v0.1.1'
