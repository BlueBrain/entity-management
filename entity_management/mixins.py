'''
Mixins to enhance entities
'''
import os
import re
from typing import List

import attr

from entity_management import nexus
from entity_management.compat import filter_
from entity_management.base import Distribution, _deserialize_list, attributes
from entity_management.settings import JSLD_REV
from entity_management.util import AttrOf


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
        self._instantiate()
        js = nexus.attach(self.id, self.meta.rev, file_name, data, content_type, token=use_auth)
        self.meta.rev = js[JSLD_REV]
        return self.evolve(distribution=_deserialize_list(List[Distribution],
                                                          js['distribution'],
                                                          token=use_auth))

    def download(self, path, use_auth=None):
        '''Download attachment of the entity and save it on the path with the originalFileName.

        Args:
            path(str): Absolute filename or path where to save the file.
                       If path is an existing folder, file name will be taken from
                       distribution originalFileName.
            use_auth(str): Optional OAuth token.
        '''
        dist = self.get_attachment()
        if dist is None:
            raise AssertionError('No attachment found')
        if os.path.exists(path) and os.path.isdir(path):
            filename = dist.originalFileName
        else:
            filename = os.path.basename(path)
            path = os.path.dirname(path)
        nexus.download(dist.downloadURL, path, filename, token=use_auth)
        return os.path.join(os.path.realpath(path), filename)

    def get_attachment(self):
        '''Get attachment distribution'''
        def is_attachment(dist):
            '''Predicate to find downloadable attachment'''
            return (hasattr(dist, 'originalFileName')
                    and hasattr(dist, 'downloadURL')
                    and dist.downloadURL.startswith('https://')
                    and dist.downloadURL.endswith('/attachment'))
        return next(filter_(is_attachment, self.distribution), None)

    def get_gpfs_path(self, media_type=None):
        '''Get gpfs link'''
        def is_gpfs(dist):
            '''Predicate to find gpfs distribution'''
            return (hasattr(dist, 'downloadURL')
                    and hasattr(dist, 'storageType')
                    and dist.storageType == 'gpfs'
                    and dist.downloadURL.startswith('file:///gpfs/')
                    and (media_type is not None
                         and hasattr(dist, 'mediaType')
                         and dist.mediaType == media_type
                         or media_type is None))
        dist = next(filter_(is_gpfs, self.distribution), None)
        if dist is not None:
            return re.sub('^file://', '', dist.downloadURL)
        else:
            return None
