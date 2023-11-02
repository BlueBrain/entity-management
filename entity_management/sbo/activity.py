"""SBO related entities for activities."""
from datetime import datetime

from attr.validators import in_

from entity_management.base import Identifiable, attributes
from entity_management.util import AttrOf


@attributes({
    'status': AttrOf(str, default=None, validators=in_([None,
                                                        'Pending',
                                                        'Running',
                                                        'Done',
                                                        'Failed'])),
    'used_config': AttrOf(Identifiable, default=None),
    'used_rev': AttrOf(int, default=None),
    'generated': AttrOf(Identifiable, default=None),
    'startedAtTime': AttrOf(datetime, default=None),
    'wasInfluencedBy': AttrOf(Identifiable, default=None),
})
class GeneratorTaskActivity(Identifiable):
    """GeneratorTaskActivity"""
