'''New nexus access layer'''
from __future__ import print_function

import logging
import requests
import sys

from functools import wraps
from pprint import pprint

from six import iteritems
from six.moves.urllib.parse import urlsplit # pylint: disable=import-error,no-name-in-module

from entity_management.settings import JSLD_ID, TOKEN

L = logging.getLogger(__name__)

_URL_TO_CLS_MAP = {}


def register_type(url_prefix, cls):
    '''Store type corresponding to url prefix'''
    _URL_TO_CLS_MAP[url_prefix] = cls


def get_type(url):
    '''Get type which corresponds to the url'''
    for url_prefix in _URL_TO_CLS_MAP:
        if url.startswith(url_prefix):
            return _URL_TO_CLS_MAP[url_prefix]
    return None


def _get_headers():
    '''Get headers with additional authorization header if NEXUS_TOKE env variable had value'''
    headers = {'accept': 'application/ld+json'}
    if TOKEN is not None:
        headers['authorization'] = 'bearer %s' % TOKEN
    return headers


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
def save(base_url, payload):
    '''Save entity, return json response

    Args:
        base_url(str): Base url of the entity which will be saved.
        payload(dict): Json-ld serialization of the entity.

    Returns:
        Json response.
    '''
    response = requests.post(base_url,
                             headers=_get_headers(),
                             json=payload)
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def update(base_url, uuid, rev, payload):
    '''Update entity, return json response

    Args:
        base_url(str): Base url of the entity which will be updated.
        uuid(str): UUID of the entity.
        rev(int): Revision number.
        payload(dict): Json-ld serialization of the entity.

    Returns:
        Json response.
    '''
    assert uuid is not None
    assert rev > 0
    response = requests.put('%s/%s' % (base_url, uuid),
                            headers=_get_headers(),
                            params={'rev': rev},
                            json=payload)
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def deprecate(base_url, uuid, rev):
    '''Mark entity as deprecated, return json response'''
    assert uuid is not None
    assert rev > 0
    response = requests.delete('%s/%s' % (base_url, uuid),
                               headers=_get_headers(),
                               params={'rev': rev})
    response.raise_for_status()
    return response.json(object_hook=_byteify)


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
        Json response.
    '''
    response = requests.put('%s/%s/attachment' % (base_url, uuid),
                            headers=_get_headers(),
                            params={'rev': rev},
                            files={'file': (file_name, data, content_type)})
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def load_by_uuid(base_url, uuid):
    '''Load Entity from the base url with appended uuid'''
    response = requests.get('%s/%s' % (base_url, uuid), headers=_get_headers())
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
    response = requests.get(base_url,
                            headers=_get_headers(),
                            params={
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


def load_by_url(url):
    '''Load Entity from url'''
    uuid = get_uuid_from_url(url)
    cls = get_type(url)
    return cls.from_uuid(uuid)
