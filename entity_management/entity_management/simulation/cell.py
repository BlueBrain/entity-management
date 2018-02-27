'''Cell related entities'''
from entity_management.util import attributes, AttrOf
from entity_management.settings import DATA_SIM, VERSION
from entity_management.base import (Entity, Release, ModelInstance, Distribution)


@attributes({'distribution': AttrOf(Distribution)})
class ModelScript(Entity):
    '''Scripts attached to the model

    For :class:`SubCellularModel` (modelScript) is a `mod` file.

    For :class:`EModel` (modelScript) is a `hoc,neuroml` file.

    :param Distribution distribution: location of the model script
    '''
    base_url = DATA_SIM + '/modelscript/' + VERSION


@attributes({'modelScript': AttrOf(ModelScript)})
class SubCellularModel(ModelInstance):
    '''SubCellular model

    :param ModelScript modelScript: SubCellular model script such as mod file
    '''
    base_url = DATA_SIM + '/subcellularmodel/' + VERSION


@attributes({'distribution': AttrOf(Distribution),
             'emodelIndex': AttrOf(Distribution)})
class EModelRelease(Release):
    '''Electrical model release

    :param Distribution distribution: emodel release location
    :param Distribution emodelIndex: emodel release index file
    '''
    base_url = DATA_SIM + '/emodelrelease/' + VERSION


@attributes({'subCellularMechanism': AttrOf(SubCellularModel, default=None),
             'modelScript': AttrOf(ModelScript, default=None),
             'isPartOf': AttrOf(EModelRelease, default=None)})
class EModel(Entity):
    '''Electrical model

    :param SubCellularModel subCellularMechanism: SubCellular mechanism.
    :param ModelScript modelScript: Model script. Script defining neuron model, e.g. a hoc file,
                                    or a zip file containing multiple hoc files.
    :param EModelRelease isPartOf: The emodel release this emodel is part of.
    '''
    base_url = DATA_SIM + '/emodel/' + VERSION


@attributes({'distribution': AttrOf(Distribution),
             'morphologyIndex': AttrOf(Distribution, default=None)})
class MorphologyRelease(Release):
    '''Morphology release

    :param Distribution distribution: distribution
    :param Distribution morphologyIndex: morphology index
    '''
    base_url = DATA_SIM + '/morphologyrelease/' + VERSION


@attributes({'emodelRelease': AttrOf(EModelRelease),
             'morphologyRelease': AttrOf(MorphologyRelease),
             'memodelIndex': AttrOf(Distribution, default=None)})
class MEModelRelease(Release):
    '''MorphoElectrical model release

    :param EModelRelease emodelRelease: electrical model release
    :param MorphologyRelease morphologyRelease: morphology model release
    :param memodelIndex Distribution: optional morpho-electrical model index
    '''
    base_url = DATA_SIM + '/memodelrelease/' + VERSION
