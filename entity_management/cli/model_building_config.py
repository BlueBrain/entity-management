"""Command line interface for Model Building Config."""
import logging
from pprint import pprint
from entity_management.config import MacroConnectomeConfig, ModelBuildingConfig
from entity_management.simulation import DetailedCircuit
from entity_management.atlas import CellComposition


def get_model_building_config(nexus_url, nexus_id):
    """Get ModelBuildingConfig instance from Nexus by URL or ID.

    Args:
        nexus_url (str): URL of the ModelBuildingConfig
        nexus_id (str): ID of the ModelBuildingConfig
    """
    if (nexus_url and nexus_id) or ((not nexus_url) and (not nexus_id)):
        raise ValueError("Exactly one of `url` or `id` must be set at a time.")

    if nexus_url:
        data = ModelBuildingConfig.from_url(url=nexus_url)
    if nexus_id:
        data = ModelBuildingConfig.from_id(resource_id=nexus_id)

    result = {
        "name": data.name,
        "description": data.description,
    }

    result["configs"] = {}

    for config in (
        data.configs.cellCompositionConfig,
        data.configs.cellPositionConfig,
        data.configs.morphologyAssignmentConfig,
        data.configs.eModelAssignmentConfig,
        data.configs.macroConnectomeConfig,
        data.configs.microConnectomeConfig,
        data.configs.synapseConfig,
        data.configs.meModelConfig,
    ):
        if config is None:
            continue

        result["configs"][config.name] = {
            "name": config.name,
            "description": config.description,
            "generatorName": config.generatorName,
            "content": config.distribution.contentUrl,
        }

        result["configs"][config.name]["used_in"] = []
        for used_in in config.used_in:
            used_in_result = {
                "id": used_in.generated.get_id(),
            }
            if isinstance(used_in.generated, DetailedCircuit):
                used_in_result[
                    "atlas_release_id"
                ] = used_in.generated.atlasRelease.get_id()
                used_in_result["circuit_url"] = used_in.generated.circuitConfigPath.url
            elif isinstance(used_in.generated, CellComposition):
                used_in_result[
                    "atlas_release_id"
                ] = used_in.generated.atlasRelease.get_id()
                used_in_result[
                    "cell_composition_summary"
                ] = used_in.generated.cellCompositionSummary.get_id()
                used_in_result[
                    "cell_composition_volume"
                ] = used_in.generated.cellCompositionVolume.get_id()
            elif isinstance(used_in.generated, MacroConnectomeConfig):
                pass  # the `generated` points to a clone of the MacroConnectomeConfig
            else:
                logging.warning(
                    "Unexpected type of `used_in` in \"%s\": %s (id: %s)",
                    config.name,
                    type(used_in.generated),
                    used_in.generated.get_id(),
                )

            result["configs"][config.name]["used_in"].append(used_in_result)

    pprint(result)
