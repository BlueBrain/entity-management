"""Sync type mapping via NEXUS schema to type mapping resource."""

import sys
import json
import logging

from pathlib import Path
from entity_management.nexus import sparql_query, load_by_id
from entity_management.context import get_resolved_context, expand


L = logging.getLogger(__name__)


ORG = "neurosciencegraph"
PROJ = "datamodels"


def main(target_file):
    query = f'''
        PREFIX nxv: <https://bluebrain.github.io/nexus/vocabulary/>
        PREFIX bmoutils: <https://bbp.epfl.ch/ontologies/core/bmoutils/>

        SELECT DISTINCT ?id
        WHERE {{
            ?id a bmoutils:SchemaToTypeMapping ;
            nxv:deprecated   false .
        }}
        LIMIT 1
    '''
    hits = sparql_query(query, org=ORG, proj=PROJ)["results"]["bindings"]

    if not hits:
        raise RuntimeError("No SchemaToTypeMapping Resource found.")

    schema_id = hits[0]["id"]["value"]

    L.info("Found SchemaToTypeMapping id: %s", schema_id)

    jsonld = load_by_id(schema_id, org=ORG, proj=PROJ)

    # expand the schema urls using the context
    schema_to_type_mapping = _expand_mapping(jsonld["@context"], jsonld["value"])

    type_to_schema_mapping = {v: k for k, v in schema_to_type_mapping.items()}

    Path(target_file).write_text(json.dumps(type_to_schema_mapping, indent=2))

    L.info("Type to schema mapping sync with file %s completed.", target_file)


def _expand_mapping(context, mapping):
    """Expand schema urls using the respective context."""

    context = get_resolved_context(context, org=ORG, proj=PROJ)

    expanded_mapping = {expand(context, k): v for k, v in mapping.items()}

    return expanded_mapping


if __name__ == "__main__":
    main(sys.argv[1])

