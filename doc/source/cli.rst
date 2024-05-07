**********************
Command line interface
**********************

.. contents::


TOKEN is the OAuth2 optional access token. Provide it in case the endpoint has OAuth2 protected access control. 
The token needs to be provided in the environment variable `NEXUS_TOKEN`, along with variables `NEXUS_ORG` and `NEXUS_PROJ`.

Get
###

Return significant values about a Nexus object. Not all types are currently supported. 

If id or url is not explicitly specified, by including `--id` or `--url`, first attempt at finding the resource is made by id and if nothing is found a second attempt is made by url. 

.. code-block:: bash

    entity-management get "https://bbp.epfl.ch/neurosciencegraph/data/modelconfigurations/1921aaae-69c4-4366-ae9d-7aa1453f2158"
    # OR
    entity-management get --id "https://bbp.epfl.ch/neurosciencegraph/data/modelconfigurations/1921aaae-69c4-4366-ae9d-7aa1453f2158"
    # OR
    entity-management get "https://bbp.epfl.ch/nexus/v1/resources/bbp/mmb-point-neuron-framework-model/_/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fmodelconfigurations%2F1921aaae-69c4-4366-ae9d-7aa1453f2158"
    # OR
    entity-management get "https://bbp.epfl.ch/nexus/v1/resources/bbp/mmb-point-neuron-framework-model/_/https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fmodelconfigurations%2F1921aaae-69c4-4366-ae9d-7aa1453f2158"  --url

.. code-block:: python

    {
        "configs": {
            "Cell composition config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2F915a2ebc-534e-4d3d-8515-b7776686670e?rev=6",
                "description": "NA",
                "generatorName": "cell_composition",
                "name": "Cell composition config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "cell_composition_summary": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/3f3aaf7d-8363-45c7-b33e-0f95d552f17f",
                        "cell_composition_volume": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/7230e226-bb71-433a-b189-0fc438f246d5",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/847b2a62-7ca0-405a-a065-2a361cc86702",
                    }
                ],
            },
            "Cell position config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2Fc70c69d2-ccbd-4b57-a0e9-c00acf53d50a?rev=1",
                "description": "NA",
                "generatorName": "cell_position",
                "name": "Cell position config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/data/scratch/proj134/workflow-outputs/27102023-96f9af1a-a941-409d-bca4-eedb4153e9ea/cellPositionConfig/root/build/config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/df76acaf-ab50-4810-aa7f-0958a0f7d92a",
                    }
                ],
            },
            "EModel assignment config": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2Ff4c642b8-ac26-46ac-a00b-a1e32c9d56d7?rev=1",
                "description": None,
                "generatorName": "placeholder",
                "name": "EModel assignment config",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/data/scratch/proj134/workflow-outputs/27102023-96f9af1a-a941-409d-bca4-eedb4153e9ea/eModelAssignmentConfig/root/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/5613f0ba-90c5-4744-990f-9e92790c1853",
                    }
                ],
            },
            "MacroConnectomeConfig": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2Fc7c30811-fa82-4658-836a-c67d3f647c5a?rev=1",
                "description": None,
                "generatorName": "connectome",
                "name": "MacroConnectomeConfig",
                "used_in": [
                    {
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/f226ae37-85d4-4cd2-88c6-d899a0b69fd3"
                    }
                ],
            },
            "Micro-connectome configuration": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2F6859c6cf-ec20-4b56-940b-ecb508e7ff3d?rev=1",
                "description": None,
                "generatorName": "connectome",
                "name": "Micro-connectome " "configuration",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/data/scratch/proj134/workflow-outputs/27102023-96f9af1a-a941-409d-bca4-eedb4153e9ea/microConnectomeConfig/placeholder__v1/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/311f7081-ef2f-486c-b28d-1d86ba6e49f5",
                    }
                ],
            },
            "MorphologyAssignmentConfig": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2Fdc378c4d-a3de-4658-9b5d-477256be9fbf?rev=5",
                "description": None,
                "generatorName": "mmodel",
                "name": "MorphologyAssignmentConfig",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/data/scratch/proj134/workflow-outputs/27102023-96f9af1a-a941-409d-bca4-eedb4153e9ea/morphologyAssignmentConfig/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/638cba2e-ffe1-4db4-8bec-ccc99e8c8c4e",
                    }
                ],
            },
            "SynapseConfig.": {
                "content": "https://bbp.epfl.ch/nexus/v1/files/bbp/mmb-point-neuron-framework-model/https%3A%2F%2Fbbp.epfl.ch%2Fdata%2Fbbp%2Fmmb-point-neuron-framework-model%2F7d7fe556-087b-4fbe-9598-cb50cfc046aa?rev=2",
                "description": None,
                "generatorName": "connectome_filtering",
                "name": "SynapseConfig.",
                "used_in": [
                    {
                        "atlas_release_id": "https://bbp.epfl.ch/neurosciencegraph/data/4906ab85-694f-469d-962f-c0174e901885",
                        "circuit_url": "file:///gpfs/bbp.cscs.ch/data/scratch/proj134/workflow-outputs/30102023-f84c50a8-4f9c-4ddd-b8e8-444cf7acb948/synapseConfig/circuit_config.json",
                        "id": "https://bbp.epfl.ch/data/bbp/mmb-point-neuron-framework-model/b6e2a15b-cb89-44ba-8bf4-0ca92c49fc54",
                    }
                ],
            },
        },
        "description": "Fully supported by circuit building.",
        "name": "Workshop - antonel",
    }
