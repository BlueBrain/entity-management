"""Command line interface."""
import logging
import click
from entity_management.nexus import load_by_id, load_by_url
from entity_management.cli.model_building_config import get_model_building_config


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
@click.option("--url", "nexus_url", type=str, help="URL of the Nexus object", required=False)
@click.option("--id", "nexus_id", type=str, help="ID of the Nexus object", required=False)
def get(nexus_url, nexus_id):
    """Get object instance from Nexus by URL or ID.

    Args:
        nexus_url (str): URL of the Nexus object
        nexus_id (str): ID of the Nexus object
    """
    if (nexus_url and nexus_id) or ((not nexus_url) and (not nexus_id)):
        raise ValueError("Exactly one of `url` or `id` must be set at a time.")

    if nexus_url:
        data = load_by_url(nexus_url, cross_bucket=True)
    elif nexus_id:
        data = load_by_id(nexus_id, cross_bucket=True)

    types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]

    if "ModelBuildingConfig" in types:
        get_model_building_config(nexus_url, nexus_id)
    else:
        raise ValueError(f"Type `{types}` is not supported.")
