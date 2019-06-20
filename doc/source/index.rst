Welcome to entity_management's documentation!
=============================================

Entity management library provides a set of python classes which
map to nexus entities possibly validated by corresponding nexus schemas
in the knowledge graph.

Entity management library provides methods to perform simple queries to nexus
and retrieve data. In order to create data in nexus, instantiate the relevant
python classes and invoke `publish` method. When python classes are instantiated
the best effort will be made to perform necessary validation so that nexus
doesn't reject data when the `publish` method is invoked. See: :doc:`examples`

Below you can find the class diagram of the entities available in the
simulation domain. By clicking on the class, you'll be taken to the class
constructor documentation. From there you'll be able to see which parameters
can be optional(having `None` as default value) and the ones which have to be
provided in order to be able to construct the object. Have in mind that some
of the class attributes are defined in the parent classes. The link to parent
class is available under `Bases` section.


**Important environment variables to establish Nexus context**:
Entity management makes use of environment variables to know which Knowledge Graph
instance, organization and project to use. Also, for convenience, access token can be set
as environment variable and not explicitly provided with every method interacting with
nexus.

By default BBP Production Nexus instance is used. To use staging environment set
`NEXUS_BASE` to `https://bbp-nexus.epfl.ch/staging/v1`. `NEXUS_ORG` variable sets the
organization to use with the default value: `myorg`. `NEXUS_PROJ` variable sets the
project to use with the default value: `myproj`.

Access token can be provided with the `NEXUS_TOKEN` environment variable. The following code
snippet can be used to obtain access token for the BBP Nexus instance using
`python-keycloak <https://python-keycloak.readthedocs.io/en/latest>`_ library:

.. code-block:: python

    from keycloak import KeycloakOpenID
    openid = KeycloakOpenID(server_url='https://bbpteam.epfl.ch/auth/',
                            client_id='bbp-nexus-public',
                            realm_name='BBP')
    access_token = openid.token(USERNAME, PASSWORD)['access_token']

For example in order to use HBP production nexus instance run your application
with the following environment variable set:
`NEXUS_BASE=https://nexus.humanbrainproject.org/v1`


**Simulation domain entities**:

.. inheritance-diagram:: entity_management.simulation
   :top-classes: entity_management.simulation._Entity
   :parts: 1


**Contents**:

.. toctree::
   :maxdepth: 2

   examples
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
