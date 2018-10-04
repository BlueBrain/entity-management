'''Settings module'''
import os

JSLD_ID = '@id'
JSLD_TYPE = '@type'
JSLD_CTX = '@context'
JSLD_REV = 'nxv:rev'
JSLD_DEPRECATED = 'nxv:deprecated'

BASE = os.getenv('NEXUS_BASE', 'https://bbp-nexus.epfl.ch/staging/v0')
VERSION = 'v0.1.0'

USERINFO = os.getenv('NEXUS_USERINFO', 'https://bbp-nexus.epfl.ch/staging/v0/oauth2/userinfo')

# if provided, nexus entities will have wasAttributedTo set to this AGENT
# this is helpful when entity management library is used in some context which
# already established some provenance regarding currently running agent
AGENT = os.getenv('NEXUS_AGENT', None)

BASE_CTXS = BASE + '/contexts'

ORG = os.getenv('NEXUS_ORG', 'neurosciencegraph')

NSG_CTX = BASE_CTXS + '/neurosciencegraph/core/data/v1.0.4'

BASE_SCHEMAS = BASE + '/schemas'

BASE_DATA = BASE + '/data'
