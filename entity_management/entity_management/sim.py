'''Simulation domain base entities'''
from entity_management.base import Identifiable, OntologyTerm
from entity_management.mixins import DistributionMixin
from entity_management.util import attributes, AttrOf


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
    })
class Entity(DistributionMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''
    _type_namespace = 'nsg'

    def __attrs_post_init__(self):
        super(Entity, self).__attrs_post_init__()
        self._type.append('prov:Entity')


@attributes({'modelOf': AttrOf(str, default=None),
             'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelInstance(Entity):
    '''Abstract model instance.

    Args:
        modelOf(str): Specifies the model.
        brainRegion(OntologyTerm): Brain region ontology term.
        species(OntologyTerm): Species ontology term.
    '''
    pass


@attributes({'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelRelease(Entity):
    '''Release base entity'''
    _url_version = 'v0.1.1'


@attributes()
class ModelScript(Entity):
    '''Base entity for the scripts attached to the model.'''
    pass


@attributes()
class ModelReleaseIndex(Entity):
    '''Index files attached to release entities'''
    _url_version = 'v0.1.1'
