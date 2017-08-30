'''Client for interacting w/ provenance and file store'''
import logging

from entity_management import fakenexus
from entity_management.compat import urlsplit
from entity_management.config import Config
from entity_management.entity import ENTITY_TYPES


L = logging.getLogger(__name__)
DEFAULT_CONFIG = Config()


def _assert_entity(type_):
    '''known entity type'''
    assert type_ in ENTITY_TYPES


def get_entity(type_, id_, config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''known entity type'''
    _assert_entity(type_)
    url = "fakenexus:///{collection}/{id}".format(collection=type_, id=id_)
    return fakenexus.get_entity(url)


def get_entity_by_url(url, config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''known entity type'''
    return fakenexus.get_entity(url)


def get_entities(type_, query, config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''register files'''
    _assert_entity(type_)
    return fakenexus.get_entities(collection=type_, query=query)


def register_entity(type_, properties, config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''register entity'''
    _assert_entity(type_)
    return fakenexus.register_entity(type_, properties)


def register_file(filepath, project, basename=None,
                  config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''register file'''
    return fakenexus.register_file(filepath, project, basename=basename)


def register_files(dirpath, files, project, basename=None,
                   config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    '''register files'''
    return fakenexus.register_files(dirpath, files, project, basename)


def get_file_path_by_url(url, config=DEFAULT_CONFIG):  # pylint: disable=unused-argument
    ''' Get locally available file path from URL '''
    scheme, netloc, path = urlsplit(url)[:3]
    if scheme in ('file', ''):
        assert(not netloc)
        result = path
    elif scheme == 'fakenexus':
        result = fakenexus.get_file_path(url)
    else:
        raise Exception("Unexpected URL scheme: '%s'" % scheme)
    return result
