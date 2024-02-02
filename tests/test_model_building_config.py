import json
import attr
from requests.exceptions import JSONDecodeError
from unittest.mock import patch, call, Mock, MagicMock
from entity_management.config import Configs
import entity_management.cli.model_building_config as test_module


def test__write_json(tmp_path):
    test_dict = {"a": "b"}
    filename = "test.json"

    test_module._write_json(test_dict, tmp_path, filename)
    res_dict = json.loads((tmp_path / filename).read_text())
    assert test_dict == res_dict


@patch.object(test_module, "_used_in_as_dict")
def test__config_usage_as_list(mock_used_dict):
    config = Mock(used_in=[f"item_{i}" for i in range(5)])
    mock_used_dict.return_value = "foo"
    res = test_module._config_usage_as_list(config)
    assert res == 5 * ["foo"]
    mock_used_dict.assert_has_calls([call(used, config) for used in config.used_in])


@patch.object(test_module, "_config_usage_as_list")
def test__configs_as_dict(mock_usage_list):
    config = MagicMock()
    test_module._configs_as_dict(5 * [config])
    mock_usage_list.assert_has_calls(5 * [call(config)])


def test__iter_configs():
    @attr.s
    class MockConfigs:
        attr_0 = attr.ib(default=None)
        attr_1 = attr.ib(default=None)
        not_attr = "foo"

    res = test_module._iter_configs(MockConfigs(attr_0=42, attr_1=666))
    assert [*res] == [42, 666]

    res = test_module._iter_configs(MockConfigs(attr_1=666))
    assert [*res] == [666]


@patch.object(test_module, "_configs_as_dict")
@patch.object(test_module, "_iter_configs")
def test_model_building_config_as_dict(mock_iter, mock_configs_dict):
    config = Mock(configs="foo")
    mock_iter.return_value = "bar"
    test_module.model_building_config_as_dict(config)

    mock_iter.assert_called_once_with("foo")
    mock_configs_dict.assert_called_once_with("bar")


def model_building_config_as_dict(model_config):
    """Get ModelBuildingConfig as a dict."""
    return {
        "name": model_config.name,
        "description": model_config.description,
        "configs": _configs_as_dict(_iter_configs(model_config.configs)),
    }


def test__get_key():
    assert test_module._get_key({"test": "value"}, "test") == "value"
    assert test_module._get_key({"@test": "value"}, "test") == "value"
    assert test_module._get_key({"@fake": "value"}, "test") is None


def test__get_ids_from_dict():
    dict_ = {
        "id": "fake_id",
        "type": "fake_type",
        "store": {"id": "another_fake_id", "type": "fake_type"},
    }

    assert test_module._get_ids_from_dict(dict_) == {"fake_id"}

    dict_["not_store"] = dict_.pop("store")
    assert test_module._get_ids_from_dict(dict_) == {"fake_id", "another_fake_id"}

    dict_["_rev"] = 42
    dict_["not_store"]["rev"] = 666

    assert test_module._get_ids_from_dict(dict_) == {"fake_id?rev=42", "another_fake_id?rev=666"}


def test__get_timestamp():
    assert test_module._get_timestamp({"_createdAt": "00:42.666"}) == "00-42.666"
    assert test_module._get_timestamp({"_createdAt": "00.42.666"}) == "00.42.666"
    assert test_module._get_timestamp({}) == ""


def test__get_type():
    assert test_module._get_type({"@type": "test"}) == "test"
    assert test_module._get_type({"@type": ["test"]}) == "test"
    assert test_module._get_type({"@type": ["Entity", "Dataset", "test"]}) == "test"
    assert test_module._get_type({"@type": ["Entity", "Dataset"]}) == "Entity"


def test__get_entity_filename():
    fake_entity = {
        "_createdAt": "fake_timestamp",
        "@type": "fake_type",
    }
    assert test_module._get_entity_filename(fake_entity) == "fake_timestamp__fake_type.json"


def test__get_distribution_filename():
    item = {"name": "fake_distribution.fake_extension"}
    entity = {"_createdAt": "fake_timestamp"}

    res = test_module._get_distribution_filename(entity, item)
    assert res == "fake_timestamp__fake_distribution.fake_extension"


@patch.object(test_module, "download_file", new=Mock())
@patch.object(test_module, "file_as_dict")
def test_download_and_get_ids_from_distribution(mock_file_as_dict):
    entity = {
        "_createdAt": "fake_time",
        "distribution": {
            "name": "test_file.json",
            "contentUrl": "fake_url",
            "encodingFormat": "application/json",
        },
    }

    mock_file_as_dict.return_value = {"id": "another_fake_id", "type": "fake_type"}

    mapping = {}
    res = test_module.download_and_get_ids_from_distribution(entity, "fake_path", mapping)
    assert res == {"another_fake_id"}
    assert mapping == {"fake_url": "fake_time__test_file.json"}


@patch.object(test_module, "load_by_id")
def test__download_entity_get_ids(mock_load, tmp_path):
    mapping = {}
    fake_entity = {"@id": "fake_id", "@type": "fake_type", "_createdAt": "fake_time"}
    mock_load.return_value = {**fake_entity}

    res = test_module._download_entity_get_ids("fake_id", tmp_path, mapping)
    file_name = "fake_time__fake_type.json"
    assert mapping == {"fake_id": file_name}
    assert res == set()

    # check entity written
    assert (tmp_path / file_name).exists()
    file_dict = json.loads((tmp_path / file_name).read_text())
    assert file_dict == fake_entity


@patch.object(test_module, "load_by_id")
@patch.object(test_module, "_get_entity_filename")
def test__download_entity_get_ids_errors(mock_get_filename, mock_load):
    # load_by_id: JSONDecodeError
    mock_load.side_effect = JSONDecodeError("", "", 666)
    res = test_module._download_entity_get_ids("fake_id", "fake_path", "fake_mapping")
    assert res == set()
    mock_get_filename.assert_not_called()

    # load_by_id: returns None
    mock_load.reset_mock(side_effect=True)
    mock_load.return_value = None
    res = test_module._download_entity_get_ids("fake_id", "fake_path", "fake_mapping")
    assert res == set()
    mock_get_filename.assert_not_called()


@patch.object(test_module, "_download_entity_get_ids")
def test__download_entity_recursive(mock_download):
    mock_download.return_value = ["another_fake_id"]

    # Test that recursion stops if id is in mapping (already checked)
    mapping = {"fake_id": 666}
    res = test_module._download_entity_recursive("fake_id", "fake_path", depth=0, mapping=mapping)
    mock_download.assert_not_called()
    assert res == mapping

    # Test that recursion stops if depth has reached 0
    res = test_module._download_entity_recursive("fake_id", "fake_path", depth=0)
    mock_download.assert_called_once_with("fake_id", "fake_path", {})
    # function adding the id to mapping is mocked, so this is expected to be an empty dict
    assert res == {}

    mock_download.reset_mock()
    res = test_module._download_entity_recursive("fake_id", "fake_path", depth=1)
    mock_download.assert_has_calls(
        [
            call("fake_id", "fake_path", {}),
            call("another_fake_id", "fake_path", {}),
        ]
    )


@patch.object(test_module, "_write_json")
@patch.object(test_module, "_download_entity_recursive")
def test_download_model_config(mock_download, mock_write, tmp_path):
    mock_download.return_value = "fake_mapping"
    outdir = tmp_path / "test_dir"
    model_config = Mock(get_id=Mock(return_value="fake_id"))
    test_module.download_model_config(model_config, outdir, depth=666)

    assert outdir.exists()
    mock_write.assert_called_once_with("fake_mapping", outdir, "id_url_file_mapping.json")
    mock_download.assert_called_once_with("fake_id", outdir, 666)
