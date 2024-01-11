"""Command line interface."""
import os
import logging
from pprint import pprint
import click
from entity_management.config import ModelBuildingConfig
from entity_management.nexus import load_by_id, load_by_url
from entity_management.util import split_url_from_revision_query
from entity_management.cli.model_building_config import model_building_config_as_dict


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
@click.argument("id_or_url", type=str, nargs=1)
def get(id_or_url):
    """Fetch a ModelBuildingConfig by ID or URL and print a subset of its contents.

    Requires NEXUS_TOKEN, NEXUS_ORG and NEXUS_PROJ to be set in the environment.

    NOTE: Does not support revisions. I.e., only retrieves the current revision of the entity.
    """
    if not_set := [v for v in ("NEXUS_TOKEN", "NEXUS_ORG", "NEXUS_PROJ") if not os.getenv(v)]:
        raise click.ClickException(f"Variable(s) {', '.join(not_set)} not set in environment.")

    id_or_url, _ = split_url_from_revision_query(id_or_url)

    # In all tested cases `load_by_url` worked with the ID. `load_by_id` kept as a backup
    data = load_by_url(id_or_url) or load_by_id(id_or_url, cross_bucket=True)
    if not data:
        raise click.ClickException(f"Resource not found: {id_or_url}")

    types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]

    if "ModelBuildingConfig" in types:
        config = ModelBuildingConfig.from_id(data['@id'], cross_bucket=True)
        pprint(model_building_config_as_dict(config))
    else:
        raise ValueError(f"Unsupported type: {types} (expected: 'ModelBuildingConfig')")
