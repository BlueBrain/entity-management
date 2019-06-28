'''New nexus access layer'''
from __future__ import print_function

import re
import logging
import os
import sys
from functools import wraps
from pprint import pprint

from six import PY2, iteritems, text_type

import requests

from entity_management.util import quote
from entity_management.state import get_org, get_proj, get_token, refresh_token, has_offline_token
from entity_management.settings import (BASE_RESOURCES, USERINFO, BASE_FILES, DASH, NSG,
                                        JSLD_TYPE)

L = logging.getLogger(__name__)

_HINT_TO_CLS_MAP = {}
_UNCONSTRAINED = 'https://bluebrain.github.io/nexus/schemas/unconstrained.json'


def register_type(key, cls):
    '''Store type corresponding type hint.

    Args:
        hint (str): Type hint. In general can be any string such as id of the schema which
            constraines the type or @type name in the case of unconstrained type.
        cls (type): Entity python class which maps to this hint.
    '''
    _HINT_TO_CLS_MAP[key] = cls


def _find_type(types):
    '''Get type from the json-ld @types. It can be a list of types or a single string.'''
    if isinstance(types, str):
        return types
    else:
        return types[0]  # just return the first one from the list for now.


def _get_headers(token=None, accept='application/ld+json'):
    '''Get headers with additional authorization header if token is not None'''
    headers = {}
    if token is not None:
        headers['authorization'] = 'Bearer ' + token
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


def _print_nexus_error(http_error):
    '''Helper function to log in stderr nexus error response.'''
    print('NEXUS ERROR>>>', file=sys.stderr)
    try:
        response_data = http_error.response.json()
    except ValueError:
        response_data = http_error.response.text
    pprint(response_data, stream=sys.stderr)
    print('<<<', file=sys.stderr)
    sys.stderr.flush()


def _nexus_wrapper(func):
    '''Pretty print nexus error responses, inject token if set in env'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        '''decorator function'''

        if 'NEXUS_DRY_RUN' in os.environ and func.__name__ in ['create', 'update', 'deprecate']:
            return None

        token_argument = kwargs.get('token', None)
        if token_argument is None:
            kwargs['token'] = get_token()

        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as http_error:
            # retry function call only when got Unauthorized, we have offline token to produce the
            # new access token and token was not explicitly provided
            if (http_error.response.status_code == 401
                    and has_offline_token()
                    and token_argument is None):
                kwargs['token'] = refresh_token()
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as http_error:
                    _print_nexus_error(http_error)
                    raise
            _print_nexus_error(http_error)
            raise
    return wrapper


@_nexus_wrapper
def get_type_from_id(resource_id, token=None):
    '''Get type which corresponds to the id_url'''
    url = '%s/%s/%s/_/%s' % (BASE_RESOURCES, get_org(), get_proj(), quote(resource_id))
    response = requests.get(url, headers=_get_headers(token))
    response.raise_for_status()
    response_json = response.json(object_hook=_byteify)
    constrained_by = response_json['_constrainedBy']
    if constrained_by == _UNCONSTRAINED:
        return _HINT_TO_CLS_MAP[_find_type(response_json[JSLD_TYPE])]
    else:
        constrained_by = constrained_by.replace('dash:', str(DASH)).replace('nsg:', str(NSG))
        return _HINT_TO_CLS_MAP[constrained_by]


@_nexus_wrapper
def create(base_url, payload, resource_id=None, token=None):
    '''Create entity, return json response

    Args:
        base_url (str): Base url of the entity which will be saved.
        payload (dict): Json-ld serialization of the entity.
        token (str): Optional OAuth token.

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
        id_url (str): Url of the entity which will be updated.
        rev (int): Revision number.
        payload (dict): Json-ld serialization of the entity.
        token (str): Optional OAuth token.

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
                                               'authorization': 'Bearer ' + token})
    response.raise_for_status()
    js = response.json(object_hook=_byteify)
    return js


def _get_files_endpoint():
    return ''


@_nexus_wrapper
def _get_file_metadata(resource_id, tag=None, token=None):
    '''Helper function'''
    url = '%s/%s/%s/%s' % (BASE_FILES, get_org(), get_proj(), quote(resource_id))
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
        token (str): Optional OAuth token.

    Returns:
        File revision.
    '''
    return _get_file_metadata(resource_id, tag, token)['_rev']


def get_file_name(resource_id, tag=None, token=None):
    '''Get file rev.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        token (str): Optional OAuth token.

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
        token (str): OAuth token.

    Returns:
        Identifier of the uploaded file.
    '''
    if resource_id:
        url = '%s/%s/%s/%s' % (BASE_FILES, get_org(), get_proj(), quote(resource_id))
        response = requests.put(url,
                                headers=_get_headers(token),
                                params={'rev': rev if rev else None},
                                files={'file': (name, data, content_type)})
    else:
        url = '%s/%s/%s' % (BASE_FILES, get_org(), get_proj())
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
        token (str): Optional OAuth token.

    Returns:
        Raw response.
    '''
    url = '%s/%s/%s/%s' % (BASE_FILES, get_org(), get_proj(), quote(resource_id))

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
