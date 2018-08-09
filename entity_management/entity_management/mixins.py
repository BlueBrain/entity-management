'''
Mixins to enhance entities
'''
import re
import attr

from typing import List

from entity_management import nexus
from entity_management.compat import filter_
from entity_management.util import attributes, AttrOf
from entity_management.base import Distribution, _deserialize_list
from entity_management.settings import JSLD_REV


@attributes({'distribution': AttrOf(List[Distribution], default=None)})
@attr.s
class DistributionMixin(object):
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
        js = nexus.attach(self._id, self._rev, file_name, data, content_type, token=use_auth)
        return self.evolve(_rev=js[JSLD_REV],
                           distribution=_deserialize_list(List[Distribution],
                                                          js['distribution'],
                                                          token=use_auth))

    def download(self, path, use_auth=None):
        '''Download attachment of the entity and save it on the path with the originalFileName.

        Args:
            path(str): Path where to save the file. File name will be taken from distribution
                originalFileName.
            use_auth(str): Optional OAuth token.
        '''
        def is_attachment(dist):
            '''Predicate to find downloadable attachment'''
            return (hasattr(dist, 'originalFileName')
                    and hasattr(dist, 'downloadURL')
                    and dist.downloadURL.startswith('https://')
                    and dist.downloadURL.endswith('/attachment'))
        dist = next(filter_(is_attachment, self.distribution), None)
        if dist is None:
            raise AssertionError('No attachment found')
        nexus.download(dist.downloadURL, path, dist.originalFileName, token=use_auth)

    def get_gpfs_path(self):
        '''Get gpfs link'''
        def is_gpfs(dist):
            '''Predicate to find gpfs distribution'''
            return (hasattr(dist, 'downloadURL')
                    and hasattr(dist, 'storageType')
                    and dist.storageType == 'gpfs'
                    and dist.downloadURL.startswith('file:///gpfs/'))
        dist = next(filter_(is_gpfs, self.distribution), None)
        if dist is not None:
            return re.sub('^file://', '', dist.downloadURL)
        else:
            return None
