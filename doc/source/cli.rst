**********************
Command line interface
**********************

.. contents::


TOKEN is the OAuth2 optional access token. Provide it in case the endpoint has OAuth2 protected
access control. If token is available in the environment variable `NEXUS_TOKEN` it will be used
by default unless it was explicitly provided in the method argument.

Model building config
#####################

Get
***

Return significant values about the whole model building config structure.

.. code-block:: bash

    model-building-config get --id "https://bbp.epfl.ch/neurosciencegraph/data/modelconfigurations/1921aaae-69c4-4366-ae9d-7aa1453f2158"
    # OR
    model-building-config get --url "https://bbp.epfl.ch/nexus/v1/resources/bbp/mmb-point-neuron-framework-model/_/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fmodelconfigurations%2F1921aaae-69c4-4366-ae9d-7aa1453f2158"

.. code-block:: python
    {
        "configs": {
            "Cell composition config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2F8a9b7a11-3629-48d4-aeba-bd991c1696bd?rev=1016",
                "description": "NA",
                "generatorName": "cell_composition",
                "name": "Cell composition config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "cell_composition_summary": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/71513f09-2834-4749-9a1c-e2460232c890",
                        "cell_composition_volume": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/da949d3c-b10a-4ded-89ee-041d928517d0",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/4ecd6153-9ce5-4adb-9d82-b0df2d2d3322",
                    }
                ],
            },
            "Cell position config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2F802f7149-43be-480c-97ed-1d3017c7e131?rev=3",
                "description": "NA",
                "generatorName": "cell_position",
                "name": "Cell position config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/project/proj134/workflow-outputs/14092023-d23c8bf4-f805-4c90-a1a2-5e7cfe839df5/cellPositionConfig/root/build/config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/e1ae5eb4-51f0-4f52-b339-94805e894cf1",
                    }
                ],
            },
            "EModel assignment config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2F54e4068d-48b8-492c-9e2d-49be9e5bfc3f?rev=5",
                "description": None,
                "generatorName": "placeholder",
                "name": "EModel assignment config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/project/proj134/workflow-outputs/14092023-d23c8bf4-f805-4c90-a1a2-5e7cfe839df5/eModelAssignmentConfig/root/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/95889eef-89f8-4625-a074-c6006e9f1808",
                    }
                ],
            },
            "MacroConnectomeConfig": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fc65236c6-386f-44d4-9c7f-4f71c1965aa8?rev=3",
                "description": None,
                "generatorName": "connectome",
                "name": "MacroConnectomeConfig",
                "used_in": [],
            },
            "Micro-connectome configuration": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2F1c967425-693f-48b6-8440-f4f9cb824b5b?rev=5",
                "description": None,
                "generatorName": "connectome",
                "name": "Micro-connectome " "configuration",
                "used_in": [],
            },
            "MorphologyAssignmentConfig": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fnexus%2Fv1%2Fresources%2Fbbp%2Fmmb-point-neuron-framework-model%2F_%2Fcd5a45d6-bc0d-42c8-9736-f5cb74607cfd?rev=20",
                "description": None,
                "generatorName": "mmodel",
                "name": "MorphologyAssignmentConfig",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/project/proj134/workflow-outputs/14092023-d23c8bf4-f805-4c90-a1a2-5e7cfe839df5/morphologyAssignmentConfig/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/2d386fab-fa41-4a11-b006-89aeb624bdba",
                    }
                ],
            },
            "SynapseConfig": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fab9fd41b-ce10-42bb-9b69-c505543d8f7f?rev=6",
                "description": None,
                "generatorName": "connectome_filtering",
                "name": "SynapseConfig",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/project/proj134/workflow-outputs/14092023-d23c8bf4-f805-4c90-a1a2-5e7cfe839df5/synapseConfig/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/68ab6f28-8ab0-4e53-a2a5-9052ed541c93",
                    }
                ],
            },
        },
        "description": "Latest supported by workflow.",
        "name": "Release 23.01",
    }
