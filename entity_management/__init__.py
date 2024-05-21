# SPDX-License-Identifier: Apache-2.0

"""entity-management"""

from importlib.metadata import version

__version__ = version(__package__)

import logging

# To ensure that classes are registered and found in entity_management.nexus._HINT_TO_CLS_MAP
from entity_management import (
    atlas,
    config,
    electrophysiology,
    emodel,
    experiment,
    morphology,
    simulation,
    workflow,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
