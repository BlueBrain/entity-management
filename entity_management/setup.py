#!/usr/bin/env python
""" entity_management setup """
import ast
import os

from setuptools import setup


############ VERSION FINDING
def get_version(version_filepath):
    '''extract version information from a version.py file'''
    VERSION_VAR_NAME = 'VERSION'
    with open(version_filepath, 'rU') as version_file:
        tree = compile(
            version_file.read(), version_filepath, 'exec', ast.PyCF_ONLY_AST)

    version = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if (isinstance(node.targets[0], ast.Name) and
                  isinstance(node.value, ast.Str)):
                if node.targets[0].id == VERSION_VAR_NAME:
                    version = node.value.s

    if version is None:
        raise Exception('Missing VERSION string (must be uppercase)')

    return version

VERSION = get_version(os.path.join(os.path.dirname(__file__),
                                   'entity_management/version.py'))

############ REQUIREMENTS FINDING
BASEDIR = os.path.dirname(os.path.abspath(__file__))
REQS = []
EXTRA_REQS_PREFIX = 'requirements_'
EXTRA_REQS = {}

import pip
from pip.req import parse_requirements
from optparse import Option


def parse_reqs(reqs_file):
    ''' parse the requirements '''
    options = Option('--workaround')
    options.skip_requirements_regex = None
    # Hack for old pip versions: Versions greater than 1.x
    # have a required parameter "sessions" in parse_requierements
    if pip.__version__.startswith('1.'):
        install_reqs = parse_requirements(reqs_file, options=options)
    else:
        from pip.download import PipSession  # pylint:disable=E0611
        options.isolated_mode = False
        install_reqs = parse_requirements(reqs_file,  # pylint:disable=E1123
                                          options=options,
                                          session=PipSession)
    return [str(ir.req) for ir in install_reqs]

REQS = parse_reqs(os.path.join(BASEDIR, 'requirements.txt'))

# look for extra requirements (ex: requirements_bbp.txt)
for file_name in os.listdir(BASEDIR):
    if not file_name.startswith(EXTRA_REQS_PREFIX):
        continue
    base_name = os.path.basename(file_name)
    (extra, _) = os.path.splitext(base_name)
    extra = extra[len(EXTRA_REQS_PREFIX):]
    EXTRA_REQS[extra] = parse_reqs(file_name)

setup(
    name="entity-management",
    version=VERSION,
    install_requires=REQS,
    extras_require=EXTRA_REQS,
    packages=['entity_management',
              ],
    include_package_data=True,
    author="NSE Team",
    author_email="bbp-ou-nse@groupes.epfl.ch",
    description="Access to production entity management",
    license="BBP-internal-confidential",
    keywords=('computational neuroscience',
              'simulation',
              'analysis',
              'visualization',
              'parameters',
              'BlueBrainProject'),
    url="http://bluebrain.epfl.ch",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'License :: Proprietary',
                 'Operating System :: POSIX',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Utilities',
                 ],
)
