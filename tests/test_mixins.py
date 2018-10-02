from mock import patch
from nose.tools import assert_equal, assert_raises

from entity_management.base import Distribution
from entity_management.mixins import DistributionMixin


def test_download():
    assert_raises(Exception, DistributionMixin(distribution=[]).download, 'bla')

    dist = Distribution(originalFileName='mario', downloadURL='https://an/attachment')

    with patch('entity_management.mixins.nexus'):
        assert_equal(DistributionMixin(distribution=[dist]).download('/a/non/existing/dir/bla'),
                     '/a/non/existing/dir/bla')
