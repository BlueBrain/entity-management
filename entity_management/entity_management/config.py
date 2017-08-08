'''client config'''
import os

ENVIRONMENTS = {'prod': 'prod',
                'staging': 'staging',
                'local': 'local',
                }


class Config(object):
    '''Config for entity clients: contains environment, will contain credentials, etc'''
    def __init__(self, environment=None):
        if environment is None:
            environment = os.environ.get('ENTITY_ENVIRONMENT', 'prod')
        assert environment in ENVIRONMENTS, \
            'Environment must be one of %s' % ENVIRONMENTS.keys()
        self.environment = ENVIRONMENTS[environment]
