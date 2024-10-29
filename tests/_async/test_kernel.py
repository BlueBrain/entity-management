"""Test module for low level code:
 - entity_management_async.state
"""

from entity_management_async.state import get_org, get_proj, set_org, set_proj


def test_state_proj():
    set_proj("tmp")
    assert get_proj() == "tmp"


def test_state_org():
    set_org("tmp")
    assert get_org() == "tmp"
