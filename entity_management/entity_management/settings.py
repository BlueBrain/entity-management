'''Settings module'''
import os

JSLD_ID = '@id'
JSLD_REV = 'nxv:rev'
JSLD_DEPRECATED = 'nxv:deprecated'

TOKEN = os.getenv('NEXUS_TOKEN')

BASE = os.getenv('NEXUS_BASE', 'https://bbp-nexus.epfl.ch/dev/v0')
VERSION = 'v0.1.0'

BASE_CTXS = BASE + '/contexts'

ORG = os.getenv('NEXUS_ORG', 'neurosciencegraph')

# ENTITY_CTX = BASE_CTXS + ORG + 'core/data/' + VERSION
NSG_CTX = BASE_CTXS + '/' + ORG + '/core/data/' + VERSION
ENTITY_CTX = BASE_CTXS + '/bbp/core/entity/' + VERSION
# NSG_CTX = BASE_CTXS + '/bbp/neurosciencegraph/core/' + VERSION

BASE_SCHEMAS = BASE + '/schemas'

BASE_DATA = BASE + '/data'
DATA_SIM = BASE_DATA + '/' + ORG + '/simulation'
