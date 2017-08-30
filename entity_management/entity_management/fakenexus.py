""" Access to fakenexus """

import functools
import hashlib
import logging
import os
import shutil

import requests

from entity_management.compat import urlsplit, urlunsplit
from entity_management.entity import ENTITY_TYPES

L = logging.getLogger(__name__)


SERVER_URL = "148.187.85.73:5000"
PROJECT_DIR = "/gpfs/bbp.cscs.ch/project/{project}/.nexus"

BLOCK_SIZE = 4 * 1024 * 1024


def _md5sum(filepath):
    '''get md5sum of file'''
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as fd:
        for chunk in iter(functools.partial(fd.read, BLOCK_SIZE), b''):
            hash_md5.update(chunk)
    result = hash_md5.hexdigest()
    assert len(result) == 32
    return result


def _snapshot_file(src_path, dst_path):
    '''copy file to 'immutable' store'''
    L.debug("Snapshot file: %s -> %s", src_path, dst_path)
    shutil.copyfile(src_path, dst_path)
    os.chmod(dst_path, 0o444)


def register_entity(collection, entity):
    '''register entity w/ fakenexus in collection'''
    L.debug('register_entity: %s to %s', entity, collection)
    base_url = "http://{server}/{collection}/".format(server=SERVER_URL,
                                                      collection=collection)
    resp = requests.post(base_url, json=entity)
    resp.raise_for_status()
    return "fakenexus:///{collection}/{uuid}".format(collection=collection,
                                                     uuid=resp.content)


def register_file(filepath, project, basename=None):
    '''register file w/ fakenexus in collection'''
    L.debug('Register file: %s to %s', filepath, project)
    if basename is None:
        basename = os.path.basename(filepath)
    filename = _md5sum(filepath) + "-" + basename
    stored_path = os.path.join(PROJECT_DIR.format(project=project), "files", filename)
    if not os.path.exists(stored_path):
        _snapshot_file(filepath, stored_path)
    return "fakenexus://{project}/files/{filename}".format(project=project,
                                                           filename=filename)


def register_files(dirpath, files, project, basename=None):
    '''register files w/ fakenexus in collection'''
    if basename is None:
        basename = os.path.basename(dirpath)
    file_checksums = [_md5sum(os.path.join(dirpath, filename))
                      for filename in sorted(files)]
    total_checksum = hashlib.md5("".join(file_checksums)).hexdigest()
    dirname = total_checksum + "-" + basename
    stored_path = os.path.join(PROJECT_DIR.format(project=project), "files", dirname)
    if not os.path.exists(stored_path):
        os.mkdir(stored_path)
        for filename in files:
            _snapshot_file(
                os.path.join(dirpath, filename),
                os.path.join(stored_path, filename)
            )

    return "fakenexus://{project}/files/{dirname}".format(project=project, dirname=dirname)


def get_entity(url):
    """ Get entity by 'fakenexus://' URL. """
    L.debug('Getting entity: %s', url)
    scheme, netloc, path = urlsplit(url)[:3]
    assert(scheme == 'fakenexus')

    if netloc in ENTITY_TYPES:
        path = os.path.join(netloc, path[1:])
        netloc = SERVER_URL
    elif not netloc:
        netloc = SERVER_URL

    http_url = urlunsplit(("http", netloc, path, None, None))
    resp = requests.get(http_url)
    resp.raise_for_status()
    return resp.json()


def get_entities(collection, query):
    '''list entites that satisfy dictionary `query`'''
    collection = ENTITY_TYPES[collection]

    url = os.path.join('http://', SERVER_URL, collection)
    resp = requests.get(url, params=query)
    resp.raise_for_status()
    return resp.json()


def get_file_path(url):
    """ Get file path by 'fakenexus://' URL. """
    L.debug('Getting filepath: %s', url)
    scheme, netloc, path = urlsplit(url)[:3]
    assert(scheme == 'fakenexus')
    return os.path.join(PROJECT_DIR.format(project=netloc), path[1:])
