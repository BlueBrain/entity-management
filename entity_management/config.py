# SPDX-License-Identifier: Apache-2.0

"""Entities for Model building config

    see entity_management/cli/model_building_config.py for an example
    on how to use the objects

"""

from entity_management.base import Frozen, _NexusBySparqlIterator, attributes
from entity_management.core import Entity
from entity_management.util import AttrOf
from entity_management.workflow import BbpWorkflowConfig, GeneratorTaskActivity


@attributes(
    {"generatorName": AttrOf(str, default=None), "configVersion": AttrOf(int, default=None)}
)
class _SubConfig(BbpWorkflowConfig):
    """SubConfig.
    One of several partial configs making up the whole ModelBuildingConfig
    """

    @property
    def used_in(self):
        """List ids of activities using the specified config.

        Returns:
            Iterator through the found resources.
        """
        query = """
            PREFIX nxv: <https://bluebrain.github.io/nexus/vocabulary/>
            PREFIX bmo: <https://bbp.epfl.ch/ontologies/core/bmo/>
            SELECT ?entity
            WHERE {
                ?entity a bmo:GeneratorTaskActivity ;
                    bmo:used_config <%s> ;
                    nxv:deprecated false .
            }
        """ % (
            self.get_id()
        )
        return _NexusBySparqlIterator(GeneratorTaskActivity, query)

    @property
    def content(self):
        """Return content of the config."""
        # pylint: disable=no-member
        return self.distribution.as_dict()


class BrainRegionSelectorConfig(_SubConfig):
    """BrainRegionSelectorConfig"""


class CellCompositionConfig(_SubConfig):
    """CellCompositionConfig"""


class CellPositionConfig(_SubConfig):
    """CellPositionConfig"""


class EModelAssignmentConfig(_SubConfig):
    """EModelAssignmentConfig"""


class MacroConnectomeConfig(_SubConfig):
    """MacroConnectomeConfig"""


class MicroConnectomeConfig(_SubConfig):
    """MicroConnectomeConfig"""


class MorphologyAssignmentConfig(_SubConfig):
    """MorphologyAssignmentConfig"""


class SynapseConfig(_SubConfig):
    """SynapseConfig"""


class MEModelConfig(_SubConfig):
    """MEModelConfig"""


@attributes(
    {
        "brainRegionSelectorConfig": AttrOf(BrainRegionSelectorConfig, default=None),
        "cellCompositionConfig": AttrOf(CellCompositionConfig),
        "cellPositionConfig": AttrOf(CellPositionConfig),
        "morphologyAssignmentConfig": AttrOf(MorphologyAssignmentConfig),
        "eModelAssignmentConfig": AttrOf(EModelAssignmentConfig, default=None),
        "macroConnectomeConfig": AttrOf(MacroConnectomeConfig),
        "microConnectomeConfig": AttrOf(MicroConnectomeConfig),
        "synapseConfig": AttrOf(SynapseConfig),
        "meModelConfig": AttrOf(MEModelConfig, default=None),
    }
)
class Configs(Frozen):
    """Sub configs of ModelBuildingConfig."""


@attributes(
    {
        "configs": AttrOf(Configs),
    }
)
class ModelBuildingConfig(Entity):
    """ModelBuildingConfig"""
