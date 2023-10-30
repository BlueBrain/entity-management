"""Entities for Model building config

    see entity_management/cli/model_building_config.py for an example
    on how to use the objects

"""
from datetime import datetime
from attr.validators import in_
from entity_management.base import (
    attributes, _NexusBySparqlIterator, Identifiable, Frozen, BrainLocation)
from entity_management.util import AttrOf
from entity_management.atlas import AtlasRelease, AtlasSpatialReferenceSystem
from entity_management.core import Entity, DataDownload, Subject, Agent
from entity_management.simulation import DetailedCircuit  # pylint: disable=unused-import


@attributes(
    {"generatorName": AttrOf(str), "configVersion": AttrOf(int)}
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
            SELECT ?entity
            WHERE {?entity <https://bbp.epfl.ch/ontologies/core/bmo/used_config> <%s> .}
            LIMIT 20
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
    "cellCompositionConfig": AttrOf(CellCompositionConfig, default=None),
    "cellPositionConfig": AttrOf(CellPositionConfig, default=None),
    "morphologyAssignmentConfig": AttrOf(MorphologyAssignmentConfig, default=None),
    "eModelAssignmentConfig": AttrOf(EModelAssignmentConfig, default=None),
    "macroConnectomeConfig": AttrOf(MacroConnectomeConfig, default=None),
    "microConnectomeConfig": AttrOf(MicroConnectomeConfig, default=None),
    "synapseConfig": AttrOf(SynapseConfig, default=None),
})
class Configs(Frozen):
    """Sub configs of ModelBuildingConfig."""


@attributes({
    "configs": AttrOf(Configs),
})
class ModelBuildingConfig(Entity):
    """ModelBuildingConfig"""


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


@attributes({
    'agent': AttrOf(Agent, default=None),
})
class Contribution(Frozen):
    """Contribution"""


@attributes({
    'atlasRelease': AttrOf(AtlasRelease, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'contribution': AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    'subject': AttrOf(Subject, default=None),
})
class CellCompositionSummary(Entity):
    """CellCompositionSummary"""


@attributes({
    'about': AttrOf(list[str], default=None),
    'atlasRelease': AttrOf(AtlasRelease, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'contribution': AttrOf(Contribution, default=None),
    "distribution": AttrOf(DataDownload),
    'subject': AttrOf(Subject, default=None),
})
class CellCompositionVolume(Entity):
    """CellCompositionVolume"""


@attributes({
    'about': AttrOf(list[str], default=None),
    'atlasRelease': AttrOf(AtlasRelease, default=None),
    'atlasSpatialReferenceSystem': AttrOf(AtlasSpatialReferenceSystem, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'cellCompositionSummary': AttrOf(CellCompositionSummary, default=None),
    'cellCompositionVolume': AttrOf(CellCompositionVolume, default=None),
    'contribution': AttrOf(Contribution, default=None),
})
class CellComposition(Entity):
    """CellComposition"""
