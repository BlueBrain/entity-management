# pylint: disable=missing-docstring,no-member
import json
import tempfile

import pytest

import entity_management.nexus as nexus
from entity_management.core import DataDownload, WorkflowExecution, Entity, Activity, Person


@pytest.fixture(name="workflow_resp", scope="session")
def fixture_workflow_resp():
    with open("tests/data/workflow_resp.json") as f:
        return json.load(f)


@pytest.fixture(name="file_resp", scope="session")
def fixture_file_resp():
    with open("tests/data/file_resp.json") as f:
        return json.load(f)


def test_workflow_execution(monkeypatch, workflow_resp, file_resp):
    monkeypatch.setattr(nexus, "upload_file", lambda *a, **b: file_resp)
    monkeypatch.setattr(nexus, "create", lambda *a, **b: workflow_resp)

    with tempfile.NamedTemporaryFile(suffix=".zip") as temp:
        temp.write(b"Some data")  # 9 bytes of data
        temp.flush()
        distribution = DataDownload.from_file(file_like=temp.name, content_type="application/zip")
        workflow = WorkflowExecution(
            name="module_name.TaskName",
            module="module",
            task="task",
            version="1",
            distribution=distribution,
        )

    assert workflow.as_json_ld()["distribution"]["@type"] == "DataDownload"
    assert workflow.distribution.contentSize["value"] == 9
    assert workflow.distribution.encodingFormat == "application/zip"


def test_data_download_no_url_and_content_url_provided():
    with pytest.raises(Exception):
        DataDownload()


def test_publish_with_attribution(monkeypatch):
    entity = Entity(name="test")
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity = entity.publish(was_attributed_to=Person(email="email"))
    assert entity.wasAttributedTo[0].email == "email"


def test_publish_with_existing_attribution(monkeypatch):
    entity = Entity(name="test", wasAttributedTo=[Person(email="email1")])
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity = entity.publish(was_attributed_to=Person(email="email2"))
    emails = [person.email for person in entity.wasAttributedTo]
    assert "email1" in emails
    assert "email2" in emails


def test_publish_without_workflow(monkeypatch):
    entity = Entity(name="test")
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity.publish()


def test_entity_publish_with_activity(monkeypatch):
    entity = Entity(name="test")
    activity = Activity(name="activity")
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity = entity.publish(activity=activity)
    assert entity.wasGeneratedBy.name == activity.name


def test_activity_publish_with_activity(monkeypatch):
    activity1 = Activity(name="activity1")
    activity2 = Activity(name="activity2")
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    activity1 = activity1.publish(activity=activity2)
    assert activity1.wasInformedBy.name == activity2.name


def test_publish_with_activity_override(monkeypatch):
    entity = Entity(name="test", wasGeneratedBy=Activity(name="activity1"))
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity = entity.publish(activity=Activity(name="activity2"))
    assert entity.wasGeneratedBy.name == "activity2", (
        "Original entity wasGeneratedBy activity should be overriden by the one "
        "provided in publish method"
    )


def test_publish_activity_with_activity_no_override(monkeypatch):
    activity = Activity(name="test", wasInformedBy=Activity(name="activity1"))
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    activity = activity.publish(activity=Activity(name="activity2"))
    assert activity.wasInformedBy.name == "activity1", (
        "Original activity wasStartedBy activity should not be overriden by the one "
        "provided in publish method"
    )


def test_publish_entity_with_workflow(monkeypatch):
    monkeypatch.setattr("entity_management.core.WORKFLOW", "workflow_id")
    monkeypatch.setattr(
        WorkflowExecution,
        "from_id",
        classmethod(
            lambda *a, **b: WorkflowExecution(
                name="workflow", module="module", task="task", version="1"
            )
        ),
    )
    entity = Entity(name="name")
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    entity = entity.publish()
    assert entity.wasGeneratedBy.name == "workflow"


def test_publish_activity(monkeypatch):
    activity = Activity()
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    activity.publish()


def test_publish_activity_with_workflow(monkeypatch):
    monkeypatch.setattr("entity_management.core.WORKFLOW", "workflow_id")
    monkeypatch.setattr(
        WorkflowExecution,
        "from_id",
        classmethod(
            lambda *a, **b: WorkflowExecution(
                name="workflow", module="module", task="task", version="1"
            )
        ),
    )
    activity = Activity()
    monkeypatch.setattr(nexus, "create", lambda *a, **b: {})
    activity = activity.publish()
    assert activity.wasInfluencedBy.name == "workflow"


@pytest.fixture(name="file_link_resp", scope="session")
def fixture_file_link_resp():
    with open("tests/data/file_link_resp.json") as f:
        return json.load(f)


def test_data_download_link_file(monkeypatch, file_link_resp):
    monkeypatch.setattr(nexus, "link_file", lambda *a, **b: file_link_resp)

    with tempfile.NamedTemporaryFile(suffix=".zip") as temp:
        file_path = temp.name
        distribution = DataDownload.link_file(file_path=file_path, content_type="application/zip")

    assert "b00896ef-db8c-4fae-90e4-ae157a306746" in distribution.contentUrl


@pytest.fixture(name="entity_data_download_resp")
def fixture_entity_data_download_resp():
    with open("tests/data/entity_data_download_resp.json") as f:
        return json.load(f)


def test_data_download_get_location(monkeypatch, entity_data_download_resp, file_link_resp):
    monkeypatch.setattr(nexus, "load_by_url", lambda *a, **b: entity_data_download_resp)
    monkeypatch.setattr(nexus, "_get_file_metadata", lambda *a, **b: file_link_resp)

    entity = Entity.from_id("id")
    assert (
        entity.distribution.get_location()
        == "https://s3.us-west-1.amazonaws.com/bucket/relative/path/to/file.zip"
    )


def test_data_download_get_location_path(monkeypatch, entity_data_download_resp, file_link_resp):
    monkeypatch.setattr(nexus, "load_by_url", lambda *a, **b: entity_data_download_resp)
    monkeypatch.setattr(nexus, "_get_file_metadata", lambda *a, **b: file_link_resp)

    entity = Entity.from_id("id")
    assert entity.distribution.get_location_path() == "/bucket/relative/path/to/file.zip"


def test_data_download_get_url_as_path(monkeypatch, entity_data_download_resp):
    monkeypatch.setattr(nexus, "load_by_url", lambda *a, **b: entity_data_download_resp)
    entity = Entity.from_id("id")
    assert entity.distribution.get_url_as_path() == "/gpfs/distribution_path.json"


def test_data_download_get_url_as_path__raises(monkeypatch, entity_data_download_resp):

    del entity_data_download_resp["distribution"]["url"]
    monkeypatch.setattr(nexus, "load_by_url", lambda *a, **b: entity_data_download_resp)
    entity = Entity.from_id("id")

    with pytest.raises(AssertionError, match="No url!"):
        entity.distribution.get_url_as_path()

    entity_data_download_resp["distribution"]["url"] = "https://non-file-uri"
    entity = Entity.from_id("id")

    with pytest.raises(AssertionError, match=r"URL 'https://non-file-uri' is not a file URI."):
        entity.distribution.get_url_as_path()
