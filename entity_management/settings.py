# SPDX-License-Identifier: Apache-2.0

"""Settings module"""

import json
import os
from pathlib import Path

from rdflib import Namespace

JSLD_ID = "@id"
JSLD_TYPE = "@type"
JSLD_CTX = "@context"
JSLD_REV = "nxv:rev"
JSLD_LINK_REV = "_rev"
JSLD_LINK_TAG = "tag"
JSLD_DEPRECATED = "nxv:deprecated"

SCHEMA_UNCONSTRAINED = "https://bluebrain.github.io/nexus/schemas/unconstrained.json"

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


TYPE_TO_SCHEMA_MAPPING_FILE = Path(__file__).parent / "data/type_to_schema_mapping.json"
TYPE_TO_SCHEMA_MAPPING = json.loads(TYPE_TO_SCHEMA_MAPPING_FILE.read_bytes())
