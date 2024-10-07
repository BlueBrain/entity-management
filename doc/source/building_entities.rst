Building Entities
=================

.. _model_building_config:

ModelBuildingConfig
-------------------

The ``ModelBuildingConfig`` serves as the master configuration for the entire model building workflow, encompassing all generator configurations required at each stage of the process.

.. graphviz::

   digraph foo{

    rankdir = "LR"
    splines = "ortho"

    ModelBuildingConfig[
        shape = Mrecord style = filled fillcolor = lemonchiffon
    ]

    CellCompositionConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    CellPositionConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    MorphologyAssignmentConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    MEModelConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    MacroConnectomeConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    MicroConnectomeConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    SynapseConfig [
        shape = Mrecord style = filled fillcolor = lemonchiffon
        width = 3
    ]

    ModelBuildingConfig -> CellCompositionConfig [label="configs[cellCompositionConfig]", labelheight=2];
    ModelBuildingConfig -> CellPositionConfig [label="configs[cellPositionConfig]"];
    ModelBuildingConfig -> MorphologyAssignmentConfig [label="configs[morphologyAssignmentConfig]"];
    ModelBuildingConfig -> MEModelConfig [label="configs[meModelConfig]"];
    ModelBuildingConfig -> MacroConnectomeConfig [label="configs[macroConnectomeConfig]"];
    ModelBuildingConfig -> MicroConnectomeConfig [label="configs[microConnectomeConfig]"];
    ModelBuildingConfig -> SynapseConfig [label="configs[synapseConfig]"];

   }

.. _cell_composition_config:

CellCompositionConfig
---------------------

The ``CellCompositionConfig`` is a configuration entity that stores the settings used to update the densities of an existing ``CellComposition``.


Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variantDefinition
     - CWL definition to be used.
   * - inputs
     - Inputs to placement. A CellComposition entry.
   * - configuration
     - Overrides for the CellComposition input.

``inputs`` is used to list the base ``CellComposition`` that will be used and ``configuration`` to specify the optional overrides of which densities to modify.

To specify an overrides the region/mtype/etype combination must be specified as follows:


.. code-block:: json

  "overrides": {
    "http://api.brain-map.org/api/v2/data/Structure/23": {
      "hasPart": {
        "https://bbp.epfl.ch/ontologies/core/bmo/GenericExcitatoryNeuronMType": {
          "hasPart": {
            "https://bbp.epfl.ch/ontologies/core/bmo/GenericExcitatoryNeuronEType": {
              "composition": {
                "neuron": {
                  "density": 1200
                }
              }
            }
          }
        }
      }
    }
  }

There are two keys that can be used to update a density composition:

* density
* density_ratio

where ``density`` is used to update the voxels with the specific value and ``density-ratio`` adjusts the values relative to an existing density.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/cell_composition_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/cell_composition_config_distribution.json
   :language: json


.. _cell_position_config:

CellPositionConfig
------------------

The ``CellPositionConfig`` is a configuration entity that stores the settings used for placing cells in space.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variantDefinition
     - CWL definition to be used.
   * - inputs
     - Inputs to placement. Currently Empty.
   * - configuration
     - Placement algorithm configuration options.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/cell_position_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/cell_position_config_distribution.json
   :language: json

.. _morphology_assignment_config:

MorphologyAssignmentConfig
--------------------------

The ``MorphologyAssignmentConfig`` is a configuration entity that stores the settings used for assigning morphologies to a node population.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variantDefinition
     - CWL definitions to be used.
   * - defaults
     - Default configurations for synthesis and placeholders.
   * - configuration
     - Configuration for topological synthesis entries.

There are two main ways of asignment:

* placeholder_assignment: Use placeholder cells.
* topological_synthesis: Synthesize morphologies using topological branching information.

defaults
^^^^^^^^

The configurations for placeholders and synthesis are stored under ``defaults`` corresponding to the following entities:

* :ref:`CanonicalMorphologyModelConfig <canonical_morphology_model_config>`
* :ref:`PlaceholderMorphologyConfig <placeholder_morphology_config>`

which define a canonical model or placeholder morphologies for each (region, mtype) combination in the atlas.

.. code-block:: json

    "defaults": {
    "topological_synthesis": {
      "@id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/fae6eb46-3007-41c6-af69-941a82aada68",
      "@type": "CanonicalMorphologyModelConfig"
    },
    "placeholder_assignment": {
      "@id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/9503a07d-8337-48eb-8637-acc26b0f13bf",
      "@type": "PlaceholderMorphologyConfig"
    }


.. note::

   Both default configurations should be computed on the same Atlas Release and be in sync with each other.

configuration
^^^^^^^^^^^^^

In the ``configuration`` section only the (region, mtype) combinations that will be synthesized are listed:

.. code-block:: json

  "configuration": {
    "topological_synthesis": {
      "http://api.brain-map.org/api/v2/data/Structure/632": {
        "https://bbp.epfl.ch/ontologies/core/bmo/GenericExcitatoryNeuronMType": {}
      }
    }
  }


The entries in configuration determine which entries will be selected from the default :ref:`CanonicalMorphologyModelConfig <canonical_morphology_model_config>`.
By convention the rest of the entries will be assigned placeholders from the default :ref:`PlaceholderMorphologyConfig <placeholder_morphology_config>`.

It is also possible to specify overrides for the topological synthesis configuration as follows:

.. code-block:: json

  "configuration": {
    "topological_synthesis": {
      "http://api.brain-map.org/api/v2/data/Structure/632": {
        "https://bbp.epfl.ch/ontologies/core/bmo/GenericExcitatoryNeuronMType": {
          "@id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/canonicalmorphologymodels/dfda5210-39b5-428d-ac0c-43852f99df02",
          "overrides": {
            "apical_dendrite": {
              "randomness": 0.11,
              "step_size": {
                "norm": {
                  "mean": 7.6,
                  "std": 0.2
                }
              },
              "targeting": 0.34
            }
          }
        }
      }
    }
  }


Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/morphology_assignment_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/morphology_assignment_config_distribution.json
   :language: json


.. _me_model_config:

MEModelConfig
-------------

The ``MEModelConfig`` is a configuration entity that stores the settings used for assigning emodels to node populations with morphologies.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variantDefinition
     - CWL definitions to be used.
   * - defaults
     - Placeholder configurations for emodels.
   * - overrides
     - Overrides to placeholder emodel configuration.

defaults
^^^^^^^^

The defaults contain the following placeholder configurations:

* neurons_me_model: :ref:`PlaceholderEModelConfig <placeholder_emodel_config>`

overrides
^^^^^^^^^

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/me_model_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/me_model_config_distribution.json
   :language: json


.. _macro_connectome_config:

MacroConnectomeConfig
---------------------

The ``MacroConnectomeConfig`` is a configuration entity that stores the settings used for macroscopic connectome configuration.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - initial
     - Initial connectome configurations.
   * - overrides
     - Connectome overrides on the initial configuration.


Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/macro_connectome_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/macro_connectome_config_distribution.json
   :language: json


.. _micro_connectome_config:

MicroConnectomeConfig
---------------------

The ``MicroConnectomeConfig`` is a configuration entity that stores the settings used for microscopic connectome configuration.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variants
     - Variant CWL definitions for connectome algorithms.
   * - initial
     - Initial micro connectome configurations.
   * - overrides
     - Connectome overrides on the initial configuration.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/micro_connectome_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/micro_connectome_config_distribution.json
   :language: json


.. _synapse_config:

SynapseConfig
-------------

The ``SynapseConfig`` is a configuration entity that stores the settings for assigning synaptic parameters to circuits.

Distribution Keys
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Key
     - Explanation
   * - variantDefinition
     - Variant CWL definition information.
   * - defaults
     - Initial synaptic parameter configurations.
   * - configuration
     - Final synaptic parameter configuration.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/synapse_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/synapse_config_distribution.json
   :language: json


.. _canonical_morphology_model_config:

CanonicalMorphologyModelConfig
------------------------------

The ``CanonicalMorphologyModelConfig`` is a configuration entity that stores the canonical models for each (region, mtype) combination, used for topological synthesis.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/canonical_morphology_model_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/canonical_morphology_model_config_distribution.json
   :language: json


.. _placeholder_morphology_config:

PlaceholderMorphologyConfig
---------------------------

The ``PlaceholderMorphologyConfig`` is a configuration entity that stores placeholder morphologies for each (region, mtype) combination, used for morphology assignment.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/placeholder_morphology_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/placeholder_morphology_config_distribution.json
   :language: json


.. _placeholder_emodel_config:

PlaceholderEModelConfig
-----------------------

The ``PlaceholderEModelsConfig`` is a configuration entity that stores the placeholder emodels for each (region, etype) combination, used for emodel assignment.

Distribution Schema
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../entity_management/schemas/placeholder_emodel_config_distribution.yml
   :language: yaml

Distribution Example
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../tests/data/placeholder_emodel_config_distribution.json
   :language: json
