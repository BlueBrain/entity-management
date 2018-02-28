'''Cell related entities'''
from entity_management.util import attributes, AttrOf
from entity_management.settings import DATA_SIM, VERSION
from entity_management.base import (Entity, Release, ModelInstance, Distribution)


@attributes({'distribution': AttrOf(Distribution, default=None)})
class ModelScript(Entity):
    '''Scripts attached to the model:

    * For :class:`SubCellularModel` (modelScript) is a ``mod`` file.
    * For :class:`EModel` (modelScript) is a ``hoc``, ``neuroml`` file.

    Args:
        distribution(Distribution): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    base_url = DATA_SIM + '/modelscript/' + VERSION


@attributes({'modelScript': AttrOf(ModelScript)})
class SubCellularModel(ModelInstance):
    '''SubCellular model

    Args:
        modelScript(ModelScript): SubCellular model script such as mod file
    '''
    base_url = DATA_SIM + '/subcellularmodel/' + VERSION


@attributes({'distribution': AttrOf(Distribution)})
class SynapseRelease(Release):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(Distribution): Location of the synapse release/mod files.
    '''
    base_url = DATA_SIM + '/synapserelease/' + VERSION


@attributes({'distribution': AttrOf(Distribution),
             'emodelIndex': AttrOf(Distribution)})
class EModelRelease(Release):
    '''Electrical model release

    Args:
        distribution(Distribution): EModel release location provides a path to ``hoc`` files.
        emodelIndex(Distribution): EModel release index file.
    '''
    base_url = DATA_SIM + '/emodelrelease/' + VERSION


@attributes({'subCellularMechanism': AttrOf(SubCellularModel, default=None),
             'modelScript': AttrOf(ModelScript, default=None),
             'isPartOf': AttrOf(EModelRelease, default=None)})
class EModel(ModelInstance):
    '''Electrical model

    Args:
        subCellularMechanism(SubCellularModel): SubCellular mechanism.
        modelScript(ModelScript): Model script. Script defining neuron model, e.g. a ``hoc`` file,
            or a zip file containing multiple ``hoc`` files.
        isPartOf(EModelRelease): The emodel release this emodel is part of.
    '''
    base_url = DATA_SIM + '/emodel/' + VERSION


@attributes({'distribution': AttrOf(Distribution),
             'morphologyIndex': AttrOf(Distribution, default=None)})
class MorphologyRelease(Release):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    Args:
        distribution(Distribution): If morphology release is provided at the external
            location distribution should provide the path to locate it. It should contain

            * ``v1`` folder with morphologies in H5v1 format
            * ``ascii`` folder with morphologies in ASC format
            * ``annotations`` folder with morphology annotations used for placement

        morphologyIndex(Distribution): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''
    base_url = DATA_SIM + '/morphologyrelease/' + VERSION


@attributes({'distribution': AttrOf(Distribution, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None)})
class Morphology(Entity):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution(Distribution): If morphology is stored at the external location distribution
            should provide the path to it.
        isPartOf(MorphologyRelease): Release this morphology is part of.
    '''
    base_url = DATA_SIM + '/morphology/' + VERSION


@attributes({'eModel': AttrOf(EModel, default=None),
             'morphology': AttrOf(Morphology, default=None),
             'modelScript': AttrOf(ModelScript, default=None)})
class MEModel(ModelInstance):
    '''Detailed Neuron model with morphology and electrical models.

    Args:
        eModel(EModel): Electrical model.
        morphology(Morphology): Neuron morphology.
        modelScript(ModelScript): Model script which instantiates neuron with specified morphology
            and electrical model.
    '''
    base_url = DATA_SIM + '/memodel/' + VERSION


@attributes({'emodelRelease': AttrOf(EModelRelease),
             'morphologyRelease': AttrOf(MorphologyRelease),
             'memodelIndex': AttrOf(Distribution, default=None)})
class MEModelRelease(Release):
    '''MorphoElectrical model release

    Args:
        emodelRelease(EModelRelease): electrical model release
        morphologyRelease(MorphologyRelease): morphology model release
        memodelIndex(Distribution): optional morpho-electrical model index
    '''
    base_url = DATA_SIM + '/memodelrelease/' + VERSION
