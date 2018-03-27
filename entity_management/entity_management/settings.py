'''Settings module'''
import os

JSLD_ID = '@id'
JSLD_REV = 'nxv:rev'
JSLD_DEPRECATED = 'nxv:deprecated'

BASE = os.getenv('NEXUS_BASE', 'https://bbp-nexus.epfl.ch/staging/v0')
VERSION = 'v0.1.0'

BASE_CTXS = BASE + '/contexts'

ORG = os.getenv('NEXUS_ORG', 'neurosciencegraph')

NSG_CTX = BASE_CTXS + '/neurosciencegraph/core/data/v0.3.0'
ENTITY_CTX = NSG_CTX

BASE_SCHEMAS = BASE + '/schemas'

BASE_DATA = BASE + '/data'
DATA_SIM = BASE_DATA + '/' + ORG + '/simulation'
