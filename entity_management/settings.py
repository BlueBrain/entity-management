# SPDX-License-Identifier: Apache-2.0

"""Settings module"""

import os
import json
import importlib.resources

from rdflib import Namespace

JSLD_ID = "@id"
JSLD_TYPE = "@type"
JSLD_CTX = "@context"
JSLD_REV = "nxv:rev"
JSLD_LINK_REV = "_rev"
JSLD_LINK_TAG = "tag"
JSLD_DEPRECATED = "nxv:deprecated"

USERINFO = os.getenv("NEXUS_USERINFO", "https://bbp.epfl.ch/nexus/v1/identities")
DEFAULT_TAG = "v0.1.0"

# if provided, nexus entities will have wasAttributedTo set to this AGENT
# this is helpful when entity management library is used in some context which
# already established some provenance regarding currently running agent
WORKFLOW = os.getenv("NEXUS_WORKFLOW", None)

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
PROV = Namespace("http://www.w3.org/ns/prov#")
NSG = Namespace("https://neuroshapes.org/")
DASH = Namespace("https://neuroshapes.org/dash/")
NXV = Namespace("https://bluebrain.github.io/nexus/vocabulary/")


with importlib.resources.open_text("entity_management.data", "schema_to_type_mapping.json") as file:
    TYPE_TO_SCHEMA_MAPPING = {type_: schema for schema, type_ in json.load(file)["value"].items()}
