#!/usr/bin/env python
'''Upload data to nexus
Prerequisites in scripts folder:
    (cd scripts && git clone https://github.com/lbologna/bsp_data_repository.git)
    (cd scripts/bsp_data_repository &&
    find . -name '*.zip'
    -exec unzip '{}' -x '*.pdf' -x '*.pkl' -x '*.json' -x '*.txt' -d ../models/ ';')
    cp -r /gpfs/bbp.cscs.ch/project/proj66/home/vangeit/src/NeuroMLExport/\
            cellmodels/SuppWebsite.mousify/output.20180316/memodel_dirs scripts/
'''
import os
import json

from entity_management.core import Agent, SoftwareAgent
from entity_management.base import OntologyTerm, Distribution
from entity_management.simulation import (SubCellularModelScript, SubCellularModel, EModelBuilding,
                                          EModelScript, EModel, Morphology, MEModel,
                                          IonChannelMechanismRelease)


TOKEN = os.getenv('NEXUS_TOKEN')


BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                            label='field CA1 of the hippocampus')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116',
                       label='Rattus norvegicus')


agent_name = 'NSE'
agent = Agent.from_name(agent_name, TOKEN)
if agent is None:
    agent = Agent(name=agent_name)
    agent = agent.publish(TOKEN)


bluepyopt = 'BluePyOpt'
bluepyopt_agent = SoftwareAgent.from_name(bluepyopt, TOKEN)
if bluepyopt_agent is None:
    bluepyopt_agent = SoftwareAgent(name=bluepyopt, version='1.5.29')
    bluepyopt_agent = bluepyopt_agent.publish(TOKEN)


name = 'Hippocampus ion channel mechanism release'
mod_release = IonChannelMechanismRelease.from_name(name, TOKEN)
if mod_release is None:
    print('Creating IonChannelMechanismRelease: %s' % name)
    mod_release = IonChannelMechanismRelease(
            name=name,
            distribution=Distribution(
                accessURL='https://github.com/cnr-ibf-pa/hbp-bsp-models/releases/tag/v1.0.1'),
            brainRegion=BRAIN_REGION,
            species=SPECIES)
    mod_release = mod_release.publish(TOKEN)

mod_files = 'scripts/hbp-bsp-models/mod_files'
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


bsp_data_repository = 'scripts/bsp_data_repository/optimizations'
models_dir = 'scripts/models'
for model_name in os.listdir(models_dir):
    model_dir = '%s/%s' % (models_dir, model_name)
    if os.path.isdir(model_dir):
        with open('%s/%s/%s_meta.json' % (bsp_data_repository, model_name, model_name)) as f:
            meta_info = json.load(f)
        best_cell = str(meta_info['best_cell'])

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
            model_scripts = []
            for hoc_file in os.listdir('%s/checkpoints' % model_dir):
                hoc_path = '%s/checkpoints/%s' % (model_dir, hoc_file)
                assert os.path.isfile(hoc_path)
                name, ext = os.path.splitext(hoc_file)
                assert ext == '.hoc'

                emodel_script = EModelScript(name=name)
                emodel_script = emodel_script.publish(TOKEN)
                with open(hoc_path) as f:
                    # pylint: disable=maybe-no-member
                    emodel_script.attach(hoc_file, f, 'application/neuron-hoc', TOKEN)
                model_scripts.append(emodel_script)

                if hoc_file == best_cell:
                    main_model_script = emodel_script # best_cell will be referenced from memodel

            emodel = EModel(name=model_name,
                            modelScript=model_scripts,
                            subCellularMechanism=mechanisms,
                            brainRegion=BRAIN_REGION,
                            species=SPECIES)
            emodel = emodel.publish(TOKEN)

            emodel_building = EModelBuilding(used=morphology, generated=emodel,
                                             wasAssociatedWith=[agent, bluepyopt_agent],
                                             wasStartedBy=agent)
            emodel_building = emodel_building.publish(TOKEN)

        memodel = MEModel.from_name(model_name, TOKEN)
        if memodel is None:
            print('Creating memodel: %s' % model_name)
            memodel = MEModel(name=model_name,
                              eModel=emodel,
                              morphology=morphology,
                              mainModelScript=main_model_script,
                              brainRegion=BRAIN_REGION,
                              species=SPECIES)
            memodel = memodel.publish(TOKEN)
