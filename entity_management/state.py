'''State of the interaction with nexus. For example current project to use.

Nexus organization, project and access token are initialized from the corresponding
environment variables. They can be updated using setter functions from this module.
'''
import os

import jwt

from keycloak import KeycloakOpenID

BASE = os.getenv('NEXUS_BASE', 'https://bbp.epfl.ch/nexus/v1')

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
    elif token_info['typ'] in ['Offline', 'Refresh']:
        OFFLINE_TOKEN = token
        refresh_token()


# Initialize token from the environment
set_token(os.getenv('NEXUS_TOKEN', None))


def get_org(org=None):
    '''Get current organization.

    Args:
        org (str): optional Organization.

    Returns:
        ``org`` argument. If it was not provided then returns the value of global ``Organization``
        variable which is initialized from NEXUS_ORG environment variable.
    '''
    if org:
        return org
    return ORG


def set_org(org):
    '''Set global ``Organization`` variable.'''
    global ORG  # pylint: disable=global-statement
    ORG = org


def get_proj(proj=None):
    '''Get current project.

    Args:
        proj (str): optional Project.

    Returns:
        ``proj`` argument. If it was not provided then returns the value of global ``Project``
        variable which is initialized from NEXUS_PROJ environment variable.
    '''
    if proj:
        return proj
    return PROJ


def set_proj(proj):
    '''Set global ``Project`` variable.'''
    global PROJ  # pylint: disable=global-statement
    PROJ = proj


def set_base(base):
    '''Set global ``Base`` url variable.'''
    global BASE  # pylint: disable=global-statement
    BASE = base


def get_base_resources(base=None):
    '''Get url to nexus environment base for the resources.

    Args:
        base (str): optional ``Base`` url of nexus instance to be used.

    Returns:
        Nexus resources endpoint url is either based on ``base`` function argument provided
        or based on the global ``BASE`` variable value which is initialized from NEXUS_BASE
        environment variable.
    '''
    if base:
        return '%s/resources' % base
    return '%s/resources' % BASE


def get_base_views(base=None):
    '''Get url to nexus environment base for the views.

    Args:
        base (str): optional ``Base`` url of nexus instance to be used.

    Returns:
        Nexus views endpoint url is either based on ``base`` function argument provided
        or based on the global ``BASE`` variable value which is initialized from NEXUS_BASE
        environment variable.
    '''
    if base:
        return '%s/views' % base
    return '%s/views' % BASE


def get_base_url(base=None, org=None, proj=None):
    '''Get base url.'''
    return '%s/%s/%s/_' % (get_base_resources(base), get_org(org), get_proj(proj))


def get_sparql_url(base=None, org=None, proj=None):
    '''Get base url.'''
    return '%s/%s/%s/graph/sparql' % (get_base_views(base), get_org(org), get_proj(proj))


def get_base_files(base=None):
    '''Get url to nexus environment base for the files.

    Args:
        base (str): optional ``Base`` url of nexus instance to be used.

    Returns:
        Nexus files endpoint url either based on ``base`` argument provided or based on the
        global ``Base`` variable value which is initialized from NEXUS_BASE environment variable.
    '''
    if base:
        return '%s/files' % base
    return '%s/files' % BASE
