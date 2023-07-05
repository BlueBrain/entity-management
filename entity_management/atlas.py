"""Atlas related entities."""
from entity_management.base import Identifiable, attributes
from entity_management.util import AttrOf


@attributes(
    {
        "label": AttrOf(str),
        "identifier": AttrOf(int),
        "notation": AttrOf(str),
        "prefLabel": AttrOf(str),
    }
)
class AtlasBrainRegion(Identifiable):
    """Atlas Brain Region as defined by the brain model ontology."""

    @staticmethod
    def _ontology_location():
        """Return org and proj for ontologies."""
        return "neurosciencegraph", "datamodels"

    @classmethod
    def from_id(
        cls, resource_id, on_no_result=None, base=None, org=None, proj=None, use_auth=None,
        cross_bucket=False, **kwargs
    ):
        """
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. It will receive
                `resource_id` as a first argument.
            kwargs: Keyword arguments which will be forwarded to ``on_no_result`` function.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()

        return super(AtlasBrainRegion, cls).from_id(
            resource_id, on_no_result, base, proj, org, use_auth, **kwargs
        )

    @classmethod
    def from_url(cls, url, base=None, org=None, proj=None, use_auth=None):
        """
        Load entity from url.

        Args:
            url (str): Full url to the entity in nexus. ``_self`` content is a valid full URL.
            use_auth (str): OAuth token in case access is restricted.
                token should be in the format for the authorization header: Bearer VALUE.
        """
        if proj is None and org is None:
            proj, org = cls._ontology_location()
        return super(AtlasBrainRegion, cls).from_url(url, base, org, proj, use_auth)
