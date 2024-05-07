import json
import typing
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

import attr
import pytest

from entity_management import nexus
from entity_management.core import DataDownload
from entity_management import emodel as test_module
from entity_management.electrophysiology import Trace


DATA_DIR = Path(__file__).parent / "data"


def _follow(obj, string):
    s = string.split(".")
    current = obj
    for a in s:
        current = getattr(current, a)
    return current


def _instantiate(cls, response_file):
    response = json.loads(response_file.read_bytes())
    with patch("entity_management.nexus.load_by_url", return_value=response):
        return cls.from_id(None)


def _apply(func, obj):
    if not isinstance(obj, list):
        obj = [obj]
    return (func(o) for o in obj)


def _not_none(obj):
    assert all(_apply(lambda o: o is not None, obj))


def _has_id(obj):
    assert all(_apply(lambda o: o.get_id() is not None, obj))


def _has_rev(obj):
    assert all(_apply(lambda o: o.get_rev() is not None, obj))


def _has_content_url(obj):
    assert all(_apply(lambda o: o.contentUrl is not None, obj))


def _has_json_encoding_format(obj):
    assert any(_apply(lambda o: o.encodingFormat == "application/json", obj))


def _has_agent_id(obj):
    assert all(_apply(lambda o: o.agent.get_id() is not None, obj))


def _has_body_label(obj):
    assert all(_apply(lambda o: o.hasBody.label is not None, obj))


def _nonempty_list(obj):
    assert isinstance(obj, list) and len(obj) > 0


def _is_datetime(obj):
    assert isinstance(obj, datetime)


def _has_emodel_elements(obj_list):
    assert all(isinstance(obj, test_module.EModel) for obj in obj_list)


def _get_path_result(obj, path, test_type):
    return _test_type(_follow(path, obj), test_type)


@pytest.fixture(scope="module")
def emodel_release():
    return _instantiate(test_module.EModelRelease, DATA_DIR / "emodel_release_resp.json")


@pytest.mark.parametrize(
    "path,test_func",
    [
        ("name", _not_none),
        ("eModelDataCatalog", _has_id),
        ("atlasRelease", _has_id),
        ("atlasRelease", _has_rev),
        ("contribution", _has_agent_id),
        ("brainLocation.brainRegion.url", _not_none),
        ("releaseDate", _is_datetime),
    ],
)
def test_EModelRelease(path, test_func, emodel_release):
    test_func(_follow(emodel_release, path))


ENTITY_TESTS = [
    ("name", _not_none),
    ("contribution", _has_agent_id),
]


@pytest.fixture(scope="module")
def emodel_data_catalog():
    return _instantiate(test_module.EModelDataCatalog, DATA_DIR / "emodel_data_catalog_resp.json")


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("distribution.contentUrl", _not_none),
        ("distribution", _has_json_encoding_format),
        ("brainLocation.brainRegion.url", _not_none),
        ("hasPart", _nonempty_list),
        ("hasPart", _has_emodel_elements),
        ("hasPart", _has_id),
    ],
)
def test_EModelDataCatalog(path, test_func, emodel_data_catalog):
    test_func(_follow(emodel_data_catalog, path))


@pytest.fixture(scope="module")
def emodel():
    return _instantiate(test_module.EModel, DATA_DIR / "emodel_resp.json")


def _has_data_download_elements(obj_list):
    assert all(isinstance(obj, DataDownload) and obj.contentUrl is not None for obj in obj_list)


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("mType", _not_none),
        ("iteration", _not_none),
        ("score", _not_none),
        ("seed", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _nonempty_list),
        ("distribution", _has_data_download_elements),
        ("generation.activity.followedWorkflow", _has_id),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_EModel(path, test_func, emodel):
    test_func(_follow(emodel, path))


@pytest.fixture(scope="module")
def emodel_configuration():
    return _instantiate(
        test_module.EModelConfiguration, DATA_DIR / "emodel_configuration_resp.json"
    )


def _validate_union_field_types(cls, field_name, obj_list):
    # get the types inside the union inside the list type

    types = typing.get_args(typing.get_args(getattr(attr.fields(cls), field_name).type)[0])

    expected_class_names = {t.__name__ for t in types}
    names = {type(obj).__name__ for obj in obj_list}

    assert expected_class_names == names


def _validate_emodel_configuration_uses(obj_list):
    _nonempty_list(obj_list)
    _has_id(obj_list)
    _validate_union_field_types(test_module.EModelConfiguration, "uses", obj_list)


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _has_content_url),
        ("distribution", _has_json_encoding_format),
        ("uses", _validate_emodel_configuration_uses),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_EModelConfiguration(path, test_func, emodel_configuration):
    test_func(_follow(emodel_configuration, path))


@pytest.fixture(scope="module")
def emodel_script():
    return _instantiate(test_module.EModelScript, DATA_DIR / "emodel_script_resp.json")


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("seed", _not_none),
        ("annotation", _has_body_label),
        ("generation.activity.followedWorkflow", _has_id),
        ("distribution", _has_content_url),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_EModelScript(path, test_func, emodel_script):
    test_func(_follow(emodel_script, path))


@pytest.fixture(scope="module")
def sub_cellular_model_script():
    return _instantiate(
        test_module.SubCellularModelScript, DATA_DIR / "sub_cellular_model_script_resp.json"
    )


@pytest.mark.parametrize(
    "path,test_func",
    [
        ("name", _not_none),
        ("description", _not_none),
        ("contribution", _has_agent_id),
        ("description", _not_none),
        ("distribution", _nonempty_list),
        ("distribution", _has_content_url),
        ("modelId", _not_none),
        ("nmodlParameters", _not_none),
        ("exposesParameter", _not_none),
        ("identifier", _not_none),
        ("isLjpCorrected", _not_none),
        ("isTemperatureDependent", _not_none),
        ("ion", _not_none),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
        ("subject.species.url", _not_none),
        ("subject.species.label", _not_none),
        ("temperature", _not_none),
    ],
)
def test_SubCellularModelScript(path, test_func, sub_cellular_model_script):
    test_func(_follow(sub_cellular_model_script, path))


@pytest.fixture(scope="module")
def emodel_pipeline_settings():
    return _instantiate(
        test_module.EModelPipelineSettings, DATA_DIR / "emodel_pipeline_settings_resp.json"
    )


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _has_content_url),
        ("distribution", _has_json_encoding_format),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_EModelPipelineSettings(path, test_func, emodel_pipeline_settings):
    test_func(_follow(emodel_pipeline_settings, path))


@pytest.fixture(scope="module")
def extraction_targets_configuration():
    return _instantiate(
        test_module.ExtractionTargetsConfiguration,
        DATA_DIR / "extraction_targets_configuration_resp.json",
    )


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _has_content_url),
        ("distribution", _has_json_encoding_format),
        ("uses", _nonempty_list),
        ("uses", _has_id),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_ExtractionTargetsConfiguration(path, test_func, extraction_targets_configuration):
    test_func(_follow(extraction_targets_configuration, path))


@pytest.fixture(scope="module")
def fitness_calculator_configuration():
    return _instantiate(
        test_module.FitnessCalculatorConfiguration,
        DATA_DIR / "fitness_calculator_configuration_resp.json",
    )


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _has_content_url),
        ("distribution", _has_json_encoding_format),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
    ],
)
def test_FitnessCalculatorConfiguration(path, test_func, fitness_calculator_configuration):
    test_func(_follow(fitness_calculator_configuration, path))


@pytest.fixture(scope="module")
def emodel_workflow():
    return _instantiate(test_module.EModelWorkflow, DATA_DIR / "emodel_workflow_resp.json")


def _validate_emodel_workflow_hasPart(obj_list):
    _nonempty_list(obj_list)
    _has_id(obj_list)
    _validate_union_field_types(test_module.EModelWorkflow, "hasPart", obj_list)


def _validate_emodel_workflow_generates(obj_list):
    _nonempty_list(obj_list)
    _has_id(obj_list)
    # due to the forward declaration of the EModel the definition was set to Identifiable
    # so that the deserialization handles the correct class instantation using the global
    # registry that has been populated with all classes during runtime.
    class_names = {type(o).__name__ for o in obj_list}
    assert class_names == {"EModel", "EModelScript", "FitnessCalculatorConfiguration"}


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("eModel", _not_none),
        ("eType", _not_none),
        ("iteration", _not_none),
        ("annotation", _has_body_label),
        ("distribution", _has_content_url),
        ("distribution", _has_json_encoding_format),
        ("objectOfStudy.url", _not_none),
        ("objectOfStudy.label", _not_none),
        ("hasPart", _validate_emodel_workflow_hasPart),
        ("generates", _validate_emodel_workflow_generates),
        ("state", _not_none),
    ],
)
def test_EModelWorkflow(path, test_func, emodel_workflow):
    test_func(_follow(emodel_workflow, path))


@pytest.fixture(scope="module")
def trace():
    return _instantiate(Trace, DATA_DIR / "trace_resp.json")


@pytest.mark.parametrize(
    "path,test_func",
    ENTITY_TESTS
    + [
        ("distribution", _has_content_url),
        ("contribution", _has_agent_id),
        ("brainLocation.brainRegion.url", _not_none),
    ],
)
def test_Trace(path, test_func, trace):
    test_func(_follow(trace, path))
