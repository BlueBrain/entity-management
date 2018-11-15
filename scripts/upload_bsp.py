#!/usr/bin/env python
'''Upload data to nexus
Prerequisites in scripts folder:
    (cd scripts && \
            git clone https://github.com/lbologna/bsp_data_repository.git && \
            git clone https://github.com/cnr-ibf-pa/hbp-bsp-models.git)
    (mkdir -p scripts/models && \
            cd scripts/bsp_data_repository && \
            find . -name '*.zip' \
            -exec unzip '{}' -x '*.pdf' -x '*.pkl' -x '*.json' -x '*.txt' -d ../models/ ';')
    cp -r /gpfs/bbp.cscs.ch/project/proj66/home/vangeit/src/NeuroMLExport/\
            cellmodels/SuppWebsite.mousify/output.20180316/memodel_dirs scripts/
'''
import os
import json

from entity_management.base import OntologyTerm, Distribution, BrainLocation, Identifiable
from entity_management.simulation import (SubCellularModelScript, SubCellularModel, EModelBuilding,
                                          EModelScript, EModel, IonChannelMechanismRelease)
from entity_management.morphology import ReconstructedCell


BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                            label='field CA1 of the hippocampus')
SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116',
                       label='Rattus norvegicus')


def publish(entity, attachment, name, content_type):
    '''Publish entity with attachment'''
    print('publish', type(entity), attachment)
    entity = entity.publish()
    assert entity
    with open(attachment) as file_:
        entity.attach(name, file_, content_type)
    return entity


def publish_emodel(emodel, morphology):
    '''Publish emodel'''
    print('publish_emodel', emodel.name, morphology.name)
    emodel_building = EModelBuilding(used=morphology)
    return emodel.publish(activity=emodel_building)


def main():
    '''main'''
    dataset = Identifiable(id='https://nexus-int.humanbrainproject.org/v0/data/mindseditor/'
                           'core/dataset/v0.0.4/1a5564c5-0446-40df-a8c0-a478cca100d2')
    print(dataset)

    # pylint: disable=maybe-no-member,missing-docstring,cell-var-from-loop
    mod_release = IonChannelMechanismRelease(
        name='Hippocampus ion channel mechanism release',
        distribution=[Distribution(
            downloadURL='https://github.com/cnr-ibf-pa/hbp-bsp-models/releases/tag/v1.0.1')],
        brainRegion=BRAIN_REGION,
        species=SPECIES)
    mod_release = IonChannelMechanismRelease.find_unique(
        name=mod_release.name,
        on_no_result=mod_release.publish)
    assert mod_release

    mod_files = 'scripts/hbp-bsp-models/mod_files'
    sub_cellular_models = {}
    for mod_name in os.listdir(mod_files):
        name, ext = os.path.splitext(mod_name)
        print(name)
        assert ext == '.mod'

        model_script = SubCellularModelScript(name=name)
        model_script = SubCellularModelScript.find_unique(
            name=name,
            on_no_result=lambda: publish(model_script,
                                         f'{mod_files}/{mod_name}',
                                         mod_name,
                                         'application/neuron-mod'))
        assert model_script

        model = SubCellularModel(
            name=name,
            isPartOf=[mod_release],
            modelScript=model_script,
            brainRegion=BRAIN_REGION,
            species=SPECIES)
        model = SubCellularModel.find_unique(name=name, on_no_result=model.publish)
        assert model
        sub_cellular_models[name] = model

    bsp_data_repository = 'scripts/bsp_data_repository/optimizations'
    models_dir = 'scripts/models'
    for model_name in os.listdir(models_dir):
        print(model_name)
        model_dir = f'{models_dir}/{model_name}'
        if os.path.isdir(model_dir):
            with open(f'{bsp_data_repository}/{model_name}/{model_name}_meta.json') as meta_f:
                meta_info = json.load(meta_f)
            best_cell = str(meta_info['best_cell'])

            morphology_name = os.listdir(f'{model_dir}/morphology')[0]
            morphology = ReconstructedCell(
                name=model_name,
                brainLocation=BrainLocation(brainRegion=BRAIN_REGION))
            morphology = ReconstructedCell.find_unique(
                name=morphology.name,
                on_no_result=lambda: publish(morphology,
                                             f'{model_dir}/morphology/{morphology_name}',
                                             morphology_name,
                                             'application/neurolucida'))
            assert morphology

            mechanisms = [sub_cellular_models[os.path.splitext(m)[0]]
                          for m in os.listdir(f'{model_dir}/mechanisms')]

            emodel_script = EModelScript(name=model_name)
            emodel_script = EModelScript.find_unique(
                name=emodel_script.name,
                on_no_result=lambda: publish(emodel_script,
                                             f'{model_dir}/checkpoints/{best_cell}',
                                             f'{model_name}.hoc',
                                             'application/neuron-hoc'))
            assert emodel_script

            emodel = EModel(name=model_name,
                            modelScript=[emodel_script],
                            subCellularMechanism=mechanisms,
                            brainRegion=BRAIN_REGION,
                            species=SPECIES)
            emodel = EModel.find_unique(
                name=emodel.name,
                on_no_result=lambda: publish_emodel(emodel, morphology))


if __name__ == '__main__':
    main()
