'''New nexus access layer'''
from __future__ import print_function

import re
import logging
import os
import sys
from email.header import decode_header
from functools import wraps
from pprint import pprint
import json as js

from six import PY2, iteritems, text_type

import requests

from SPARQLWrapper import SPARQLWrapper, JSON, POST, POSTDIRECTLY

from entity_management.util import quote
from entity_management.state import (get_base_resources, get_base_files, get_org, get_proj,
                                     get_token, refresh_token, has_offline_token, get_sparql_url)
from entity_management.settings import USERINFO, DASH, NSG, JSLD_TYPE

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
def get_type_from_id(resource_id, base=None, org=None, proj=None, token=None):
    '''Get type which corresponds to the id_url'''
    url = '%s/%s/%s/_/%s' % (get_base_resources(base),
                             get_org(org),
                             get_proj(proj),
                             quote(resource_id))
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
    return response.json(object_hook=_byteify)


def _get_files_endpoint():
    return ''


@_nexus_wrapper
def _get_file_metadata(resource_id, tag=None,
                       base=None, org=None, proj=None, token=None):
    '''Helper function'''
    url = '%s/%s/%s/%s' % (get_base_files(base), get_org(org), get_proj(proj), quote(resource_id))
    response = requests.get(url,
                            headers=_get_headers(token),
                            params={'tag': tag if tag else None})

    response.raise_for_status()
    return response.json(object_hook=_byteify)


def get_file_rev(resource_id, tag=None,
                 base=None, org=None, proj=None, token=None):
    '''Get file rev.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        File revision.
    '''
    return _get_file_metadata(resource_id, tag=tag,
                              base=base, org=org, proj=proj, token=token)['_rev']


def get_file_location(resource_id, tag=None,
                      base=None, org=None, proj=None, token=None):
    '''Get file location.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        File revision.
    '''
    return _get_file_metadata(resource_id, tag=tag,
                              base=base, org=org, proj=proj, token=token).get('_location')


def get_file_name(resource_id, tag=None,
                  base=None, org=None, proj=None, token=None):
    '''Get file rev.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        File name.
    '''
    return _get_file_metadata(resource_id, tag=tag,
                              base=base, org=org, proj=proj, token=token)['_filename']


@_nexus_wrapper
def upload_file(name, data, content_type, resource_id=None, storage_id=None, rev=None,
                base=None, org=None, proj=None, token=None):
    '''Upload file.

    Args:
        name (str): File name.
        data (file): File like data stream.
        content_type (str): Content type of the data stream.
        resource_id (str): Optional nexus id of the file.
        storage_id (str): Optional identifier of the storage backend where the file will be stored.
            If not provided, the project's default storage is used.
        rev (int): If you are reuploading file this needs to match current revision of the file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): OAuth token.

    Returns:
        Identifier of the uploaded file.
    '''
    if resource_id:
        url = '%s/%s/%s/%s' % (get_base_files(base),
                               get_org(org),
                               get_proj(proj),
                               quote(resource_id))
        response = requests.put(url,
                                headers=_get_headers(token),
                                params={'rev': rev if rev else None,
                                        'storage': storage_id if storage_id else None},
                                files={'file': (name, data, content_type)})
    else:
        url = '%s/%s/%s' % (get_base_files(base), get_org(org), get_proj(proj))
        response = requests.post(url,
                                 headers=_get_headers(token),
                                 params={'storage': storage_id if storage_id else None},
                                 files={'file': (name, data, content_type)})

    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_nexus_wrapper
def link_file(name, file_path, content_type, resource_id=None, storage_id=None,
              base=None, org=None, proj=None, token=None):
    '''Link file.

    Args:
        name (str): File name.
        file_path (str): File path.
        content_type (str): Content type of the data stream.
        resource_id (str): Optional nexus id of the file.
        storage_id (str): Optional identifier of the storage backend where the file will be stored.
            If not provided, the project's default storage is used.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): OAuth token.

    Returns:
        Identifier of the uploaded file.
    '''
    params = {'storage': storage_id if storage_id else None}
    json = {'filename': name, 'path': file_path, 'mediaType': content_type}
    if resource_id:
        url = '%s/%s/%s/%s' % (get_base_files(base),
                               get_org(org),
                               get_proj(proj),
                               quote(resource_id))
        response = requests.put(url, headers=_get_headers(token), params=params, json=json)
    else:
        url = '%s/%s/%s' % (get_base_files(base), get_org(org), get_proj(proj))
        response = requests.post(url, headers=_get_headers(token), params=params, json=json)

    response.raise_for_status()
    return response.json(object_hook=_byteify)


@_nexus_wrapper
def download_file(resource_id, path, file_name=None, tag=None, rev=None,
                  base=None, org=None, proj=None, token=None):
    '''Download file.

    Args:
        resource_id (str): Nexus id of the file.
        path (str): Path where to save the file.
        file_name (str): Provide file name to use instead of original name.
        tag (str): Provide tag to fetch specific file.
        rev (int): Provide revision number to fetch specific file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        str: Path to the downloaded file.
    '''
    url = '%s/%s/%s/%s' % (get_base_files(base), get_org(org), get_proj(proj), quote(resource_id))

    response = requests.get(url,
                            headers=_get_headers(token, accept=None),
                            params={'tag': tag if tag else None,
                                    'rev': rev if rev else None},
                            stream=True)
    try:
        response.raise_for_status()
        if file_name is None:
            content_disposition = response.headers.get('content-disposition')
            match = re.findall('filename="(.+)"', content_disposition)[0]
            encoded_file_name, encoding = decode_header(match)[0]
            file_name = encoded_file_name.decode(encoding)
        file_ = os.path.join(path, file_name)
        with open(file_, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    finally:
        response.close()

    return os.path.join(os.path.realpath(path), file_name)


@_nexus_wrapper
def file_as_dict(resource_id, tag=None, rev=None,
                 base=None, org=None, proj=None, token=None):
    '''Stream file.

    Args:
        resource_id (str): Nexus ID of the file.
        tag (str): Provide tag to fetch specific file.
        rev (int): Provide revision number to fetch specific file.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        Raw response.
    '''
    url = '%s/%s/%s/%s' % (get_base_files(base), get_org(org), get_proj(proj), quote(resource_id))

    response = requests.get(url,
                            headers=_get_headers(token, accept=None),
                            params={'tag': tag if tag else None,
                                    'rev': rev if rev else None},
                            stream=True)
    try:
        response.raise_for_status()
        response.raw.decode_content = True
        return js.load(response.raw)
    finally:
        response.close()


@_nexus_wrapper
def sparql_query(query, base=None, org=None, proj=None, token=None):
    '''Execute SPARQL query.

    Args:
        query (str): SPARQL query.
        base (str): Nexus instance base url.
        org (str): Nexus organization.
        proj (str): Nexus project.
        token (str): Optional OAuth token.

    Returns:
        Json response.
    '''
    endpoint = SPARQLWrapper(get_sparql_url(base, org, proj))
    endpoint.addCustomHttpHeader('authorization', 'bearer %s' % token)
    endpoint.setMethod(POST)
    endpoint.setReturnFormat(JSON)
    endpoint.setRequestMethod(POSTDIRECTLY)
    endpoint.setQuery(query)
    result = endpoint.query()
    return result._convertJSON()
