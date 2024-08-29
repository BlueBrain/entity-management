entity-management
=================

Library for handling NEXUS entity dataclass definitions.

Documentation
=============

* `latest release <https://entity-management.readthedocs.io/en/stable/>`_
* `latest snapshot <https://entity-management.readthedocs.io/en/latest/>`_

Installation
============

entity-management can be pip installed with the following command:

.. code-block:: bash

    $ pip install entity-management

Tests
=====

.. code-block:: bash

    pip install tox
    tox

Logging
=======

To log responses from Nexus in a pretty format, you may want to ensure that the package `devtools <https://github.com/samuelcolvin/python-devtools>`__ is installed, and set the environment variables:

.. code-block:: bash

    PY_DEVTOOLS_ENABLE=1
    PY_DEVTOOLS_HIGHLIGHT=1

Acknowledgements
================

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

For license and authors, see LICENSE.txt and AUTHORS.txt respectively.

Copyright (c) 2022-2024 Blue Brain Project/EPFL
