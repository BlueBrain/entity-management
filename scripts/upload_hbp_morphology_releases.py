#!/usr/bin/env python
'''Upload MorphologyRelease
'''
import os

from entity_management.base import OntologyTerm
from entity_management.simulation import MorphologyRelease


TOKEN = os.getenv('NEXUS_TOKEN')


HIPPOCAMPUS = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                           label='field CA1 of the hippocampus')
RAT = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116', label='Rattus norvegicus')

CORTEX = OntologyTerm(url='http://api.brain-map.org/api/v2/data/Structure/322',
                      label='Primary somatosensory area')
MOUSE = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10088', label='Mouse')


name = 'Rat hippocampus morphology release'
morpho_release = next(MorphologyRelease.find_by(name=name, use_auth=TOKEN), None)
if morpho_release is None:
    morpho_release = MorphologyRelease(name=name, brainRegion=HIPPOCAMPUS, species=RAT)
    morpho_release = morpho_release.publish(use_auth=TOKEN)

name = 'Mouse primary somatosensory area morphology release'
morpho_release = next(MorphologyRelease.find_by(name=name, use_auth=TOKEN), None)
if morpho_release is None:
    morpho_release = MorphologyRelease(name=name, brainRegion=CORTEX, species=MOUSE)
    morpho_release = morpho_release.publish(use_auth=TOKEN)
