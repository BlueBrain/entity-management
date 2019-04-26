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

from entity_management.util import quote
from entity_management.settings import (BASE_RESOURCES, USERINFO, BASE_FILES, ORG, PROJ,
                                        DASH, NSG)

L = logging.getLogger(__name__)

_URL_TO_CLS_MAP = {}


def register_type(schema_id, cls):
    '''Store type corresponding to type hint'''
    _URL_TO_CLS_MAP[schema_id] = cls


def get_type(types):
    '''Get type which corresponds to the id_url'''
    raise Exception(types)
    # return _URL_TO_CLS_MAP.get(_type_hint_from(id_url), None)


def get_type_from_id(resource_id, token=None):
    '''Get type which corresponds to the id_url'''
    url = '%s/%s/%s/_/%s' % (BASE_RESOURCES, ORG, PROJ, quote(resource_id))
    response = requests.get(url, headers=_get_headers(token))
    response.raise_for_status()
    constrained_by = response.json(object_hook=_byteify)['_constrainedBy']
    constrained_by = constrained_by.replace('dash:', str(DASH)).replace('nsg:', str(NSG))
    return _URL_TO_CLS_MAP[constrained_by]


def _get_headers(token=None, accept='application/ld+json'):
    '''Get headers with additional authorization header if token is not None'''
    headers = {}
    if token is not None:
        headers['authorization'] = token
    if accept is not None:
        headers['accept'] = accept
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

        if 'NEXUS_DRY_RUN' in os.environ and func.__name__ in ['create', 'update', 'deprecate']:
            return None

        token_argument = kwargs.get('token', None)
        if token_argument is None:
            kwargs['token'] = os.getenv('NEXUS_TOKEN', None)

        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                _check_token_validity(kwargs['token'])
            print('NEXUS ERROR>>>', file=sys.stderr)
            try:
                response_data = e.response.json()
            except ValueError:
                response_data = e.response.text
            pprint(response_data, stream=sys.stderr)
            # if e.response.status_code == 400: TODO this is different in v1
            #     _print_violation_summary(e.response.json())
            print('<<<', file=sys.stderr)
            raise
    return wrapper


@_nexus_wrapper
def create(base_url, payload, resource_id=None, token=None):
    '''Create entity, return json response

    Args:
        base_url(str): Base url of the entity which will be saved.
        payload(dict): Json-ld serialization of the entity.
        token(str): Optional OAuth token.

    Returns:
        Json response.
    '''
    if resource_id:
        url = '%s/%s' % (base_url, resource_id)
        response = requests.put(url, headers=_get_headers(token), json=payload)
    else:
        response = requests.post(base_url, headers=_get_headers(token), json=payload)
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


# @_nexus_wrapper
# def find_by(collection_address=None, query=None, token=None):
#     '''Find entities using NEXUS queries endpoint'''
#     if query is not None:
#         json = {'@context': NSG_CTX,
#                 'resource': 'instances',
#                 'deprecated': False,
#                 'filter': query}
#     else:
#         json = {'@context': NSG_CTX,
#                 'resource': 'instances', 'deprecated': False}
#
#     response = requests.post('%s/queries%s' % (BASE, collection_address or ''),
#                              headers=_get_headers(token),
#                              json=json,
#                              allow_redirects=False)
#
#     # query successful follow redirect
#     if response.status_code == 303:
#         return response.headers.get('location')
#
#     response.raise_for_status()
#     return None


@_nexus_wrapper
def load_by_url(url, params=None, stream=False, token=None):
    '''Load json-ld from url

    Args:
        url (str): Url of the entity which will be loaded.
        params (dict): Url query params.
        stream (bool): If True then ``response.content`` stream is returned.
        token (str): Optional OAuth token.

    Returns:
        if stream is true then response stream content is returned otherwise
        json response.
    '''
    response = requests.get(url, headers=_get_headers(token), params=params)
    # if not found then return None
    if response.status_code == 404:
        return None
    response.raise_for_status()
    if stream:
        return response.content
    else:
        return response.json(object_hook=_byteify)


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


def _get_files_endpoint():
    return ''


@_nexus_wrapper
def _get_file_metadata(resource_id, tag=None, token=None):
    '''Helper function'''
    url = '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(resource_id))
    response = requests.get(url,
                            headers=_get_headers(token),
                            params={'tag': tag if tag else None})

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json(object_hook=_byteify)


def get_file_rev(resource_id, tag=None, token=None):
    '''Get file rev.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        token(str): Optional OAuth token.

    Returns:
        File revision.
    '''
    return _get_file_metadata(resource_id, tag, token)['_rev']


def get_file_name(resource_id, tag=None, token=None):
    '''Get file rev.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        token(str): Optional OAuth token.

    Returns:
        File name.
    '''
    return _get_file_metadata(resource_id, tag, token)['_filename']


@_nexus_wrapper
def upload_file(name, data, content_type, resource_id=None, rev=None, token=None):
    '''Upload file.

    Args:
        name (str): File name.
        data (file): File like data stream.
        content_type (str): Content type of the data stream.
        resource_id (str): Nexus ID of the file.
        rev (int): If you are reuploading file this needs to match current revision of the file.
        token(str): OAuth token.

    Returns:
        Identifier of the uploaded file.
    '''
    if resource_id:
        url = '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(resource_id))
        response = requests.put(url,
                                headers=_get_headers(token),
                                params={'rev': rev if rev else None},
                                files={'file': (name, data, content_type)})
    else:
        url = '%s/%s/%s' % (BASE_FILES, ORG, PROJ)
        response = requests.post(url,
                                 headers=_get_headers(token),
                                 files={'file': (name, data, content_type)})

    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_nexus_wrapper
def download_file(resource_id, path, file_name=None, tag=None, rev=None, token=None):
    '''Download file.

    Args:
        resource_id (str): Nexus ID of the file.
        path (str): Path where to save the file.
        file_name (str): Provide file name to use instead of original name.
        tag (str): Provide tag to fetch specific file.
        rev (int): Provide revision number to fetch specific file.
        token(str): Optional OAuth token.

    Returns:
        Raw response.
    '''
    url = '%s/%s/%s/%s' % (BASE_FILES, ORG, PROJ, quote(resource_id))

    response = requests.get(url,
                            headers=_get_headers(token, accept=None),
                            params={'tag': tag if tag else None,
                                    'rev': rev if rev else None},
                            stream=True)
    try:
        response.raise_for_status()
        if file_name is None:
            file_name = response.headers.get('content-disposition')
            file_name = re.findall("filename\\*=UTF-8''(.+)", file_name)[0]
        file_ = os.path.join(path, file_name)
        with open(file_, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    finally:
        response.close()

    return os.path.join(os.path.realpath(path), file_name)
