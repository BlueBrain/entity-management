'''Settings module'''
import os

from rdflib import Namespace

JSLD_ID = '@id'
JSLD_TYPE = '@type'
JSLD_CTX = '@context'
JSLD_REV = 'nxv:rev'
JSLD_DEPRECATED = 'nxv:deprecated'

BASE = os.getenv('NEXUS_BASE', 'https://bbp-nexus.epfl.ch/staging/v1')
DEFAULT_TAG = 'v0.1.0'

USERINFO = os.getenv('NEXUS_USERINFO', 'https://bbp-nexus.epfl.ch/staging/v1/identities')

# if provided, nexus entities will have wasAttributedTo set to this AGENT
# this is helpful when entity management library is used in some context which
# already established some provenance regarding currently running agent
AGENT = os.getenv('NEXUS_AGENT', None)

BASE_CTXS = BASE + '/contexts'

ORG = os.getenv('NEXUS_ORG', 'myorg')

PROJ = os.getenv('NEXUS_PROJ', 'myproj')

NSG_CTX = BASE_CTXS + '/neurosciencegraph/core/data/v1.0.7'

BASE_SCHEMAS = BASE + '/schemas'
BASE_RESOLVERS = BASE + '/resolvers'
BASE_VIEWS = BASE + '/views'
BASE_FILES = BASE + '/files'
BASE_RESOURCES = BASE + '/resources'
BASE_PROJECTS = BASE + '/projects'
BASE_ORGS = BASE + '/orgs'

RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
PROV = Namespace('http://www.w3.org/ns/prov#')
NSG = Namespace('https://neuroshapes.org/')
DASH = Namespace('https://neuroshapes.org/dash/')
NXV = Namespace('https://bluebrain.github.io/nexus/vocabulary/')
