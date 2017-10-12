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

TESTS_REQUIRE = [
        'nose==1.3.0',
        'mock==1.0.1',
        ]

setup(
    name="entity-management",
    version=VERSION,
    install_requires=[
        'requests>=2.18,<3.0',
        ],
    tests_require=TESTS_REQUIRE,
    extras_require={
        'extension_tests': TESTS_REQUIRE,
    },
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
    download_url="https://bbpteam.epfl.ch/repository/devpi/+search?query=name%3Aentity-management",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'License :: Proprietary',
                 'Operating System :: POSIX',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Utilities',
                 ],
    scripts=['apps/entity-management.py',
             ],
)
