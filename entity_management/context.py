# SPDX-License-Identifier: Apache-2.0

"""Context related functions."""

from __future__ import annotations

from typing import Any

from rdflib.plugins.shared.jsonld.context import Context

from entity_management import nexus

_CONTEXT_CACHE = {}
_IGNORED_CONTEXTS = {
    "https://bluebrain.github.io/nexus/contexts/metadata.json",
    "https://bluebrainnexus.io/contexts/metadata.json",
}


def expand(context: Context | None, term_curie_or_iri: Any, use_vocab: bool = True) -> str:
    """Expand term using the context if it exists or return the term otherwise."""
    return context.expand(term_curie_or_iri, use_vocab) if context else term_curie_or_iri


def get_resolved_context(obj, *, base=None, org=None, proj=None, token=None):
    """Get resolved context.

    Args:
        obj: Either a resource id or the jsonld['@context'] contents.


    Returns:
        Resolved Context instance.
    """
    document = _resolve_context(obj, visited=set(), base=base, org=org, proj=proj, token=token)
    return Context(document, version=1.1)


def _load_context(resource_id, base=None, org=None, proj=None, token=None):

    if resource_id in _CONTEXT_CACHE:
        return _CONTEXT_CACHE[resource_id]

    data = nexus.load_by_id(
        resource_id, base=base, org=org, proj=proj, token=token, cross_bucket=True
    )

    assert data is not None, f"Failed to fetch context with id {resource_id}"

    if "@context" in data:
        data = data["@context"]

    _CONTEXT_CACHE[resource_id] = data
    return data


def _clean(data):
    return (d for d in data if not (isinstance(d, str) and d in _IGNORED_CONTEXTS))


def _resolve_context(context, visited, base=None, org=None, proj=None, token=None):

    document = {}
    if isinstance(context, dict):
        document.update(context)
    elif isinstance(context, list):
        for entry in _clean(context):
            result = _resolve_context(
                context=entry,
                visited=visited,
                base=base,
                org=org,
                proj=proj,
                token=token,
            )
            document.update(result)
    elif isinstance(context, str) and context not in visited:
        visited.add(context)
        result = _load_context(context, base=base, org=org, proj=proj, token=token)
        result = _resolve_context(
            result, visited=visited, base=base, org=org, proj=proj, token=token
        )
        document.update(result)

    return document
