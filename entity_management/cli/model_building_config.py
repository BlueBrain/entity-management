# SPDX-License-Identifier: Apache-2.0

"""Command line interface for Model Building Config."""

import json
import logging
import os
import re

import attr
from requests.exceptions import JSONDecodeError

from entity_management.atlas import CellComposition
from entity_management.config import BrainRegionSelectorConfig, MacroConnectomeConfig
from entity_management.nexus import download_file, file_as_dict, load_by_id
from entity_management.simulation import DetailedCircuit

UNALLOWED_ID_KEYS = {"store", "contribution"}


def _write_json(dict_, dir_, filename):
    print(f"    {filename}")
    with open(os.path.join(dir_, filename), "w", encoding="utf-8") as fd:
        json.dump(dict_, fd, indent=2)


def _used_in_as_dict(used_in, config):  # pragma: no cover
    result = {"id": used_in.generated.get_id()}

    if isinstance(used_in.generated, DetailedCircuit):
        result["atlas_release_id"] = used_in.generated.atlasRelease.get_id()
        result["circuit_url"] = used_in.generated.circuitConfigPath.url
    elif isinstance(used_in.generated, CellComposition):
        result["atlas_release_id"] = used_in.generated.atlasRelease.get_id()
        result["cell_composition_summary"] = used_in.generated.cellCompositionSummary.get_id()
        result["cell_composition_volume"] = used_in.generated.cellCompositionVolume.get_id()
    elif isinstance(used_in.generated, (MacroConnectomeConfig, BrainRegionSelectorConfig)):
        pass  # the `generated` points to a clone of the MacroConnectomeConfig
    else:
        logging.warning(
            'Unexpected type of `used_in` in "%s": %s (id: %s)',
            config.name,
            type(used_in.generated),
            used_in.generated.get_id(),
        )
    return result


def _config_usage_as_list(config):
    return [_used_in_as_dict(u, config) for u in config.used_in]


def _configs_as_dict(configs):
    return {
        config.name: {
            "name": config.name,
            "description": config.description,
            "generatorName": config.generatorName,
            "content": config.distribution.contentUrl,
            "used_in": _config_usage_as_list(config),
        }
        for config in configs
    }


def _iter_configs(configs):
    yield from (c for c in attr.astuple(configs, recurse=False) if c is not None)


def model_building_config_as_dict(model_config):
    """Get ModelBuildingConfig as a dict."""
    return {
        "name": model_config.name,
        "description": model_config.description,
        "configs": _configs_as_dict(_iter_configs(model_config.configs)),
    }


def _get_key(config, key):
    return config.get(f"@{key}") or config.get(key)


def _get_ids_from_dict(config):
    ids = set()
    if isinstance(config, dict):
        id_ = _get_key(config, "id")
        type_ = _get_key(config, "type")
        if id_ and type_:
            rev = _get_key(config, "_rev") or _get_key(config, "rev")
            if rev:
                id_ = f"{id_}?rev={rev}"
            ids.add(id_)
        for key, item in config.items():
            if key not in UNALLOWED_ID_KEYS:
                ids.update(_get_ids_from_dict(item))

    return ids


def _get_timestamp(entity):
    return re.sub(":", "-", entity.get("_createdAt", ""))


def _get_type(entity):
    types_list = entity["@type"]

    if not isinstance(types_list, list):
        return types_list
    elif len(types := set(types_list) - {"Entity", "Dataset"}) > 0:
        return list(types)[0]

    return types_list[0]


def _get_entity_filename(entity):
    return f"{_get_timestamp(entity)}__{_get_type(entity)}.json"


def _get_distribution_filename(entity, distribution_item):
    return f"{_get_timestamp(entity)}__{distribution_item.get('name')}"


def download_and_get_ids_from_distribution(entity, path, mapping):
    """Download the distribution files and get ids from them (if JSON)."""
    ids = set()
    distribution = entity.get("distribution", [])

    if not isinstance(distribution, list):
        distribution = [distribution]

    for d_item in distribution:
        url = d_item.get("contentUrl")
        if url:
            filename = _get_distribution_filename(entity, d_item)
            print(f"    {filename}")
            download_file(url, path, file_name=filename)
            mapping[url] = filename
            if d_item.get("encodingFormat", "") == "application/json":
                content = file_as_dict(url)
                ids.update(_get_ids_from_dict(content))

    return ids


def _download_entity_get_ids(id_, path, mapping):
    def _err_exit():
        print(f"\nERROR: Can't fetch: {id_}\n")
        return set()

    try:
        entity = load_by_id(id_)
    except JSONDecodeError:
        # In case id_ is a web URL instead of 'Nexus Address'
        return _err_exit()

    if not entity:
        return _err_exit()

    filename = _get_entity_filename(entity)
    _write_json(entity, path, filename)
    mapping[id_] = filename

    entity.pop("@id", None)
    ids = _get_ids_from_dict(entity)
    ids.update(download_and_get_ids_from_distribution(entity, path, mapping))

    return ids


def _download_entity_recursive(id_, path, depth, mapping=None):
    mapping = mapping or {}

    if id_ in mapping:
        return mapping

    entity_ids = _download_entity_get_ids(id_, path, mapping)

    if depth > 0:
        for sub_id in entity_ids:
            _download_entity_recursive(sub_id, path, depth - 1, mapping)

    return mapping


def download_model_config(model_config, path, depth):
    """Download model config recursively."""
    os.makedirs(path, exist_ok=True)
    print(f"\nSaving files to '{path}':\n")
    mapping = _download_entity_recursive(model_config.get_id(), path, depth)
    _write_json(mapping, path, "id_url_file_mapping.json")
