'''New nexus access layer'''
from __future__ import print_function

import logging
import requests
import sys

from functools import wraps
from pprint import pprint

from six import iteritems
from six.moves.urllib.parse import urlsplit # pylint: disable=import-error,no-name-in-module

import attr

from entity_management.settings import JSLD_ID, JSLD_REV

L = logging.getLogger(__name__)


def _byteify(data, ignore_dicts=False):
    '''Use to convert unicode strings to str while loading json'''
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in iteritems(data)
        }
    # if it's anything else, return it in its original form
    return data


def _log_nexus_exception(func):
    '''Pretty print nexus error responses'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        '''decorator function'''
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            print('NEXUS ERROR>>>', file=sys.stderr)
            pprint(e.response.json(object_hook=_byteify), stream=sys.stderr)
            print('<<<', file=sys.stderr)
            raise
    return wrapper


def get_uuid_from_url(url):
    '''Extract last part of url path which is UUID'''
    return urlsplit(url).path.split('/')[-1]


@_log_nexus_exception
def save(entity):
    '''Save entity, return new instance with uuid, rev, deprecated fields updated'''
    response = requests.post(entity.base_url,
                             headers={'accept': 'application/ld+json'},
                             json=entity.as_json_ld())
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return attr.evolve(entity,
                       uuid=get_uuid_from_url(js[JSLD_ID]),
                       rev=js[JSLD_REV])


@_log_nexus_exception
def update(entity):
    '''Update entity, return new instance with uuid, rev, deprecated fields updated'''
    response = requests.put('%s/%s' % (entity.base_url, entity.uuid),
                            headers={'accept': 'application/ld+json'},
                            params={'rev': entity.rev},
                            json=entity.as_json_ld())
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return attr.evolve(entity, rev=js[JSLD_REV])


@_log_nexus_exception
def deprecate(entity):
    '''Mark entity as deprecated, return new instance with deprecated field updated'''
    assert entity.uuid is not None
    assert entity.rev > 0
    response = requests.delete('%s/%s' % (entity.base_url, entity.uuid),
                               headers={'accept': 'application/ld+json'},
                               params={'rev': entity.rev})
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return attr.evolve(entity, rev=js[JSLD_REV], deprecated=True)


@_log_nexus_exception
def attach(base_url, uuid, rev, file_name, data, content_type):
    '''Attach binary to the entity.

    Args:
        base_url(str): Base url of the entity to which the attachment will be added.
        uuid(str): UUID of the entity.
        file_name(str): Original file name.
        data(file): File like data stream.
        content_type(str): Content type with which attachment will be delivered when accessed
            with the download url.

    Returns:
        New instance with uuid, rev, deprecated fields updated.
    '''
    response = requests.put('%s/%s/attachment' % (base_url, uuid),
                            headers={'accept': 'application/ld+json'},
                            params={'rev': rev},
                            files={'file': (file_name, data, content_type)})
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js


@_log_nexus_exception
def load_by_uuid(base_url, uuid):
    '''Load Entity from the base url with appended uuid'''
    response = requests.get('%s/%s' % (base_url, uuid))
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    js[JSLD_ID] = get_uuid_from_url(js[JSLD_ID])
    return js


@_log_nexus_exception
def find_uuid_by_name(base_url, name):
    '''Lookup not deprecated entity uuid from the base url with the name filter'''
    response = requests.get(base_url, params={
        'deprecated': 'false',
        'filter': '{"op":"eq","path":"schema:name","value":"%s"}' % name})
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    if js['total'] == 0:
        return None
    elif js['total'] > 1:
        raise ValueError('Too many results found!')
    return get_uuid_from_url(js['results'][0]['resultId'])
