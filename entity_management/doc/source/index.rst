.. entity_management documentation master file, created by
   sphinx-quickstart on Fri Aug  4 11:34:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to simulation domain entity_management's documentation!
===============================================================

Simulation domain nexus access layer provides a set of python classes which
map to nexus entities validated by corresponding nexus schemas in the
knowledge graph. Through methods available in the classes entity_management
library client can make simple queries to nexus and retrieve data. In order
to create data in nexus, instantiate the relevant python classes
and invoke `save` method. When python classes are instantiated the best effort
will be made to perform necessary validation so that nexus doesn't reject
data when the `save` method is invoked.

Below you can find the class diagram of the entities available in the
simulation domain. By clicking on the class, you'll be taken to the class
constructor documentation. From there you'll be able to see which parameters
can be optional(having `None` as default value) and the ones which have to be
provided in order to be able to construct the object. Have in mind that some
of the class attributes are defined in the parent classes. The link to parent
class is available under `Bases` section.

By default BBP Staging Nexus instance is accessed. Provide environment variables
`NEXUS_BASE(default=https://bbp-nexus.epfl.ch/staging/v0)` and
`NEXUS_ORG(default=neurosciencegraph)` to specify nexus instance and organization
context.


.. inheritance-diagram:: entity_management.base entity_management.prov entity_management.simulation.circuit entity_management.simulation.cell
   :parts: 2


Contents:

.. toctree::
   :maxdepth: 2

   examples
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
