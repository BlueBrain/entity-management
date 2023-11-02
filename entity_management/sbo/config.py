"""Entities for Model building config

    see entity_management/cli/model_building_config.py for an example
    on how to use the objects

"""
from entity_management.base import (
    attributes, _NexusBySparqlIterator, Frozen)
from entity_management.sbo.activity import GeneratorTaskActivity
from entity_management.util import AttrOf
from entity_management.core import Entity


@attributes(
    {"generatorName": AttrOf(str, default=None), "configVersion": AttrOf(int, default=None)}
)
class SubConfig(Entity):
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


class CellCompositionConfig(SubConfig):
    """CellCompositionConfig"""


class CellPositionConfig(SubConfig):
    """CellPositionConfig"""


class EModelAssignmentConfig(SubConfig):
    """EModelAssignmentConfig"""


class MacroConnectomeConfig(SubConfig):
    """MacroConnectomeConfig"""


class MicroConnectomeConfig(SubConfig):
    """MicroConnectomeConfig"""


class MorphologyAssignmentConfig(SubConfig):
    """MorphologyAssignmentConfig"""


class SynapseConfig(SubConfig):
    """SynapseConfig"""


@attributes({
    "cellCompositionConfig": AttrOf(CellCompositionConfig),
    "cellPositionConfig": AttrOf(CellPositionConfig),
    "morphologyAssignmentConfig": AttrOf(MorphologyAssignmentConfig),
    "eModelAssignmentConfig": AttrOf(EModelAssignmentConfig),
    "macroConnectomeConfig": AttrOf(MacroConnectomeConfig),
    "microConnectomeConfig": AttrOf(MicroConnectomeConfig),
    "synapseConfig": AttrOf(SynapseConfig),
})
class Configs(Frozen):
    """Sub configs of ModelBuildingConfig."""


@attributes({
    "configs": AttrOf(Configs),
})
class ModelBuildingConfig(Entity):
    """ModelBuildingConfig"""
