'''Provenance entities'''
from entity_management import nexus
from entity_management.base import (Identifiable, Distribution, OntologyTerm,
                                    _deserialize_json_to_datatype)
from entity_management.util import attributes, AttrOf
from entity_management.settings import JSLD_REV


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
    'distribution': AttrOf(Distribution, default=None)
    })
class Entity(Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''
    _type_namespace = 'nsg'

    def __attrs_post_init__(self):
        super(Entity, self).__attrs_post_init__()
        self._types.append('prov:Entity')

    def attach(self, file_name, data, content_type='text/html', token=None):
        '''Attach binary data to entity.
        Attached data downloadURL and other metadata will be available in ``distribution``.

        Args:
            file_name(str): Original file name.
            data(file): File like data stream.
            content_type(str): Content type with which attachment will be delivered when
                accessed with the download url. Default value is `text/html`.
            token(str): Optional OAuth token.

        Returns:
            New instance with distribution attribute updated.
        '''
        assert self._uuid is not None # pylint: disable=no-member
        js = nexus.attach(self._base_url, self._uuid, self._rev,
                          file_name, data, content_type, token)
        return self.evolve(_rev=js[JSLD_REV], distribution=_deserialize_json_to_datatype(
            Distribution, js['distribution'][0]))

    def download(self, path, token=None):
        '''Download attachment of the entity and save it on the path with the originalFileName.

        Args:
            path(str): Path where to save the file. File name will be taken from distribution
                originalFileName.
            token(str): Optional OAuth token.
        '''
        file_name = self.distribution.originalFileName
        url = self.distribution.downloadURL
        nexus.download(url, path, file_name, token)


@attributes()
class Release(Entity):
    '''Release base entity'''
    pass


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


@attributes()
class ModelScript(Entity):
    '''Base entity for the scripts attached to the model.'''
    pass
