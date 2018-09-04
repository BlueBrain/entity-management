'''New nexus access layer'''
from __future__ import print_function

import re
import logging
import os
import sys
from functools import wraps
from pprint import pprint

import requests
from six import PY2, iteritems, text_type
# pylint: disable=import-error,no-name-in-module, relative-import,wrong-import-order
from six.moves.urllib.parse import urlsplit

from entity_management.settings import BASE, NSG_CTX, USERINFO

L = logging.getLogger(__name__)

_URL_TO_CLS_MAP = {}


def register_type(type_hint, cls):
    '''Store type corresponding to type hint'''
    _URL_TO_CLS_MAP[type_hint] = cls


def _type_hint_from(id_url):
    '''Ignore the ending UUID and take domain/entity as type hint'''
    return '/'.join(urlsplit(id_url).path.split('/')[-4:-2])


def get_type(id_url):
    '''Get type which corresponds to the id_url'''
    return _URL_TO_CLS_MAP.get(_type_hint_from(id_url), None)


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


def _check_token_validity(token):
    '''Check that token is valid'''

    if token is None:
        raise Exception(
            'Environment variable NEXUS_TOKEN is empty. It should contain a Nexus token.'
            'You can get one by going to https://bbp-nexus.epfl.ch/staging/explorer/ '
            'and clicking the "Copy token" button')

    r = requests.get(USERINFO, headers={'accept': 'application/json', 'authorization': token})

    if r.status_code == 200:
        return
    if r.status_code == 500:
        raise Exception('GET {} is returning an Error 500. Nexus is probably down. '
                        'Try again later'.format(USERINFO))
    if r.status_code == 401:
        raise Exception('Error 401: your token has expired or you are not authorized.\n'
                        'Current token: {}\n'
                        'Suggestion: try renewing the token stored in the environment variable: '
                        'NEXUS_TOKEN'.format(token))

    raise Exception('Received error code for query\nGET {}:\nError {}, {}'.format(
        USERINFO, r.status_code, r.text))


def _print_violation_summary(data):
    '''Add colors, remove hashes and other superfluous things from error message'''
    print('\nNEXUS ERROR SUMMARY:\n', file=sys.stderr)

    for error in data['violations']:
        no_hash = re.sub(r',? *(Constraint|Node)(:|\() ?_:\w{32}\)?', '', error)
        no_hash = re.sub(r'^Error: Violation Error\((.*?)\). ', r'Violation(\g<1>):\n', no_hash)
        if no_hash.startswith('Violation'):
            color = '\033[92m'
            end_color = '\033[0m'
            color_url = re.sub(r'<(.*?)>', color + r'<\g<1>>' + end_color, no_hash)

        print(color_url + '\n', file=sys.stderr)


def _nexus_wrapper(func):
    '''Pretty print nexus error responses, inject token if set in env'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        '''decorator function'''
        token_argument = kwargs.get('token', None)
        if token_argument is None:
            kwargs['token'] = os.getenv('NEXUS_TOKEN', None)

        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                _check_token_validity(kwargs['token'])
            print('NEXUS ERROR>>>', file=sys.stderr)
            pprint(e.response.text, stream=sys.stderr)
            if e.response.status_code == 400:
                _print_violation_summary(e.response.json())
            print('<<<', file=sys.stderr)
            raise
    return wrapper


def get_uuid_from_url(url):
    '''Extract last part of url path which is UUID'''
    return urlsplit(url).path.split('/')[-1]


@_nexus_wrapper
def create(base_url, payload, token=None):
    '''Create entity, return json response

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


@_nexus_wrapper
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


@_nexus_wrapper
def deprecate(id_url, rev, token=None):
    '''Mark entity as deprecated, return json response'''
    assert id_url is not None
    assert rev > 0
    response = requests.delete(id_url,
                               headers=_get_headers(token),
                               params={'rev': rev})
    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_nexus_wrapper
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


@_nexus_wrapper
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
    response = requests.get(
        url, headers={'authorization': token} if token else {}, stream=True)
    try:
        response.raise_for_status()
        with open(os.path.join(path, file_name), 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    finally:
        response.close()


@_nexus_wrapper
def find_by(collection_address=None, query=None, token=None):
    '''Find entities using NEXUS queries endpoint'''
    if query is not None:
        json = {'@context': NSG_CTX,
                'resource': 'instances',
                'deprecated': False,
                'filter': query}
    else:
        json = {'@context': NSG_CTX,
                'resource': 'instances', 'deprecated': False}

    response = requests.post('%s/queries%s' % (BASE, collection_address or ''),
                             headers=_get_headers(token),
                             json=json,
                             allow_redirects=False)

    # query successful follow redirect
    if response.status_code == 303:
        return response.headers.get('location')

    response.raise_for_status()
    return None


@_nexus_wrapper
def load_by_url(url, token=None):
    '''Load json-ld from url'''
    response = requests.get(url, headers=_get_headers(token))
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js


@_nexus_wrapper
def get_current_agent(token=None):
    '''Get user info'''
    if token is None:
        return None

    response = requests.get(USERINFO, headers={'accept': 'application/json',
                                               'authorization': token})
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js
