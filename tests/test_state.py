from unittest.mock import patch
from entity_management import state as test_module


def test_refresh_token__no_offline_token():
    """Test that refreshing is not attempted if no OFFLINE_TOKEN"""
    with (
        patch("entity_management.state.ACCESS_TOKEN", "my-token"),
        patch("entity_management.state.OFFLINE_TOKEN", None),
    ):
        token = test_module.refresh_token()
        assert token == "my-token"


def test_get_base_resolvers():
    res = test_module.get_base_resolvers(base="my-base")
    assert res == "my-base/resolvers"


def test_get_base_resolvers__None():
    with patch("entity_management.state.BASE", "my-base"):
        res = test_module.get_base_resolvers()
        assert res == "my-base/resolvers"
