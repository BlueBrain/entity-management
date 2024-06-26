# SPDX-License-Identifier: Apache-2.0

"""Command line interface."""

import logging
import os
from pprint import pprint

import click

from entity_management.cli.model_building_config import (
    download_model_config,
    model_building_config_as_dict,
)
from entity_management.config import ModelBuildingConfig
from entity_management.nexus import load_by_id, load_by_url
from entity_management.util import split_url_params


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
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, file_okay=False, resolve_path=True),
    default=None,
    help="If specified, the configs will be downloaded and saved to the given directory.",
)
@click.option(
    "-d",
    "--max-depth",
    default=1,
    show_default=True,
    help=(
        "Download is recursive, this is its maximum depth. "
        "'0' only downloads given entity and it's distribution. "
    ),
)
def get(id_or_url, output, max_depth):
    """Fetch a ModelBuildingConfig by ID or URL and print a subset of its contents.

    Requires NEXUS_TOKEN, NEXUS_ORG and NEXUS_PROJ to be set in the environment.

    NOTE: Does not support revisions. I.e., only retrieves the current revision of the entity.
    """
    if not_set := [v for v in ("NEXUS_TOKEN", "NEXUS_ORG", "NEXUS_PROJ") if not os.getenv(v)]:
        raise click.ClickException(f"Variable(s) {', '.join(not_set)} not set in environment.")

    id_or_url, _ = split_url_params(id_or_url)

    # In all tested cases `load_by_url` worked with the ID. `load_by_id` kept as a backup
    data = load_by_url(id_or_url) or load_by_id(id_or_url, cross_bucket=True)
    if not data:
        raise click.ClickException(f"Resource not found: {id_or_url}")

    types = data["@type"] if isinstance(data["@type"], list) else [data["@type"]]

    if "ModelBuildingConfig" in types:
        config = ModelBuildingConfig.from_id(data["@id"], cross_bucket=True)
        pprint(model_building_config_as_dict(config))

        if output is not None:
            download_model_config(config, output, max_depth)
    else:
        raise ValueError(f"Unsupported type: {types} (expected: 'ModelBuildingConfig')")
