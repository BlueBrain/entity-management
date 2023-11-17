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
@click.argument('identifier', type=str, nargs=1)
@click.option("--url", "url_hint", is_flag=True, default=False,
              help="Force identifier as nexus id.")
@click.option("--id", "id_hint", is_flag=True, default=False,
              help="Force identifier as nexus url.")
def get(identifier, url_hint, id_hint):
    """Get object instance from Nexus by URL or ID.

    Args:
        (str): URL or ID of the Nexus object
        url_hint (bool): Force identifier as nexus id
        id_hint (bool): Force identifier as nexus url
    """
    if (url_hint and id_hint):
        raise ValueError("At most one of `url` or `id` cat be set at a time.")

    nexus_id = None
    nexus_url = None

    if url_hint:
        data = load_by_url(identifier)
        nexus_url = identifier
    elif id_hint:
        data = load_by_id(identifier, cross_bucket=True)
        nexus_id = identifier
    else:
        data = load_by_id(identifier, cross_bucket=True)
        if not data:
            data = load_by_url(identifier)
            nexus_url = identifier
        else:
            nexus_id = identifier

    if not data:
        raise ValueError("Not found")

    types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]

    if "ModelBuildingConfig" in types:
        get_model_building_config(nexus_url, nexus_id)
    else:
        raise ValueError(f"Type `{types}` is not supported.")
