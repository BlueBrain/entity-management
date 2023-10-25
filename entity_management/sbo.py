from entity_management.core import Entity
from entity_management.base import attributes
from entity_management.util import AttrOf2


@attributes({
    "configs": AttrOf2(dict[str, Entity])
})
class ModelBuildingConfig(Entity):
    pass
