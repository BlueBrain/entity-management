# SPDX-License-Identifier: Apache-2.0

"""Bbp-workflow entities."""

from entity_management.base import Identifiable, _NexusBySparqlIterator, attributes
from entity_management.core import Activity, Entity
from entity_management.util import AttrOf


class BbpWorkflowConfig(Entity):
    """BbpWorkflow generic task config.

    Args:
        distribution (DataDownload): config stored in a cfg file.
    """


class BbpWorkflowResource(Entity):
    """BbpWorkflow generic resource produced by a task."""


@attributes(
    {
        "used_config": AttrOf(BbpWorkflowConfig),
        "used_rev": AttrOf(int),
        "generated": AttrOf(Identifiable, default=None),
    }
)
class BbpWorkflowActivity(Activity):
    """BbpWorkflow generic task activity.

    Args:
        used_config (BbpWorkflowConfig): config.
        used_rev (int): specific revision of the config.
        generated (Identifiable): resource.
    """

    @classmethod
    def used_config(cls, config, config_rev, was_influenced_by=None, **kwargs):
        """List activities using the specified config.

        Args:
            config (BbpWorkflowConfig): config entity.
            config_rev (int): config entity specific revision.
            was_influenced_by (Activity): Activity that influenced this activity.

        Returns:
            Iterator through the found resources.
        """
        constraints = [
            "nxv:deprecated false",
            f"bmo:used_config <{config.get_id()}>",
            f"bmo:used_rev {config_rev}",
        ]
        if was_influenced_by:
            constraints.append(f"prov:wasInfluencedBy <{was_influenced_by.get_id()}>")
        str_constraints = "; ".join(constraints)

        query = f"""
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX nxv:  <https://bluebrain.github.io/nexus/vocabulary/>
            PREFIX bmo:  <https://bbp.epfl.ch/ontologies/core/bmo/>
            SELECT ?entity
            WHERE {{
                ?entity a bmo:{cls.__name__} ; {str_constraints}  .
            }}
            LIMIT 1
        """
        return _NexusBySparqlIterator(cls, query, **kwargs)


class GeneratorTaskActivity(BbpWorkflowActivity):
    """Activity of a Generator Task."""
