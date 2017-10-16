'''client config'''
import os

ENVIRONMENTS = {
    'prod': {
        'nexus_url': 'https://bbp-nexus.epfl.ch/staging/v0/'
    },
    'staging': {
        'nexus_url': 'https://bbp-nexus.epfl.ch/staging/v0/'
    },
}


class Config(object):
    '''Config for entity clients: contains environment, will contain credentials, etc'''

    def __init__(self, environment=None):
        if environment is None:
            environment = os.environ.get('ENTITY_ENVIRONMENT', 'prod')
        assert environment in ENVIRONMENTS, \
            'Environment must be one of %s' % ENVIRONMENTS.keys()
        self.environment = ENVIRONMENTS[environment]


DEFAULT_CONFIG = Config()
