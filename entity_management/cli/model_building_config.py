"""Command line interface for Model Building Config."""
import logging
from pprint import pprint
import click
from entity_management.model.building.config import ModelBuildingConfig
from entity_management.simulation import DetailedCircuit
from entity_management.atlas import CellComposition


@click.group()
@click.version_option()
@click.option("-v", "--verbose", count=True)
def cli(verbose):
    """The CLI object."""
    logging.basicConfig(
        level=(logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)],
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@cli.command()
@click.option("--url", "nexus_url", type=str, help="URL of the ModelBuildingConfig", required=False)
@click.option("--id", "nexus_id", type=str, help="ID of the ModelBuildingConfig", required=False)
def get(nexus_url, nexus_id):
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
    ):
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
            else:
                raise TypeError(f"Unexpected type of `used_in`: {type(used_in)}")

            result["configs"][config.name]["used_in"].append(used_in_result)

    pprint(result)
