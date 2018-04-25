'''
Mixins to enhance entities
'''
from entity_management import nexus
from entity_management.util import attributes, AttrOf
from entity_management.base import Frozen, Distribution, _deserialize_json_to_datatype
from entity_management.settings import JSLD_REV


@attributes({'distribution': AttrOf(Distribution, default=None)})
class DistributionMixin(Frozen):
    '''Provide `distribution` attribute.
    attach/download corresponding operations on the distribution.
    '''

    def attach(self, file_name, data, content_type='text/html', use_auth=None):
        '''Attach binary data to entity.
        Attached data downloadURL and other metadata will be available in ``distribution``.

        Args:
            file_name(str): Original file name.
            data(file): File like data stream.
            content_type(str): Content type with which attachment will be delivered when
                accessed with the download url. Default value is `text/html`.
            use_auth(str): Optional OAuth token.

        Returns:
            New instance with distribution attribute updated.
        '''
        js = nexus.attach(self._id, self._rev, file_name, data, content_type, use_auth)
        return self.evolve(_rev=js[JSLD_REV], distribution=_deserialize_json_to_datatype(
            Distribution, js['distribution'][0])) # nexus allows one attachment hence [0]

    def download(self, path, use_auth=None):
        '''Download attachment of the entity and save it on the path with the originalFileName.

        Args:
            path(str): Path where to save the file. File name will be taken from distribution
                originalFileName.
            use_auth(str): Optional OAuth token.
        '''
        file_name = self.distribution.originalFileName
        url = self.distribution.downloadURL
        nexus.download(url, path, file_name, use_auth)
