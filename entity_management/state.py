'''State of the interaction with nexus. For example current project to use.

Nexus organization, project and access token are initialized from the corresponding
environment variables. They can be updated using setter functions from this module.
'''
import os

import jwt

from keycloak import KeycloakOpenID

KEYCLOAK_SECRET = os.getenv('KC_SCR', None)

TOKEN = os.getenv('NEXUS_TOKEN', None)  # can be access token or offline if running in bbp-workflow
ORG = os.getenv('NEXUS_ORG', 'myorg')
PROJ = os.getenv('NEXUS_PROJ', 'myproj')

ACCESS_TOKEN = None
OFFLINE_TOKEN = None

KEYCLOAK = KeycloakOpenID(server_url='https://bbpteam.epfl.ch/auth/',
                          client_id='bbp-workflow',
                          client_secret_key=KEYCLOAK_SECRET,
                          realm_name='BBP')


def get_token():
    '''Get access token.'''
    return ACCESS_TOKEN


def has_offline_token():
    '''Checks if offline token is available.'''
    return OFFLINE_TOKEN is not None


def refresh_token():
    '''Get new access token from the offline token.'''
    global ACCESS_TOKEN  # pylint: disable=global-statement
    ACCESS_TOKEN = KEYCLOAK.refresh_token(OFFLINE_TOKEN)['access_token']
    return ACCESS_TOKEN


def set_token(token):
    '''Sets the token for interaction with Nexus API.'''
    global ACCESS_TOKEN, OFFLINE_TOKEN  # pylint: disable=global-statement

    if token is None:
        return

    token_info = jwt.decode(token, verify=False)

    if token_info['typ'] == 'Bearer':
        ACCESS_TOKEN = token
    elif token_info['typ'] == 'Offline':
        OFFLINE_TOKEN = token
        refresh_token()


# Initialize token from the environment
set_token(os.getenv('NEXUS_TOKEN', None))


def get_org():
    '''Get current organization.'''
    return ORG


def set_org(org):
    '''Set current organization.'''
    global ORG  # pylint: disable=global-statement
    ORG = org


def get_proj():
    '''Get current project.'''
    return PROJ


def set_proj(proj):
    '''Set current project.'''
    global PROJ  # pylint: disable=global-statement
    PROJ = proj
