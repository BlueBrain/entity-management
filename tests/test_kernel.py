"""Test module for low level code:
 - entity_management.state
"""

from entity_management.state import get_org, set_org, get_proj, set_proj


def test_state_proj():
    set_proj("tmp")
    assert get_proj() == "tmp"


def test_state_org():
    set_org("tmp")
    assert get_org() == "tmp"
