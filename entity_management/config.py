# Automatically generated, DO NOT EDIT.
# SPDX-License-Identifier: Apache-2.0

"""Entities for Model building config

    see entity_management/cli/model_building_config.py for an example
    on how to use the objects

"""

from entity_management.base import Derivation, Frozen, _NexusBySparqlIterator, attributes
from entity_management.core import DataDownload, Entity
from entity_management.util import AttrOf, LazySchemaValidator
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

    def get_content(self):
        """Return content of the config."""
        return self.content


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("brain_region_selector_config_distribution.yml")],
        )
    }
)
class BrainRegionSelectorConfig(_SubConfig):
    """BrainRegionSelectorConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("cell_composition_config_distribution.yml")],
        )
    }
)
class CellCompositionConfig(_SubConfig):
    """CellCompositionConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("cell_position_config_distribution.yml")],
        )
    }
)
class CellPositionConfig(_SubConfig):
    """CellPositionConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
        )
    }
)
class EModelAssignmentConfig(_SubConfig):
    """EModelAssignmentConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("macro_connectome_config_distribution.yml")],
        )
    }
)
class MacroConnectomeConfig(_SubConfig):
    """MacroConnectomeConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("micro_connectome_config_distribution.yml")],
        )
    }
)
class MicroConnectomeConfig(_SubConfig):
    """MicroConnectomeConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("morphology_assignment_config_distribution.yml")],
        )
    }
)
class MorphologyAssignmentConfig(_SubConfig):
    """MorphologyAssignmentConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("canonical_morphology_model_config_distribution.yml")],
        ),
        "derivation": AttrOf(Derivation, default=None),
    }
)
class CanonicalMorphologyModelConfig(Entity):
    """Canonical config in MorphologyAssignmentConfig distribution."""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("placeholder_morphology_config_distribution.yml")],
        ),
        "derivation": AttrOf(Derivation, default=None),
    }
)
class PlaceholderMorphologyConfig(Entity):
    """Placeholder morphologies config in MorphologyAssignmentConfig distribution."""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("synapse_config_distribution.yml")],
        )
    }
)
class SynapseConfig(_SubConfig):
    """SynapseConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("me_model_config_distribution.yml")],
        )
    }
)
class MEModelConfig(_SubConfig):
    """MEModelConfig"""


@attributes(
    {
        "distribution": AttrOf(
            DataDownload,
            validators=[LazySchemaValidator("placeholder_emodel_config_distribution.yml")],
        )
    }
)
class PlaceholderEModelConfig(Entity):
    """PlaceholderEModelConfig in MEModelConfig distribution."""


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
