''' nexus access layer '''
import logging
import requests
from urllib import urlencode
from urlparse import urljoin
from entity_management.client import DEFAULT_CONFIG
L = logging.getLogger(__name__)

PROPERTY_NS = "bbpprodprop:"
WHITE_LIST_NEXUS = ['@id', '@type', 'rev']
# TODO only circuit is supported now.
CIRCUIT_SCHEMA = 'v0.0.8'
CIRCUIT_TYPE = 'bbprod:circuit'


def _map_from_raw(raw_properties):
    ''' return actual properties w/o namespace
    and a white listed properties of nexus
    '''
    ret = {}
    for k, v in raw_properties.items():
        if PROPERTY_NS == k[:len(PROPERTY_NS)]:
            ret[k[len(PROPERTY_NS):]] = v
        elif k in WHITE_LIST_NEXUS:
            ret[k] = v
    return ret


def _map_to_raw(properties):
    ''' add a namespace to the raw_properties and add nexus boilerplate '''
    raw_properties = {
        '@context': {
            '@vocab': 'https://bbp-nexus.epfl.ch/voc/productionentity/core/',
            'bbpprodprop':
            'https://bbp-nexus.epfl.ch/voc/bbp/productionentity/prop/core/',
            'bbprod':
            'https://bbp-nexus.epfl.ch/voc/bbp/productionentity/core/'
        },
        '@type': CIRCUIT_TYPE
    }
    for k, v in properties.items():
        if k in WHITE_LIST_NEXUS:
            raw_properties[k] = v
        else:
            raw_properties[PROPERTY_NS + k] = v
    return raw_properties


def _build_url(type_, versioned=True, config=DEFAULT_CONFIG):
    ''' get the nexus url for a particular type '''
    paths = [
        'data',
        'bbp',  # organization
        'core',  # domain
        type_
    ]
    if versioned:
        paths.append(CIRCUIT_SCHEMA)
    return urljoin(config.environment['nexus_url'], '/'.join(paths))


def _from_ids_to_url(ids):
    ''' convert nexus ids to a url '''
    if isinstance(ids, basestring):
        return ids
    return ids['@id'] + '?' + urlencode({'rev': str(ids['rev'])})


def get_entity(ids):
    ''' remove namespace from keys and other boilerplate '''
    get_url = _from_ids_to_url(ids)
    req = requests.get(get_url)
    req.raise_for_status()
    return _map_from_raw(req.json())


def get_entities(type_, from_, size, config=DEFAULT_CONFIG):
    ''' get a paginated list of entities without namespace and nexus additions'''
    url = _build_url(type_, False, config)
    req = requests.get(url, params={'from': from_, 'size': size})
    req.raise_for_status()
    results = req.json()['results']
    results_id = [r['resultId'] for r in results]
    # TODO replace that when properties are available in result
    res_properties = [get_entity(r_id) for r_id in results_id]
    return res_properties


def register_entity(type_, properties, config=DEFAULT_CONFIG):
    ''' create an entity in nexus based on the schema providing properties w/o namespace '''
    url = _build_url(type_, True, config)
    body = _map_to_raw(properties)
    req = requests.post(url, json=body)
    req.raise_for_status()
    return req.json()


def update_entity(ids, properties):
    ''' update an entity in nexus providing properties w/o namespace '''
    body = _map_to_raw(properties)
    url = _from_ids_to_url(ids)
    req = requests.put(url, json=body)
    req.raise_for_status()
    return req.json()
