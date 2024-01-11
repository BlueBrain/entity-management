"""Command line interface for Model Building Config."""
import os
import logging
import attr
from entity_management.config import MacroConnectomeConfig, BrainRegionSelectorConfig
from entity_management.simulation import DetailedCircuit
from entity_management.atlas import CellComposition


def _used_in_as_dict(used_in, config):
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
            "Unexpected type of `used_in` in \"%s\": %s (id: %s)",
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
            "used_in": _config_usage_as_list(config)
        } for config in configs
    }


def _iter_configs(configs):
    yield from (c for c in attr.astuple(configs, recurse=False) if c is not None)


def model_building_config_as_dict(model_config):
    """Get ModelBuildingConfig as a dict."""
    return {
        "name": model_config.name,
        "description": model_config.description,
        "configs": _configs_as_dict(_iter_configs(model_config.configs))
    }


def download_config_files(path, model_config):
    """Download ModelBuildingConfig's config files."""
    configs = [*_iter_configs(model_config.configs)]

    if len(configs) == 0:
        print(" * No configs to download")
        return

    os.makedirs(path, exist_ok=True)

    for config in configs:
        config.distribution.download(path)

    print(f" * Saved {len(configs)} configs to {path}")
