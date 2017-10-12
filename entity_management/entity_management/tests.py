from mock import patch, Mock
from nose.tools import raises

import entity_management.client as client


@raises(Exception)
@patch('entity_management.nexus')
def test_get_entity_by_dummy_url(nx):
    client.get_entity_by_url('http://hello.world')


@patch('entity_management.nexus.get_entity', return_value={})
@patch('entity_management.fakenexus.get_entity', return_value={})
def test_get_entity_by_fakenexus_url(fakenexus_patched, nexus_patched):
    url = 'fakenexus://nexus.world'
    client.get_entity_by_url(url)
    fakenexus_patched.assert_called_once_with(url)
    assert not nexus_patched.called


@patch('entity_management.nexus.get_entity', return_value={})
@patch('entity_management.fakenexus.get_entity', return_value={})
def test_get_entity_by_nexus_http(fakenexus_patched, nexus_patched):
    url = 'http://nexus.world'
    client.get_entity_by_url(url)
    nexus_patched.assert_called_once_with(url)
    assert not fakenexus_patched.called


@patch('entity_management.nexus.get_entity', return_value={})
@patch('entity_management.fakenexus.get_entity', return_value={})
def test_get_entity_by_nexus_https(fakenexus_patched, nexus_patched):
    url = 'https://nexus.world'
    client.get_entity_by_url(url)
    nexus_patched.assert_called_once_with(url)
    assert not fakenexus_patched.called
