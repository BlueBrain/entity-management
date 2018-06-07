#!/usr/bin/env python
'''Upload data to nexus'''
import os

from entity_management.base import OntologyTerm
from entity_management.simulation import (SubCellularModelScript, SubCellularModel,
                                          EModelScript, EModel, Morphology, MEModel)


TOKEN = os.getenv('NEXUS_TOKEN')


# BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
#                             label='field CA1 of the hippocampus')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10088',
                       label='Mouse')

mod_files = os.path.expanduser('/gpfs/bbp.cscs.ch/project/proj55/singlecell/e-models/mechanisms')
mechanisms = []
for mod_name in os.listdir(mod_files):
    mod_file = '%s/%s' % (mod_files, mod_name)
    assert os.path.isfile(mod_file)
    name, ext = os.path.splitext(mod_name)
    assert ext == '.mod'
    print('Creating mod: %s' % name)
    model = SubCellularModel.from_name(name, TOKEN)
    if model is None:
        model_script = SubCellularModelScript(name=name)
        model_script = model_script.publish(TOKEN)
        with open(mod_file) as f:
            # pylint: disable=maybe-no-member
            model_script.attach(mod_name, f, 'application/neuron-mod', TOKEN)
        model = SubCellularModel(name=name,
                                 modelScript=model_script,
                                 # brainRegion=BRAIN_REGION,
                                 species=SPECIES)
        model = model.publish(TOKEN)
    mechanisms.append(model)


model_name = 'Thalamo-cortical neuron'
model_desc = 'E-model of a thalamo-cortical neuron of the mouse VPL nucleus'

hoc_file = os.path.expanduser(
        '/gpfs/bbp.cscs.ch/project/proj55/singlecell/e-models/bAC_TC_VPL_2d79e9c_2.hoc')
assert os.path.isfile(hoc_file)
emodel_script = EModelScript.from_name(model_name, TOKEN)
if emodel_script is None:
    emodel_script = EModelScript(name=model_name)
    emodel_script = emodel_script.publish(TOKEN)
    with open(hoc_file) as f:
        # pylint: disable=maybe-no-member
        emodel_script.attach('cell.hoc', f, 'application/neuron-hoc', TOKEN)

morphology_name = 'R281HI-6-6-16_ventralneuron'
morphology = Morphology.from_name(morphology_name, TOKEN)
if morphology is None:
    morphology = Morphology(name=morphology_name)
    morphology = morphology.publish(TOKEN)

    morphology_file = os.path.expanduser(
            '/gpfs/bbp.cscs.ch/project/proj55/singlecell/e-models/morphology/'
            'R281HI-6-6-16_ventralneuron.asc')
    assert os.path.isfile(morphology_file)
    with open(morphology_file) as f:
        # pylint: disable=maybe-no-member
        morphology.attach('%s.asc' % morphology_name, f, 'application/neurolucida', TOKEN)

emodel = EModel.from_name(model_name, TOKEN)
if emodel is None:
    emodel = EModel(name=model_name,
                    subCellularMechanism=mechanisms,
                    # brainRegion=BRAIN_REGION,
                    species=SPECIES)
    emodel = emodel.publish(TOKEN)

memodel = MEModel.from_name(model_name, TOKEN)
if memodel is None:
    memodel = MEModel(name=model_name,
                      eModel=emodel,
                      morphology=morphology,
                      mainModelScript=emodel_script,
                      # brainRegion=BRAIN_REGION,
                      species=SPECIES)
    memodel = memodel.publish(TOKEN)
