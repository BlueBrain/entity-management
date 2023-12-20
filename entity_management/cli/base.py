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

    Command requires environmental variables NEXUS_ORG, NEXUS_PROJ and NEXUS_TOKEN.
    
    Args:
        (str): URL or ID of the Nexus object
        url_hint (bool): Force identifier as nexus id
        id_hint (bool): Force identifier as nexus url
    """
    if (url_hint and id_hint):
        raise ValueError("At most one of `url` or `id` cat be set at a time.")

    nexus_id = None
    nexus_url = None
    data = None

    if id_hint or not url_hint:
        try:
            data = load_by_id(identifier, cross_bucket=True)
            nexus_id = identifier
        except (AttributeError, ValueError, TypeError) as e:
            # if lookup by id was requested, propagate the exception
            if id_hint:
                raise e
    
    if data is None:
        data = load_by_url(identifier)
        nexus_url = identifier

    if not data:
        raise ValueError("Not found")

    types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]

    if "ModelBuildingConfig" in types:
        get_model_building_config(nexus_url, nexus_id)
    else:
        raise ValueError(f"Type `{types}` is not supported.")
