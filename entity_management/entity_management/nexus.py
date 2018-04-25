'''New nexus access layer'''
from __future__ import print_function

import logging
import requests
import sys
import os

from functools import wraps
from pprint import pprint

from six import iteritems, text_type, PY2
from six.moves.urllib.parse import urlsplit # pylint: disable=import-error,no-name-in-module

from entity_management.settings import BASE, NSG_CTX

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


def _get_headers(token):
    '''Get headers with additional authorization header if token is not None'''
    headers = {'accept': 'application/ld+json'}
    if token is not None:
        headers['authorization'] = token
    return headers


def _byteify(data, ignore_dicts=False):
    '''Use to convert unicode strings to str while loading json'''
    # if this is a unicode string, return its string representation
    if isinstance(data, text_type):
        return data.encode('utf-8') if PY2 else data
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
            pprint(e.response.text, stream=sys.stderr)
            print('<<<', file=sys.stderr)
            raise
    return wrapper


def get_uuid_from_url(url):
    '''Extract last part of url path which is UUID'''
    return urlsplit(url).path.split('/')[-1]


@_log_nexus_exception
def save(base_url, payload, token=None):
    '''Save entity, return json response

    Args:
        base_url(str): Base url of the entity which will be saved.
        payload(dict): Json-ld serialization of the entity.
        token(str): Optional OAuth token.

    Returns:
        Json response.
    '''
    response = requests.post(base_url,
                             headers=_get_headers(token),
                             json=payload)
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def update(id_url, rev, payload, token=None):
    '''Update entity, return json response

    Args:
        id_url(str): Url of the entity which will be updated.
        rev(int): Revision number.
        payload(dict): Json-ld serialization of the entity.
        token(str): Optional OAuth token.

    Returns:
        Json response.
    '''
    assert id_url is not None
    assert rev > 0
    response = requests.put(id_url,
                            headers=_get_headers(token),
                            params={'rev': rev},
                            json=payload)
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def deprecate(id_url, rev, token=None):
    '''Mark entity as deprecated, return json response'''
    assert id_url is not None
    assert rev > 0
    response = requests.delete(id_url,
                               headers=_get_headers(token),
                               params={'rev': rev})
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def attach(id_url, rev, file_name, data, content_type, token=None):
    '''Attach binary to the entity.

    Args:
        id_url(str): Url of the entity to which the attachment will be added.
        file_name(str): Original file name.
        data(file): File like data stream.
        content_type(str): Content type with which attachment will be delivered when accessed
            with the download url.
        token(str): Optional OAuth token.

    Returns:
        Json response.
    '''
    assert id_url is not None
    assert rev > 0
    response = requests.put('%s/attachment' % id_url,
                            headers=_get_headers(token),
                            params={'rev': rev},
                            files={'file': (file_name, data, content_type)})
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_log_nexus_exception
def download(url, path, file_name, token=None):
    '''Download entity attachment.

    Args:
        url(str): Url of the attachment.
        path(str): Path where to save the file.
        file_name(str): File name.
        token(str): Optional OAuth token.

    Returns:
        Raw response.
    '''
    response = requests.get(url, headers={'authorization': token} if token else {}, stream=True)
    try:
        response.raise_for_status()
        with open(os.path.join(path, file_name), 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    finally:
        response.close()


@_log_nexus_exception
def load_by_uuid(base_url, uuid, token=None):
    '''Load Entity from the base url with appended uuid'''
    response = requests.get('%s/%s' % (base_url, uuid), headers=_get_headers(token))
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js


@_log_nexus_exception
def find_uuid_by_name(base_url, name, token=None):
    '''Lookup not deprecated entity uuid from the base url with the name filter'''
    response = requests.get(base_url,
                            headers=_get_headers(token),
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


@_log_nexus_exception
# def find_by(cls, token=None, **properties): FIXME uncomment when properties will be clear
def find_by(cls, token=None):
    '''Lookup not deprecated entity uuid from the base url with the name filter'''
    props = []
    # 'path':"name","value":"%s"} % name}) FIXME one of the properties will be name
    response = requests.post('%s/queries' % BASE,
                             headers=_get_headers(token),
                             json={
                                 '@context': NSG_CTX,
                                 'resource': 'instances',
                                 'deprecated': False,
                                 'filter': {
                                     'op': 'and',
                                     'value': [{'op': 'eq', 'path': 'rdf:type', 'value': cls}]
                                     + props
                                     }
                                 },
                             allow_redirects=False)

    # query successful follow redirect
    if response.status_code == 308:
        location = response.headers.get('location')
        return location
    response.raise_for_status()
    return None


@_log_nexus_exception
def load_by_url(url, token=None):
    '''Load json-ld from url'''
    response = requests.get(url, headers=_get_headers(token))
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js
