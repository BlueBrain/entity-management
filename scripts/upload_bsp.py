#!/usr/bin/env python
'''Upload data to nexus'''
import os

from entity_management.prov import Agent
from entity_management.base import OntologyTerm
from entity_management.simulation.cell import (SubCellularModelScript, SubCellularModel,
                                               EModelScript, EModel, Morphology, MEModel)


TOKEN = os.getenv('NEXUS_TOKEN')


BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                            label='field CA1 of the hippocampus')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116',
                       label='Rattus norvegicus')

agent_name = 'NSE'
agent = Agent.from_name(agent_name, TOKEN)
if agent is None:
    agent = Agent(name=agent_name)
    agent = agent.save(TOKEN)

mod_files = 'scripts/hbp-bsp-models/mod_files'
sub_cellular_models = {}
for mod_name in os.listdir(mod_files):
    mod_file = '%s/%s' % (mod_files, mod_name)
    assert os.path.isfile(mod_file)
    name, ext = os.path.splitext(mod_name)
    assert ext == '.mod'
    print('Creating mod: %s' % name)
    model = SubCellularModel.from_name(name, TOKEN)
    if model is None:
        model_script = SubCellularModelScript(name=name)
        model_script = model_script.save(TOKEN)
        with open(mod_file) as f:
            model_script.attach(mod_name, f, 'application/neuron-mod', TOKEN)
        model = SubCellularModel(name=name,
                                 modelScript=model_script,
                                 brainRegion=BRAIN_REGION,
                                 species=SPECIES)
        model = model.save(TOKEN)
    sub_cellular_models[name] = model


models_dir = 'scripts/models'
for model_name in os.listdir(models_dir):
    model_dir = '%s/%s' % (models_dir, model_name)
    if os.path.isdir(model_dir):
        hoc_file = '%s/checkpoints/cell.hoc' % model_dir
        assert os.path.isfile(hoc_file)
        emodel_script = EModelScript.from_name(model_name, TOKEN)
        if emodel_script is None:
            emodel_script = EModelScript(name=model_name)
            emodel_script = emodel_script.save(TOKEN)
            with open(hoc_file) as f:
                emodel_script.attach('cell.hoc', f, 'application/neuron-hoc', TOKEN)

        morphology_name = os.listdir('%s/morphology' % model_dir)[0]
        morphology_file = '%s/morphology/%s' % (model_dir, morphology_name)
        assert os.path.isfile(morphology_file)
        morphology = Morphology.from_name(model_name, TOKEN)
        if morphology is None:
            morphology = Morphology(model_name)
            morphology = morphology.save(TOKEN)
            with open(morphology_file) as f:
                morphology.attach(morphology_name, f, 'application/neurolucida', TOKEN)

        mechanisms = [sub_cellular_models[os.path.splitext(m)[0]]
                      for m in os.listdir('%s/mechanisms' % model_dir)]
        emodel = EModel.from_name(model_name, TOKEN)
        if emodel is None:
            emodel = EModel(name=model_name,
                            subCellularMechanism=mechanisms,
                            brainRegion=BRAIN_REGION,
                            species=SPECIES)
            emodel = emodel.save(TOKEN)

        memodel = MEModel.from_name(model_name, TOKEN)
        if memodel is None:
            print('Creating memodel: %s' % model_name)
            memodel = MEModel(name=model_name,
                              eModel=emodel,
                              morphology=morphology,
                              modelScript=emodel_script,
                              brainRegion=BRAIN_REGION,
                              species=SPECIES)
            memodel = memodel.save(TOKEN)
