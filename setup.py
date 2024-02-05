#!/usr/bin/env python
""" entity_management setup """
from setuptools import setup, find_packages

from entity_management.version import VERSION


TESTS_REQUIRE = [
    "nose==1.3.0",
    "mock==1.0.1",
    "responses",
]

setup(
    name="entity-management",
    version=VERSION,
    install_requires=[
        "requests",
        "attrs",
        "python-dateutil",
        "sparqlwrapper",
        "rdflib",
        "pyjwt",
        "python-keycloak",
        "devtools[pygments]",
        "click",
    ],
    python_requires=">=3.10",
    tests_require=TESTS_REQUIRE,
    extras_require={
        "extension_tests": TESTS_REQUIRE,
    },
    packages=find_packages(),
    include_package_data=True,
    author="NSE (Neuroscientific Software Engineering)",
    author_email="bbp-ou-nse@groupes.epfl.ch",
    description="Access to production entity management",
    long_description="Access to production entity management",
    license="BBP-internal-confidential",
    entry_points={
        "console_scripts": [
            "entity-management=entity_management.cli.base:cli",
        ]
    },
    keywords=(
        "computational neuroscience",
        "simulation",
        "analysis",
        "nexus",
        "parameters",
        "BlueBrainProject",
    ),
    url="http://bluebrain.epfl.ch",
    download_url="https://bbpteam.epfl.ch/repository/devpi/+search?query=name%3Aentity-management",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: Proprietary",
        "Operating System :: POSIX",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
)
