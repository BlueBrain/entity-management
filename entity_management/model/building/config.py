"""Entities for Model building config"""
from datetime import datetime
from entity_management.base import attributes, _NexusBySparqlIterator, Identifiable
from entity_management.util import AttrOf
from entity_management.core import Entity, DataDownload, Activity
from entity_management.nexus import sparql_query, load_by_id, register_type
from attr.validators import in_


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
        #result = sparql_query(query)
        #ids = [item["entity"]["value"] for item in result["results"]["bindings"] if item["entity"]["type"] == "uri"]
        #return {item: load_by_id(item)["generated"]["@id"] for item in ids}
        return _NexusBySparqlIterator(GeneratorTaskActivity, query)

    @property
    def content(self):
        """Return content of the config."""
        # pylint: disable=no-member
        return self.distribution.as_dict()


class CellCompositionConfig(SubConfig):
    pass


class CellPositionConfig(SubConfig):
    pass


class EModelAssignmentConfig(SubConfig):
    pass


class MorphologyAssignmentConfig(SubConfig):
    pass


class SynapseConfig(SubConfig):
    pass


@attributes({"configs": AttrOf(dict)})
class ModelBuildingConfig(Entity):
    """ModelBuildingConfig."""

    def _instantiate_configs(self):
        # pylint: disable=no-member
        for key, value in self.configs.items():
            self.configs[key] = SubConfig.from_id(resource_id=value["@id"], cross_bucket=True)

    @classmethod
    def from_id(cls, **kwargs):
        # pylint: disable=arguments-differ,no-member
        result = super().from_id(**kwargs)
        result._instantiate_configs()
        return result

    @classmethod
    def from_url(cls, **kwargs):
        # pylint: disable=arguments-differ,no-member
        result = super().from_url(**kwargs)
        result._instantiate_configs()
        return result


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
    #'wasInfluencedBy': AttrOf(Identifiable, default=None),
})
class GeneratorTaskActivity(Identifiable):
    pass