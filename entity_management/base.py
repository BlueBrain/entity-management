# SPDX-License-Identifier: Apache-2.0

"""
Base simulation entities

.. inheritance-diagram:: entity_management.base
   :parts: 2
"""

import logging
import typing
from datetime import datetime
from pprint import pformat

import attr
from dateutil.parser import parse
from rdflib.graph import BNode, Graph

from entity_management import nexus, typecheck
from entity_management.context import expand, get_resolved_context
from entity_management.settings import (
    DASH,
    JSLD_CTX,
    JSLD_ID,
    JSLD_LINK_REV,
    JSLD_LINK_TAG,
    JSLD_TYPE,
    NSG,
    NXV,
    RDF,
)
from entity_management.state import get_base_resources, get_base_url, get_org, get_proj
from entity_management.util import AttrOf, NotInstantiated, _clean_up_dict, quote

L = logging.getLogger(__name__)

SYS_ATTRS = {
    "_id",
    "_type",
    "_context",
    "_constrainedBy",
    "_createdAt",
    "_createdBy",
    "_deprecated",
    "_project",
    "_rev",
    "_self",
    "_updatedAt",
    "_updatedBy",
}


def _copy_sys_meta(src, dest):
    """Copy system metadata from source to destination entity."""
    for attribute in SYS_ATTRS:
        if hasattr(src, attribute):
            dest._force_attr(attribute, getattr(src, attribute))


def _type_class(type_):
    """Get type class. First try if it's `typing` type class then fallback to regular type."""
    return typing.get_origin(type_) or type_


def custom_getattr(obj, name):
    """Overload of __getattribute__ to trigger instantiation of Nexus object
    if the attribute is NotInstantiated"""
    if name == "__class__" or not isinstance(obj, Identifiable):
        return object.__getattribute__(obj, name)

    value = object.__getattribute__(obj, name)
    if value is NotInstantiated and obj._id is not None:
        obj._instantiate()
        return getattr(obj, name)
    else:
        return value


def attributes(attr_dict=None, repr=True):  # pylint: disable=redefined-builtin
    """decorator to simplify creation of classes that have args and kwargs"""
    if attr_dict is None:
        attr_dict = {}  # just inherit attributes from parent class

    return lambda cls: attr.attrs(cls, these={k: v() for k, v in attr_dict.items()}, repr=repr)


@attr.s
class _NexusBySchemaIterator:
    """Nexus paginated list iterator."""

    cls = attr.ib()
    total_items = attr.ib(type=int, default=None)
    page_from = attr.ib(type=int, default=0)
    page_size = attr.ib(type=int, default=50)
    deprecated = attr.ib(type=bool, default=False)
    base = attr.ib(default=None)
    org = attr.ib(default=None)
    proj = attr.ib(default=None)
    use_auth = attr.ib(default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __iter__(self):
        return self

    def __next__(self):
        """Return next entity from the paginated result set, fetch next page if required"""
        # fetch next page if needed
        if self.total_items is None or self.page_from + self.page_size == self._item_index:
            self.page_from = self._item_index
            data = nexus.load_by_url(
                self.cls.get_constrained_url(base=self.base, org=self.org, proj=self.proj),
                stream=True,
                params={
                    "from": self.page_from,
                    "size": self.page_size,
                    "deprecated": self.deprecated,
                },
                token=self.use_auth,
            )
            graph = Graph().parse(data=data, format="json-ld")
            self.total_items = [
                o for s, o in graph.subject_objects(NXV.total) if isinstance(s, BNode)
            ][0].value
            self._page = [str(subj) for subj in graph.subjects(RDF.type, self.cls._nsg_type)]

        if self._item_index >= self.total_items:
            raise StopIteration()

        id_url = self._page[self._item_index - self.page_from]
        self._item_index += 1
        return self.cls._lazy_init(id_url, base=self.base, org=self.org, proj=self.proj)


@attr.s
class _NexusBySparqlIterator:
    """Nexus paginated list iterator."""

    cls = attr.ib()
    query = attr.ib(type=str)
    base = attr.ib(type=str, default=None)
    org = attr.ib(type=str, default=None)
    proj = attr.ib(type=str, default=None)
    use_auth = attr.ib(type=str, default=None)
    _item_index = attr.ib(type=int, default=0)
    _page = attr.ib(default=None)

    def __iter__(self):
        return self

    def __next__(self):
        """Return next entity from the paginated result set, fetch next page if required"""
        # fetch next page if needed
        if self._page is None:
            json = nexus.sparql_query(
                self.query, base=self.base, org=self.org, proj=self.proj, token=self.use_auth
            )
            self._page = [i["entity"]["value"] for i in json["results"]["bindings"]]

        if self._item_index >= len(self._page):
            raise StopIteration()

        id_url = self._page[self._item_index]
        self._item_index += 1
        return self.cls._lazy_init(id_url, base=self.base, org=self.org, proj=self.proj)


@attr.s(frozen=True)
class Frozen:
    """Utility class making derived classed immutable. Use `evolve` method to introduce changes."""

    def _force_attr(self, attribute, value):
        """Helper method to enforce attribute value on frozen instance"""
        object.__setattr__(self, attribute, value)

    def evolve(self, **changes):
        """Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        """

        obj = attr.evolve(self, **changes)
        return obj


class _RegistryMeta(type):
    """Initialize class variables."""

    def __init__(cls, name, bases, attrs):
        # Always register constrained type hint, so we can recover in a unique way class from
        # _constrainedBy
        constrained_by = str(DASH[name.lower()])
        nexus.register_type(constrained_by, cls)
        # also registre by class name so we can recover from @type
        nexus.register_type(name, cls)

        cls._nsg_type = NSG[name]

        super().__init__(name, bases, attrs)


class BlankNode(Frozen, metaclass=_RegistryMeta):
    """Blank node."""

    def __attrs_post_init__(self):
        self._force_attr("_type", type(self).__name__)


def _serialize_obj(value, include_rev=False):
    """Serialize object"""
    if isinstance(value, OntologyTerm):
        return {JSLD_ID: value.url, "label": value.label}

    if isinstance(value, Identifiable):
        if include_rev:
            return {JSLD_ID: value._id, JSLD_TYPE: value._type, JSLD_LINK_REV: value._rev}
        else:
            return {JSLD_ID: value._id, JSLD_TYPE: value._type}

    if isinstance(value, datetime):
        return value.isoformat()

    if attr.has(type(value)):
        rv = {}
        for attribute in attr.fields(type(value)):
            attr_name = attribute.name
            attr_value = getattr(value, attr_name)
            if attr_value is not None:  # ignore empty values
                if isinstance(attr_value, (tuple, list, set)):
                    rv[attr_name] = [_serialize_obj(i, include_rev) for i in attr_value]
                elif isinstance(attr_value, dict):
                    rv[attr_name] = {
                        kk: _serialize_obj(vv, include_rev) for kk, vv in attr_value.items()
                    }
                else:
                    rv[attr_name] = _serialize_obj(attr_value, include_rev)
        if hasattr(value, "_type"):  # BlankNode have types
            rv[JSLD_TYPE] = value._type
        return rv

    return value


def _deserialize_list(data_type, data_raw, *, context, base, org, proj, token):
    """Deserialize list of json elements"""
    # Enforce a list of a single element if data_raw is not a sequence
    if not typecheck.is_data_sequence(data_raw):
        data_raw = [data_raw]

    if not len(data_raw):
        return None

    type_args = typing.get_args(data_type)

    list_element_type = type_args[0] if type_args else type(data_raw[0])

    result_list = []
    for data_element in data_raw:
        data = _deserialize_json_to_datatype(
            list_element_type,
            data_element,
            context=context,
            base=base,
            org=org,
            proj=proj,
            token=token,
        )
        if data is not None:
            result_list.append(data)

    if not len(result_list):
        return None

    return result_list


def _deserialize_dict(data_type, data_raw, *, context, base, org, proj, token):
    """Deserialize a dict of json elements."""

    # collapse a sequence of one element if the data_type is a mapping
    if typecheck.is_data_sequence(data_raw):
        assert len(data_raw) == 1
        data_raw = data_raw[0]

    if not len(data_raw):
        return None

    type_args = typing.get_args(data_type)
    if type_args:
        assert len(type_args) == 2
        value_type = type_args[1]
    else:
        value_type = None

    return {
        data_key: _deserialize_json_to_datatype(
            value_type or type(data_element),
            data_element,
            context=context,
            base=base,
            org=org,
            proj=proj,
            token=token,
        )
        for data_key, data_element in data_raw.items()
    }


def _deserialize_json_to_datatype(
    data_type, data_raw, *, context=None, base=None, org=None, proj=None, token=None
):
    """Deserialize raw data json to data_type"""
    # pylint: disable=too-many-return-statements
    if data_raw is None:
        return None

    try:
        if data_type in {str, int, float, bool}:
            return data_type(data_raw)

        type_class = _type_class(data_type)

        if typecheck.is_type_sequence(type_class):
            return _deserialize_list(
                data_type, data_raw, context=context, base=base, org=org, proj=proj, token=token
            )

        if typecheck.is_type_mapping(type_class):
            return _deserialize_dict(
                data_type, data_raw, context=context, base=base, org=org, proj=proj, token=token
            )

        if typecheck.is_type_union(type_class):
            return _deserialize_union(
                data_type, data_raw, context=context, base=base, org=org, proj=proj, token=token
            )

        if issubclass(type_class, Identifiable):
            return _deserialize_identifiable(
                data_type, data_raw, base=base, org=org, proj=proj, token=token
            )

        if issubclass(type_class, OntologyTerm):
            return data_type(url=expand(context, data_raw[JSLD_ID]), label=data_raw["label"])

        if issubclass(type_class, Frozen):
            return _deserialize_frozen(
                data_type, data_raw, context=context, base=base, org=org, proj=proj, token=token
            )

        if type_class == datetime:
            return _deserialize_datetime(data_raw)

        # attr classes that are not subclasses of Identifiable or Frozen
        return data_type(**_clean_up_dict(data_raw))

    except Exception:
        L.error("Error deserializing type: %s for raw data:\n%s", data_type, pformat(data_raw))
        raise


def _deserialize_datetime(data_raw):
    if typecheck.is_data_mapping(data_raw):
        return parse(data_raw["@value"])
    return parse(data_raw)


def _deserialize_union(data_type, data_raw, *, context, base, org, proj, token):
    """Deserialize a union of types."""
    type_args = typing.get_args(data_type)

    # e.g. DataDownload | list[DataDownload]
    if typecheck.is_type_single_or_list_union(data_type):
        if typecheck.is_data_sequence(data_raw):
            return _deserialize_list(
                type_args[1],
                data_raw,
                context=context,
                base=base,
                org=org,
                proj=proj,
                token=token,
            )
        return _deserialize_json_to_datatype(
            type_args[0],
            data_raw,
            context=context,
            base=base,
            org=org,
            proj=proj,
            token=token,
        )

    # if data_raw is a json dict with a type, then try to fetch and instantiate that type.
    # Covers subclasses of Identifiable, BlankNode, and their combinations.
    if typecheck.is_data_mapping(data_raw) and JSLD_TYPE in data_raw:
        data_type = nexus.get_type_from_name(data_raw[JSLD_TYPE])
        return _deserialize_json_to_datatype(
            data_type, data_raw, context=context, base=base, org=org, token=token
        )

    # e.g. int | float | dict
    if type(data_raw) in typecheck.get_type_root_args(data_type):
        return data_raw

    raise NotImplementedError(
        "Unknown type/data combination:\n" f"data_type: {data_type}\n" f"data_raw : {data_raw}"
    )


def _deserialize_identifiable(data_type, data_raw, *, base, org, proj, token):
    """Deserialize an Identifiable class."""
    resource_id = data_raw[JSLD_ID]
    type_ = data_raw[JSLD_TYPE]
    rev = data_raw.get(JSLD_LINK_REV, NotInstantiated)
    tag = data_raw.get(JSLD_LINK_TAG, NotInstantiated)

    # if generic Identifiable class is declared find the more specific type
    if data_type is Identifiable:

        # get type class by name from the global registry if present
        data_type = nexus.get_type_from_name(type_)
        if not data_type:
            # otherwise get the class type from the id
            data_type = nexus.get_type_from_id(
                resource_id, base, org, proj, token=token, cross_bucket=True
            )

    return data_type._lazy_init(resource_id, type_, rev=rev, tag=tag, base=base, org=org, proj=proj)


def _deserialize_frozen(data_type, data_raw, context, base, org, proj, token):

    attr_fields = attr.fields_dict(data_type)

    # Blank node is represented as an Identifiable.
    # Get the payload from the id to use as raw data.
    if JSLD_ID in data_raw:
        data_raw = nexus.load_by_id(
            data_raw[JSLD_ID], base=base, org=org, proj=proj, token=token, cross_bucket=True
        )

    field_values = {
        k: _deserialize_json_to_datatype(
            attr_fields[k].type, v, context=context, base=base, org=org, proj=proj, token=token
        )
        for k, v in data_raw.items()
        if k in attr_fields
    }
    data = data_type(**field_values)

    if issubclass(data_type, BlankNode):
        try:
            data._force_attr("_type", data_raw[JSLD_TYPE])
        except KeyError:
            # This is a workaround for entities that need to be migrated from Frozen to BlankNode
            # These resources need to have a @type but it is not yet present in their data. To allow
            # backward compatibity the data type's name is used when type is not found.
            # If all the BlankNode resources have been updated with a @type, this can be removed.
            L.warning("No @type found in BlankNode data. The class type will be used instead.")
    return data


def _deserialize_resource(
    json_ld, cls, *, resolve_context=False, base=None, org=None, proj=None, token=None
):
    """Build class instance from json."""

    if cls == Unconstrained:
        instance = Unconstrained(json=json_ld)
    else:

        if resolve_context and "@context" in json_ld:
            context = get_resolved_context(
                json_ld["@context"], base=base, org=org, proj=proj, token=token
            )
        else:
            context = None

        # prepare all entity init args
        init_args = {}
        for field in attr.fields(cls):
            raw = json_ld.get(field.name)
            if field.init and raw is not None:
                type_ = field.type
                init_args[field.name] = _deserialize_json_to_datatype(
                    type_, raw, context=context, base=base, org=org, proj=proj, token=token
                )
        instance = cls(**init_args)

    # augment instance with extra params present in the response
    instance._force_attr("_id", json_ld.get(JSLD_ID))
    instance._force_attr("_type", json_ld.get(JSLD_TYPE))
    instance._force_attr("_context", json_ld.get(JSLD_CTX))
    for key, value in json_ld.items():
        if key in SYS_ATTRS:
            instance._force_attr(key, value)

    if cls == Unconstrained:
        for sys_attr in SYS_ATTRS:
            json_ld.pop(sys_attr, None)
        json_ld.pop(JSLD_ID, None)
        json_ld.pop(JSLD_TYPE, None)
        json_ld.pop(JSLD_CTX, None)

    return instance


class _IdentifiableMeta(_RegistryMeta):
    """Initialize class variables."""

    def __init__(cls, name, bases, attrs):
        cls.__getattribute__ = custom_getattr
        super().__init__(name, bases, attrs)


@attr.s
class Identifiable(Frozen, metaclass=_IdentifiableMeta):
    """Represents collapsed/lazy loaded entity having type and id.
    Access to any attributes will load the actual entity from nexus and forward property
    requests to that entity.
    """

    _id = None
    _self = NotInstantiated
    _type = NotInstantiated
    _context = NotInstantiated
    _constrainedBy = NotInstantiated
    _createdAt = NotInstantiated
    _createdBy = NotInstantiated
    _deprecated = NotInstantiated
    _project = NotInstantiated
    _rev = NotInstantiated
    _tag = NotInstantiated
    _updatedAt = NotInstantiated
    _updatedBy = NotInstantiated

    @classmethod
    def _lazy_init(
        cls,
        resource_id,
        type_=NotInstantiated,
        rev=NotInstantiated,
        tag=NotInstantiated,
        base=None,
        org=None,
        proj=None,
    ):
        """Instantiate an object and put all its attributes to NotInstantiated."""
        # Running the validator has the side effect of instantiating
        # the object, which we do not want
        attr.set_run_validators(False)
        obj = cls(**{arg.name: NotInstantiated for arg in attr.fields(cls)})
        obj._force_attr("_id", resource_id)
        obj._force_attr("_type", type_)
        obj._force_attr("_rev", rev)
        obj._force_attr("_tag", tag)
        obj._force_attr("_lazy_meta_", (base, org, proj))
        attr.set_run_validators(True)
        return obj

    @classmethod
    def get_constrained_url(cls, base=None, org=None, proj=None):
        """Get schema constrained url."""
        constrained_by = str(DASH[cls.__name__.lower()])
        return f"{get_base_resources(base)}/{get_org(org)}/{get_proj(proj)}/{quote(constrained_by)}"

    @classmethod
    def from_id(
        cls,
        resource_id,
        *,
        on_no_result=None,
        cross_bucket=False,
        resolve_context=False,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
        **kwargs,
    ):
        """
        Load entity from resource id.

        Args:
            resource_id (str): id of the entity to load.
            on_no_result (Callable): A function to be called when no result found. It will receive
                `resource_id` as a first argument.
            cross_bucket (bool):
                Use the resolvers instead of the resources endpoint. Default False.
            resolve_context (bool):
                Resolve ontological term curies using the resource's context. Default False.
            kwargs: Keyword arguments which will be forwarded to ``on_no_result`` function.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        json_ld = nexus.load_by_id(
            resource_id=resource_id,
            cross_bucket=cross_bucket,
            base=base,
            org=org,
            proj=proj,
            token=use_auth,
        )

        if json_ld is not None:
            return _deserialize_resource(
                json_ld,
                cls,
                resolve_context=resolve_context,
                base=base,
                org=org,
                proj=proj,
                token=use_auth,
            )
        elif on_no_result is not None:
            return on_no_result(
                resource_id, base=base, org=org, proj=proj, use_auth=use_auth, **kwargs
            )
        else:
            return None

    @classmethod
    def from_url(cls, url, *, resolve_context=False, base=None, org=None, proj=None, use_auth=None):
        """
        Load entity from url.

        Args:
            url (str): Full url to the entity in nexus. ``_self`` content is a valid full URL.
            resolve_context (bool):
                Resolve ontological term curies using the resource's context. Default False.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        json_ld = nexus.load_by_url(url, token=use_auth)

        if json_ld is not None:
            return _deserialize_resource(
                json_ld,
                cls,
                resolve_context=resolve_context,
                base=base,
                org=org,
                proj=proj,
                token=use_auth,
            )
        else:
            return None

    @classmethod
    def list_by_schema(cls, **kwargs):
        """List all instances belonging to the schema this type defines.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        """
        return _NexusBySchemaIterator(cls, **kwargs)

    def get_id(self):
        """Retrieve _id property."""
        return self._id

    def get_rev(self):
        """Retrieve _rev property."""
        return self._rev

    def get_url(self):
        """Retrieve URL of the nexus entity.

        Returns:
            Content of the ``_self`` property.
        """
        return self._self

    def as_json_ld(self, include_rev=False):
        """Get json-ld representation of the Entity
        Return json with added json-ld properties such as @context and @type
        """
        if isinstance(self, Unconstrained):
            return self.json  # pylint: disable=no-member

        json_ld = {}
        for attribute in attr.fields(type(self)):
            attr_value = getattr(self, attribute.name)
            if attr_value is not None:  # ignore empty values
                attr_name = attribute.name
                if typecheck.is_data_sequence(attr_value):
                    json_ld[attr_name] = [_serialize_obj(i, include_rev) for i in attr_value]
                elif typecheck.is_data_mapping(attr_value):
                    json_ld[attr_name] = {
                        kk: _serialize_obj(vv, include_rev) for kk, vv in attr_value.items()
                    }
                else:
                    json_ld[attr_name] = _serialize_obj(attr_value, include_rev)
        if hasattr(self, "_context") and self._context is not NotInstantiated:
            json_ld[JSLD_CTX] = self._context
        else:
            json_ld[JSLD_CTX] = ["https://bbp.neuroshapes.org"]
            # json_ld[JSLD_CTX] = ['https://bluebrainnexus.io/contexts/shacl-20170720.json',
            #                      'https://bluebrainnexus.io/contexts/resource.json',
            #                      'https://incf.github.io/neuroshapes/contexts/data.json']

        # obj was already deserialized from nexus => we have type
        # or we explicitly set the _type in the class
        if self._type is not NotInstantiated:
            json_ld[JSLD_TYPE] = self._type  # pylint: disable=no-member
        else:  # by default use class name
            json_ld[JSLD_TYPE] = type(self).__name__
        return json_ld

    def publish(
        self,
        *,
        resource_id=None,
        sync_index=False,
        base=None,
        org=None,
        proj=None,
        use_auth=None,
        include_rev=False,
    ):
        """Create or update entity in nexus. Makes a remote call to nexus instance to persist
        entity attributes.

        Args:
            resource_id (str): Resource identifier. If not provided nexus will generate one.
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
            include_rev (bool): Whether to include _rev in the linked entities or not.
        Returns:
            New instance of the same class with revision updated.
        """
        payload = self.as_json_ld(include_rev)

        if self._id:
            json_ld = nexus.update(
                self._self,
                self._rev,
                payload,
                sync_index=sync_index,
                token=use_auth,
            )
        else:
            json_ld = nexus.create(
                get_base_url(base, org, proj),
                payload,
                resource_id,
                sync_index=sync_index,
                token=use_auth,
            )

        # Nexus truncates the contexts and expands the bmo types. For example:
        #
        # '@type': [
        #   'CellCompositionConfig',
        #   'Entity',
        # ]
        #
        # will be returned in the response without the neuroshapes context as:
        #
        # '@type': [
        #   'https://bbp.epfl.ch/ontologies/core/bmo/CellCompositionConfig',
        #   'http://www.w3.org/ns/prov#Entity',
        # ],
        #
        # To avoid this the payload's type, which is shrunk due to the resource's context, is used
        # wherever possible to address this inconsistency.
        if JSLD_TYPE in payload:
            json_ld[JSLD_TYPE] = payload[JSLD_TYPE]

        self._process_response(json_ld)
        return self

    def _process_response(self, json_ld):
        for sys_attr in SYS_ATTRS:
            if sys_attr in json_ld:
                self._force_attr(sys_attr, json_ld[sys_attr])
        self._force_attr("_id", json_ld.get(JSLD_ID))
        self._force_attr("_type", json_ld.get(JSLD_TYPE))

    def _instantiate(self):
        """Fetch nexus object with id=self._id if it was not initialized before."""
        if hasattr(self, "_lazy_meta_"):
            base, org, proj = getattr(self, "_lazy_meta_")
        else:
            base, org, proj = (None, None, None)

        # use the revision or tag in the retrieval if they are priori available
        tag = object.__getattribute__(self, "_tag")
        rev = object.__getattribute__(self, "_rev")

        # note that tag is given precedence over _rev becauce it avoids replaying history up to that
        # revision, and is therefore faster
        if tag is not NotInstantiated:
            resource_id = f"{self._id}?tag={tag}"
        elif rev is not NotInstantiated:
            resource_id = f"{self._id}?rev={rev}"
        else:
            resource_id = self._id

        fetched_instance = type(self).from_id(
            resource_id, base=base, org=org, proj=proj, cross_bucket=True
        )

        for attribute in attr.fields(type(self)):
            self._force_attr(attribute.name, getattr(fetched_instance, attribute.name))
        _copy_sys_meta(fetched_instance, self)

    def deprecate(self, sync_index=False, use_auth=None):
        """Mark entity as deprecated.
        Deprecated entities are not possible to retrieve by name.

        Args:
            use_auth (str): OAuth token in case access is restricted.
                Token should be in the format for the authorization header: Bearer VALUE.
        """
        nexus.deprecate(self._self, self._rev, sync_index=sync_index, token=use_auth)
        return self

    def evolve(self, **changes):
        """Create new instance of the frozen(immutable) object with *changes* applied.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        """
        obj = attr.evolve(self, **changes)
        _copy_sys_meta(self, obj)
        return obj

    def clone(self, **changes):
        """Create new instance of the frozen(immutable) object with *changes* applied.

        Note: A clone is stripped of its id if present.

        Args:
            changes: Keyword changes in the new copy, should be a subset of class
                constructor(__init__) keyword arguments.
        Returns:
            New instance of the same class with changes applied.
        """
        obj = self.evolve(**changes)
        obj._force_attr("_id", None)
        return obj


@attributes(
    {
        "json": AttrOf(dict),
    }
)
class Unconstrained(Identifiable):
    """Shapeless data.

    Args:
        json (dict): python dictionary which will be seralized into json.
    """

    _url_schema = "_"


@attributes(
    {
        "value": AttrOf(str),
        "unitText": AttrOf(str, default=None),
        "unitCode": AttrOf(str, default=None),
    }
)
class QuantitativeValue(Frozen):
    """External resource representations,
    this can be a file or a folder on gpfs

    Args:
        value (str): Value.
        unitText (str): Unit text.
        unitCode (str): The unit of measurement given using the UN/CEFACT Common Code (3 characters)
            or a URL. Other codes than the UN/CEFACT Common Code may be used with a prefix followed
            by a colon.
    """


@attributes(
    {
        "url": AttrOf(str),
        "label": AttrOf(str, default=None),
    }
)
class OntologyTerm(Frozen):
    """Ontology term such as brain region or species

    Args:
        url (str): Ontology term url identifier.
        label (str): Label for the ontology term.
    """


@attributes({"brainRegion": AttrOf(OntologyTerm)})
class BrainLocation(BlankNode):
    """Brain location.

    Args:
        brainRegion (OntologyTerm): Brain region ontology term.
    """


@attributes(
    {
        "entity": AttrOf(Identifiable),
    }
)
class Derivation(BlankNode):
    """Derivation."""


@attributes(
    {
        "species": AttrOf(OntologyTerm, default=None),
        "strain": AttrOf(OntologyTerm, default=None),
    }
)
class Subject(BlankNode):
    """Subject.

    Args:
        name (str): Subject name.
        species (OntologyTerm): Species ontology term.
        strain (OntologyTerm): Strain ontology term.
    """
