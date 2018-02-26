'''Cell related entities'''
import attr
from attr.validators import instance_of

from entity_management.util import optional_of
from entity_management.settings import DATA_SIM, VERSION
from entity_management.base import (Entity, Release, ModelInstance, Distribution,
                                    _merge, _attrs_pos, _attrs_kw)


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class ModelScript(Entity):
    '''Scripts attached to the model

    For :class:`SubCellularModel` (modelScript) is a `mod` file.

    For :class:`EModel` (modelScript) is a `hoc,neuroml` file.

    :param Distribution distribution: location of the model script
    '''
    base_url = DATA_SIM + '/modelscript/' + VERSION


@attr.s(these=_merge(
    {'modelScript': attr.ib(type=ModelScript, validator=instance_of(ModelScript))},
    _attrs_pos(ModelInstance),
    _attrs_kw(ModelInstance)))
class SubCellularModel(ModelInstance):
    '''SubCellular model

    :param ModelScript modelScript: SubCellular model script such as mod file
    '''
    base_url = DATA_SIM + '/subcellularmodel/' + VERSION


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution)),
     'emodelIndex': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Release),
    _attrs_kw(Release)))
class EModelRelease(Release):
    '''Electrical model release

    :param Distribution distribution: emodel release location
    :param Distribution emodelIndex: emodel release index file
    '''
    base_url = DATA_SIM + '/emodelrelease/' + VERSION


@attr.s(these=_merge(
    _attrs_pos(Entity),
    {'subCellularMechanism': attr.ib(type=SubCellularModel,
                                     validator=optional_of(SubCellularModel),
                                     default=None),
     'modelScript': attr.ib(type=ModelScript, validator=optional_of(ModelScript), default=None),
     'isPartOf': attr.ib(type=EModelRelease, validator=optional_of(EModelRelease), default=None)},
    _attrs_kw(Entity)))
class EModel(Entity):
    '''Electrical model

    :param SubCellularModel subCellularMechanism: SubCellular mechanism.
    :param ModelScript modelScript: Model script. Script defining neuron model, e.g. a hoc file,
                                    or a zip file containing multiple hoc files.
    :param EModelRelease isPartOf: The emodel release this emodel is part of.
    '''
    base_url = DATA_SIM + '/emodel/' + VERSION


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=optional_of(Distribution))},
    _attrs_pos(Release),
    {'morphologyIndex': attr.ib(type=Distribution,
                                validator=optional_of(Distribution),
                                default=None)},
    _attrs_kw(Release)))
class MorphologyRelease(Release):
    '''Morphology release

    :param Distribution distribution: distribution
    :param Distribution morphologyIndex: morphology index
    '''
    base_url = DATA_SIM + '/morphologyrelease/' + VERSION


@attr.s(these=_merge(
    {'emodelRelease': attr.ib(type=EModelRelease, validator=instance_of(EModelRelease)),
     'morphologyRelease': attr.ib(type=MorphologyRelease,
                                  validator=instance_of(MorphologyRelease))},
    _attrs_pos(Release),
    {'memodelIndex': attr.ib(type=Distribution,
                             validator=optional_of(Distribution),
                             default=None)},
    _attrs_kw(Release)))
class MEModelRelease(Release):
    '''MorphoElectrical model release

    :param EModelRelease emodelRelease: electrical model release
    :param MorphologyRelease morphologyRelease: morphology model release
    :param memodelIndex Distribution: optional morpho-electrical model index
    '''
    base_url = DATA_SIM + '/memodelrelease/' + VERSION
