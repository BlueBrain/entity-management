from unittest.mock import patch

from entity_management_async import state as test_module


async def test_refresh_token__no_offline_token():
    """Test that refreshing is not attempted if no OFFLINE_TOKEN"""
    with patch(f"{test_module.__name__}.ACCESS_TOKEN", "my-token"):
        with patch(f"{test_module.__name__}.OFFLINE_TOKEN", None):
            token = await test_module.refresh_token()
            assert token == "my-token"


def test_get_base_resolvers():
    res = test_module.get_base_resolvers(base="my-base")
    assert res == "my-base/resolvers"


def test_get_base_resolvers__None():
    with patch(f"{test_module.__name__}.BASE", "my-base"):
        res = test_module.get_base_resolvers()
        assert res == "my-base/resolvers"


def test_base_url__cross_bucket():
    with patch(f"{test_module.__name__}.BASE", "my-base"):
        with patch(f"{test_module.__name__}.PROJ", "my-proj"):
            with patch(f"{test_module.__name__}.ORG", "my-org"):
                res = test_module.get_base_url()
                assert res == "my-base/resources/my-org/my-proj/_"

                res = test_module.get_base_url(cross_bucket=True)
                assert res == "my-base/resolvers/my-org/my-proj/_"


def test_base_url__schema_id():
    res = test_module.get_base_url(base="base", org="org", proj="proj", schema_id="schema-id")
    assert res == "base/resources/org/proj/schema-id"


async def test_get_user_id():

    mock_payload = {"preferred_username": "foo"}

    with patch(f"{test_module.__name__}.get_token_info", return_value=mock_payload):
        res = await test_module.get_user_id(base="base", org="org")
        assert res == "base/realms/org/users/foo"

        with patch(f"{test_module.__name__}.BASE", "my-base"):
            res = await test_module.get_user_id(org="org")
            assert res == "my-base/realms/org/users/foo"

        with patch(f"{test_module.__name__}.ORG", "my-org"):
            res = await test_module.get_user_id(base="base")
            assert res == "base/realms/my-org/users/foo"


def test_get_es_url():

    res = test_module.get_es_url(base="foo", org="bar", proj="zee")
    assert res == "foo/views/bar/zee/documents/_search"

    with patch(f"{test_module.__name__}.BASE", "my-base"):
        with patch(f"{test_module.__name__}.PROJ", "my-proj"):
            with patch(f"{test_module.__name__}.ORG", "my-org"):
                res = test_module.get_es_url()
                assert res == "my-base/views/my-org/my-proj/documents/_search"
