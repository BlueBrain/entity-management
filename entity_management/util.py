# SPDX-License-Identifier: Apache-2.0

"""Utilities"""

import sys
import typing
from functools import wraps
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import quote as parse_quote
from urllib.parse import unquote, urlparse

import attr
import jsonschema
import yaml
from attr.validators import instance_of as instance_of_validator
from attr.validators import optional as optional_validator

from entity_management import state, typecheck
from entity_management.exception import (
    EntityNotInstantiatedError,
    ResourceNotFoundError,
    SchemaValidationError,
)

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources

# copied from attrs, their standard way to make validators


@attr.s(repr=False, slots=True, hash=True)
class LazySchemaValidator:
    """Validate lazily the distribution schema.

    The validator decorates DataDownload's as_dict method by enforcing schema validation.

    Attributes:
        schema: The schema filename located at entity_management/schemas. Example: my_schema.yml
    """

    schema = attr.ib()

    @property
    def _schema_path(self):
        return resources.files(__package__) / "schemas" / self.schema

    def __attrs_post_init__(self):
        if not self._schema_path.exists():
            raise FileNotFoundError(f"Schema {self.schema} not found.")

    def _lazy_schema_validation(self, func):
        """Decorator for adding schema validation to as_dict method."""

        @wraps(func)
        def validated(*args, **kwargs):
            result = func(*args, **kwargs)
            validate_schema(data=result, schema_name=self.schema)
            return result

        return validated

    def __call__(self, inst, attribute, value):
        """Lazily apply schema validator to as_dict method.

        Note: It mutates the Frozen DataDownload in order to introduce this behavior.
        """
        if not hasattr(value, "as_dict"):
            raise RuntimeError(f"Expected instance with as_dict method. Got {value}")

        try:
            old_method = value.as_dict
        except AttributeError as e:
            raise RuntimeError(
                f"Expected instance with 'as_dict' method, e.g. a DataDownload. Got {value}"
            ) from e

        decorated_method = self._lazy_schema_validation(old_method)
        value._force_attr("as_dict", decorated_method)


@attr.s(repr=False, slots=True, hash=True)
class _ListOfValidator:
    """Validate list of type"""

    type_ = attr.ib()
    default = attr.ib()

    def __call__(self, inst, attribute, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if self.default is not None and value is None:
            raise TypeError(f"'{attribute.name}' must be provided", attribute, self.type_, value)

        if value is not None:
            if not typecheck.is_data_sequence(value):
                raise TypeError(f"'{attribute.name}' must be a list", attribute, self.type_, value)
            if not all(isinstance(v, self.type_) for v in value):
                raise TypeError(
                    f"'{attribute.name}' must be list of {self.type_!r} (got {value!r} that is a "
                    f"{type(value)!r}).",
                    attribute,
                    self.type_,
                    value,
                )

    def __repr__(self):
        return f"<instance_of validator for list of type {self.type_!r}>"


class _OneOrListValidator(_ListOfValidator):

    def __call__(self, inst, attribute, value):

        if value is not None and not typecheck.is_data_sequence(value):
            value = [value]

        super().__call__(inst, attribute, value)


def _list_of(type_, default):
    """
    A validator that raises a :exc:`TypeError` if the initializer is called
    with a list of wrong types for this particular attribute (checks are performed
    using :func:`isinstance` therefore it's also valid to pass a tuple of types).

    :param type_: The type to check for.
    :type type_: type or tuple of types

    :raises TypeError: With a human readable error message, the attribute
        (of type :class:`attr.Attribute`), the expected type, and the value it
        got.
    """
    return _ListOfValidator(type_, default)


def _one_or_list_of(type_, default):
    return _OneOrListValidator(type_, default)


@attr.s(repr=False, slots=True, hash=True)
class _NotInstatiatedValidator:
    """A validator that allows NotInstantiated values."""

    validator = attr.ib()

    def __call__(self, inst, attribute, value):
        if value is NotInstantiated:
            return

        self.validator(inst, attribute, value)  # pylint: disable=not-callable

    def __repr__(self):
        return f"<not instantiated validator for {repr(self.validator)} or None>"


class NotInstantiated:
    """A class for not instantiated attributes
    Trying to access an attribute with this value will trigger
    the instantiation. A Nexus query will be performed and the attribute
    will be filled with the real value"""

    def __repr__(self):
        return "<not instantiated>"


def _get_union_params(union):
    """Return Union elements for all python"""
    try:
        return union.__args__
    except AttributeError:
        return union.__union_params__


def _get_list_params(a_list):
    """Return List elements for all python"""
    try:
        return a_list.__args__
    except AttributeError:
        return a_list.__parameters__


class AttrOf:
    """Create an object with self.fn(Callable) that will be used to create an attr.ib by invoking
    Callable.

    .. deprecated:: 1.2.9
        Use regular attrs. This used to do some magic for previous versions of attrs.
    """

    def __init__(self, type_, default=attr.NOTHING, validators=None):

        validators = _make_validators(type_, default, validators)

        self.fn = lambda: attr.ib(
            type=type_, default=default, validator=validators, repr=False, kw_only=True
        )

    def __call__(self):
        return self.fn()


def _make_validators(type_, default, custom_validators):

    def instance_of(type_):
        """instance_of"""
        return _NotInstatiatedValidator(instance_of_validator(type_))

    def optional_of(type_):
        """optional_of"""
        return optional_validator(instance_of(type_))

    if typecheck.is_type_sequence(type_):
        # the collection was explicitly specified in attr.ib
        # like typing.List[Distribution]
        list_element_type = _get_list_params(type_)[0]
        if typecheck.is_type_union(list_element_type):
            types = _get_union_params(list_element_type)
            validator = _list_of(types, default)
        else:
            validator = _list_of(list_element_type, default)
    # e.g. A | list[A]
    elif typecheck.is_type_single_or_list_union(type_):
        element_type = typing.get_args(type_)[0]
        validator = _one_or_list_of(element_type, default)
    # e.g A | B
    elif typecheck.is_type_union(type_):
        types = _get_union_params(type_)
        validator = instance_of(types)
    else:
        if default is None:  # default explicitly provided as None
            validator = optional_of(type_)
        else:  # default either not provided -> mandatory, or initialized with value
            validator = instance_of(type_)

    validators = [validator]

    if custom_validators is not None:
        validators += (
            custom_validators if isinstance(custom_validators, list) else [custom_validators]
        )

    return validators


def _clean_up_dict(d):
    """Produce new dictionary without json-ld attrs which start with @"""
    return {k: v for k, v in d.items() if not k.startswith("@")}


def quote(url):
    """Helper function for urllib.parse.quote with safe=""."""
    return parse_quote(url, safe="")


def split_url_params(url):
    """Split url from revision query."""
    res = urlparse(url)
    url = f"{res.scheme}://{res.netloc}{res.path}"
    params = parse_qs(res.query)
    return url, params


def unquote_uri_path(uri):
    """Convert a file uri to a system path.

    Example:
        file:///%5BPH%5Dlayer_6.nrrd -> /[PH]layer_6.nrrd
    """
    return unquote(urlparse(uri).path)


def get_entity(
    resource_id: str,
    *,
    cls,
    cross_bucket: bool = True,
    resolve_context: bool = False,
    base: Optional[str] = None,
    org: Optional[str] = None,
    proj: Optional[str] = None,
    token: Optional[str] = None,
):
    """Instantiate an entity from a resource id.

    Args:
        resource_id: The string id of the KG resource.
        cls: entity-management class to instantiate.
        cross_bucket: Whether to use the resolvers to get the resource. Default is True.
        base: Optional nexus base endpoint. Default is retrieved from global state.
        org: Optional nexus organization. Default is retrieved from global state.
        proj: Optional nexus project. Default is retrieved from global state.
        token: Optional OAuth token. Default is retrieved from global state.

    Returns:
        Instantiated entity from given id.

    Raises:
        ResourceNotFoundError if entity is not found.
        EntityNotInstantiatedError if entity fails to be instantiated.
    """
    try:
        entity = cls.from_id(
            resource_id,
            cross_bucket=cross_bucket,
            resolve_context=resolve_context,
            base=base,
            org=org,
            proj=proj,
            use_auth=token,
        )
    except Exception as e:
        raise EntityNotInstantiatedError(
            f"Entity {cls} failed to be instantiated from id {resource_id}."
        ) from e

    if entity is None:
        raise ResourceNotFoundError(
            f"Resource id {resource_id} could not be retrieved.\n"
            f"base         : {base or state.get_base()}\n"
            f"org          : {org or state.get_org()}\n"
            f"proj         : {proj or state.get_proj()}\n"
            f"cross_bucket : {cross_bucket}"
        )
    return entity


def validate_schema(data: dict, schema_name: str) -> None:
    """Validata data against the schema with 'schema_name'."""

    def _read_schema(schema_name: str) -> dict:
        """Load a schema and return the result as a dictionary."""
        resource = resources.files(__package__) / "schemas" / schema_name
        content = resource.read_text()
        return yaml.safe_load(content)

    def _format_error(error) -> str:
        paths = " -> ".join(map(str, error.absolute_path))
        return f"[{paths}]: {error.message}"

    schema = _read_schema(schema_name)

    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)
    errors = validator.iter_errors(data)

    messages = []
    for error in errors:
        if error.context:
            messages.extend(map(_format_error, error.context))
        else:
            messages.append(_format_error(error))

    if messages:
        raise SchemaValidationError("\n".join(messages))
