#modules that are installable (ie: ones w/ setup.py)
INSTALL_MODULES=entity_management

#modules that have tests
TEST_MODULES=entity_management

# Ignore directories for pep8 and pylint (on top of tests and doc)
IGNORE_LINT=entity_management/apps|server

#packages to cover
COVER_PACKAGES=entity_management
#documentation to build, separated by spaces
DOC_MODULES=entity_management/doc
DOC_REPO=ssh://bbpcode.epfl.ch/infra/jekylltest

DOC_REQS?=sphinx==1.6.7 sphinxcontrib-napoleon==0.6.1

PYTHON_PIP_VERSION=pip==9.0.1

OPTIONAL_FEATURES:='[extension_tests]'

##### DO NOT MODIFY BELOW #####################

CI_REPO?=ssh://bbpcode.epfl.ch/platform/ContinuousIntegration.git
CI_DIR?=ContinuousIntegration

FETCH_CI := $(shell \
        if [ ! -d $(CI_DIR) ]; then \
            git clone $(CI_REPO) $(CI_DIR) > /dev/null ;\
        fi;\
        echo $(CI_DIR) )
include $(FETCH_CI)/python/common_makefile
