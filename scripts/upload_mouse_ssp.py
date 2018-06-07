#!/usr/bin/env python
'''Upload data to nexus
Prerequisites in scripts folder:
    * Prepare scripts/memodel_dirs with mouse SSCx models
    * Prepare scripts/memodel_mods with mouse SSCx mod files
'''
import os

from entity_management.core import Agent, SoftwareAgent
from entity_management.base import OntologyTerm
from entity_management.simulation import (SubCellularModelScript, SubCellularModel, EModelBuilding,
                                          EModelScript, EModel, Morphology, MEModel,
                                          IonChannelMechanismRelease)


TOKEN = os.getenv('NEXUS_TOKEN')


BRAIN_REGION = OntologyTerm(url='http://api.brain-map.org/api/v2/data/Structure/322',
                            label='Primary somatosensory area')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10088',
                       label='Mouse')


agent_name = 'NSE'
agent = Agent.from_name(agent_name, TOKEN)
if agent is None:
    agent = Agent(name=agent_name)
    agent = agent.publish(TOKEN)


bluepyopt = 'BluePyOpt'
bluepyopt_version = '1.6.27'
bluepyopt_agent = SoftwareAgent.from_name(bluepyopt, use_auth=TOKEN)
if bluepyopt_agent is None:
    bluepyopt_agent = SoftwareAgent(name=bluepyopt, version=bluepyopt_version)
    bluepyopt_agent = bluepyopt_agent.publish(TOKEN)


name = 'Mouse SSCx ion channel mechanism release'
mod_release = IonChannelMechanismRelease.from_name(name, TOKEN)
if mod_release is None:
    mod_release = IonChannelMechanismRelease(
            name=name,
            brainRegion=BRAIN_REGION,
            species=SPECIES)
    mod_release = mod_release.publish(TOKEN)


mod_files = 'scripts/memodel_mods'
sub_cellular_models = {}
for mod_name in os.listdir(mod_files):
    mod_file = '%s/%s' % (mod_files, mod_name)
    assert os.path.isfile(mod_file)
    name, ext = os.path.splitext(mod_name)
    assert ext == '.mod'
    model = SubCellularModel.from_name(name, TOKEN)
    if model is None:
        print('Creating mod: %s' % name)
        model_script = SubCellularModelScript(name=name)
        model_script = model_script.publish(TOKEN)
        with open(mod_file) as f:
            # pylint: disable=maybe-no-member
            model_script.attach(mod_name, f, 'application/neuron-mod', TOKEN)
        model = SubCellularModel(name=name,
                                 isPartOf=[mod_release],
                                 modelScript=model_script,
                                 brainRegion=BRAIN_REGION,
                                 species=SPECIES)
        model = model.publish(TOKEN)
    sub_cellular_models[name] = model


models_dir = 'scripts/memodel_dirs'
for model_dir, dirs, files in os.walk(models_dir):
    if 'mechanisms' in dirs and 'morphology' in dirs:
        hoc_files = [f for f in files if f.endswith('.hoc')]
        hoc_files.remove('constants.hoc')
        hoc_files.remove('createsimulation.hoc')
        hoc_files.remove('run.hoc')
        assert len(hoc_files) == 1
        hoc_name = hoc_files[0]
        hoc_file = '%s/%s' % (model_dir, hoc_name)

        model_name = os.path.basename(model_dir)

        morphology_name = os.listdir('%s/morphology' % model_dir)[0]
        morphology_file = '%s/morphology/%s' % (model_dir, morphology_name)
        assert os.path.isfile(morphology_file)
        morphology = Morphology.from_name(model_name, TOKEN)
        if morphology is None:
            morphology = Morphology(model_name)
            morphology = morphology.publish(TOKEN)
            with open(morphology_file) as f:
                # pylint: disable=maybe-no-member
                morphology.attach(morphology_name, f, 'application/neurolucida', TOKEN)

        mechanisms = [sub_cellular_models[os.path.splitext(m)[0]]
                      for m in os.listdir('%s/mechanisms' % model_dir)]

        emodel = EModel.from_name(model_name, TOKEN)
        if emodel is None:
            emodel_script = EModelScript(name=model_name)
            emodel_script = emodel_script.publish(TOKEN)
            with open(hoc_file) as f:
                # pylint: disable=maybe-no-member
                emodel_script.attach(hoc_name, f, 'application/neuron-hoc', TOKEN)

            emodel = EModel(name=model_name,
                            modelScript=[emodel_script],
                            subCellularMechanism=mechanisms,
                            brainRegion=BRAIN_REGION,
                            species=SPECIES)
            emodel = emodel.publish(TOKEN)

            emodel_building = EModelBuilding(used=morphology, generated=emodel,
                                             wasAssociatedWith=[agent, bluepyopt_agent],
                                             wasStartedBy=agent)
            emodel_building = emodel_building.publish(TOKEN)
        else:
            emodel_script = emodel.modelScript[0]

        memodel = MEModel.from_name(model_name, TOKEN)
        if memodel is None:
            print('Creating memodel: %s' % model_name)
            memodel = MEModel(name=model_name,
                              eModel=emodel,
                              morphology=morphology,
                              mainModelScript=emodel_script,
                              brainRegion=BRAIN_REGION,
                              species=SPECIES)
            memodel = memodel.publish(TOKEN)
