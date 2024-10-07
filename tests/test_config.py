import json
from pathlib import Path

import pytest
from entity_management import config as test_module
from entity_management.util import validate_schema

DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "schema_name",
    [
        "brain_region_selector_config_distribution",
        "cell_composition_config_distribution",
        "cell_position_config_distribution",
        "morphology_assignment_config_distribution",
        "me_model_config_distribution",
        "macro_connectome_config_distribution",
        "micro_connectome_config_distribution",
        "synapse_config_distribution",
        "canonical_morphology_model_config_distribution",
        "placeholder_morphology_config_distribution",
        "placeholder_emodel_config_distribution",
    ],
)
def test_config_distribution_schema(schema_name):
    schema = f"{schema_name}.yml"
    example = DATA_DIR / f"{schema_name}.json"
    data = json.loads(example.read_bytes())
    validate_schema(data=data, schema_name=schema)
