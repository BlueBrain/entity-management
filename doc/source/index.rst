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

**Important environment variables to establish Nexus context**

Entity management library makes use of environment variables to know which Knowledge Graph
instance, organization and project to use. Also, for convenience, access token can be set
as environment variable and not explicitly provided with every method interacting with
nexus.

By default BBP Production Nexus instance is used. To use staging environment set
`NEXUS_BASE` to `https://bbp-nexus.epfl.ch/staging/v1`.
`NEXUS_ORG` variable sets the current organization. If nothing is set with this variable the
default value is: `myorg`. The `NEXUS_PROJ` variable sets the project to use. The default value is:
`myproj`.

Access token can be provided with the `NEXUS_TOKEN` environment variable. The following code
snippet can be used to obtain access token for the BBP Nexus instance using
`python-keycloak <https://python-keycloak.readthedocs.io/en/latest>`_ library:

.. code-block:: python

    from keycloak import KeycloakOpenID
    openid = KeycloakOpenID(server_url='https://bbpauth.epfl.ch/auth/',
                            client_id='my-client-id',
                            realm_name='BBP')
    access_token = openid.token(USERNAME, PASSWORD)['access_token']

To establish nexus context programmatically use the :mod:`state.py<entity_management.state>` module
functions.


**Simulation domain entities**

Below you can find the class diagram of the entities available in the
simulation domain. By clicking on the class, you will be taken to the class
constructor documentation. From there you can see which parameters
are optional (having `None` as default value), and which must be
provided in order to construct the object. Keep in mind that some
of the class attributes are defined in the parent classes. The link to parent
class is available under `Bases` section.

.. inheritance-diagram:: entity_management.simulation
   :top-classes: entity_management.simulation._Entity
   :parts: 1


.. toctree::
   :hidden:
   :maxdepth: 2

   Home <self>
   prov_patterns
   examples
   api
   cli
