"""Entities for Model building config"""
from entity_management.base import attributes, _NexusBySparqlIterator
from entity_management.util import AttrOf
from entity_management.core import Entity, DataDownload, Activity


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "generatorName": AttrOf(str),
    }
)
class SubConfig(Entity):
    """SubConfig.
    One of several partial configs making up the whole ModelBuildingConfig
    """

    @property
    def used_in(self):
        """List activities using the specified config.

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
        return _NexusBySparqlIterator(Activity, query)

    @property
    def content(self):
        """Return content of the config."""
        # pylint: disable=no-member
        return self.distribution.as_dict()


@attributes({"configs": AttrOf(dict)})
class ModelBuildingConfig(Entity):
    """ModelBuildingConfig."""

    def _instantiate_configs(self):
        # pylint: disable=no-member
        for key, value in self.configs.items():
            self.configs[key] = SubConfig.from_id(resource_id=value["@id"])

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
