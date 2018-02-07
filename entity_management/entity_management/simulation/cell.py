'''Cell related entities'''
import attr
from attr.validators import instance_of

from entity_management.settings import DATA_SIM, VERSION
from entity_management.base import Entity, Distribution, _merge, _attrs_pos, _attrs_kw, _optional_of


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=instance_of(Distribution)),
     'emodelIndex': attr.ib(type=Distribution, validator=instance_of(Distribution))},
    _attrs_pos(Entity),
    _attrs_kw(Entity)))
class EModelRelease(Entity):
    '''Electrical model release'''
    base_url = DATA_SIM + '/emodelrelease/' + VERSION


@attr.s(these=_merge(
    {'distribution': attr.ib(type=Distribution, validator=_optional_of(Distribution))},
    _attrs_pos(Entity),
    {'morphologyIndex': attr.ib(type=Distribution,
                                validator=_optional_of(Distribution),
                                default=None)},
    _attrs_kw(Entity)))
class MorphologyRelease(Entity):
    '''Morphology release

    :param Distribution distribution: distribution
    :param Distribution morphologyIndex: morphology index
    '''
    base_url = DATA_SIM + '/morphologyrelease/' + VERSION


@attr.s(these=_merge(
    {'emodelRelease': attr.ib(type=EModelRelease, validator=instance_of(EModelRelease)),
     'morphologyRelease': attr.ib(type=MorphologyRelease,
                                  validator=instance_of(MorphologyRelease))},
    _attrs_pos(Entity),
    {'memodelIndex': attr.ib(type=Distribution,
                             validator=_optional_of(Distribution),
                             default=None)},
    _attrs_kw(Entity)))
class MEModelRelease(Entity):
    '''MorphoElectrical model release

    :param EModelRelease emodelRelease: electrical model release
    :param MorphologyRelease morphologyRelease: morphology model release
    :param memodelIndex Distribution: optional morpho-electrical model index
    '''
    base_url = DATA_SIM + '/memodelrelease/' + VERSION
