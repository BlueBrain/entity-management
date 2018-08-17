#!/usr/bin/env python

# prepare emname to morph(morphs.json)
# jq '. as $in | keys[] | {(.): $in[.].morph_path}' final.json > morphs.json

# prepare emname to traces(traces.json)
# jq '.[][]|{(.emname): [.features[][][][][]?[]?|.i_file?,.v_file?]|unique}' features_collection.json > traces.json

# prepare emname to hoc(hocs.json)
# jq 'keys[]+".hoc"' morphs.json | xargs -I % find /gpfs/bbp.cscs.ch/project/proj64/home/vangeit/memodel_packages/draft1/memodel_dirs -type f -name % -print -quit
# addidional location for missing emodels: /gpfs/bbp.cscs.ch/project/proj64/home/vangeit/memodel_packages/draft1_morezips


import os
import json
from pprint import pprint
from os.path import dirname, splitext, basename
from tempfile import TemporaryDirectory
from itertools import zip_longest

import sys
assert sys.version_info >= (3, 6)

from entity_management.core import Person, SoftwareAgent
from entity_management.base import OntologyTerm, Distribution
from entity_management.morphology import ReconstructedCell
from entity_management.electrophysiology import Trace
from entity_management.simulation import (SubCellularModelScript, SubCellularModel, EModelBuilding,
                                          EModelScript, EModel, Morphology, TraceCollection,
                                          IonChannelMechanismRelease)

SSC = OntologyTerm(url='http://api.brain-map.org/api/v2/data/Structure/322',
                   label='Primary somatosensory area')
RAT = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116',
                   label='Rattus norvegicus')


def grouper(iterable, n, fillvalue=None):
    'Collect data into fixed-length chunks or blocks'
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def main():
    cur_dir = dirname(__file__)
    with open(f'{cur_dir}/data/morphs.json') as f: # pylint: disable=invalid syntax
        morphs = json.load(f)

    with open(f'{cur_dir}/data/traces.json') as f:
        traces = json.load(f)

    with open(f'{cur_dir}/data/hocs.json') as f:
        hocs = json.load(f)

    email = 'christian.rossert@epfl.ch'

    person = next(Person.find_by(email=email), None)
    if person is None:
        person = Person(email=email,
                        givenName='Christian',
                        familyName='Rossert')
        person = person.publish()
    print(person)

    blue_py_opt = 'BluePyOpt'
    blue_py_opt_version = '1'
    blue_py_opt_agent = next(SoftwareAgent.find_by(name=blue_py_opt, version=blue_py_opt_version),
                             None)
    if blue_py_opt_agent is None:
        blue_py_opt_agent = SoftwareAgent(name=blue_py_opt, version=blue_py_opt_version)
        blue_py_opt_agent = blue_py_opt_agent.publish()
    print(blue_py_opt_agent)

    name = 'Rat SSCx ion channel mechanism release'
    mod_release = next(IonChannelMechanismRelease.find_by(name=name), None)
    if mod_release is None:
        mod_release = IonChannelMechanismRelease(name=name, brainRegion=SSC, species=RAT)
        mod_release = mod_release.publish(person=person)
    print(mod_release)

    sub_cellular_models = {}
    take_first_location = lambda dict_: next(iter(dict_.items()))[1]
    emodel_location = dirname(take_first_location(hocs))
    mod_files = f'{emodel_location}/mechanisms'
    for mod_name in os.listdir(mod_files):
        mod_file = f'{mod_files}/{mod_name}'
        assert os.path.isfile(mod_file)
        name, ext = splitext(mod_name)
        if ext != '.mod':
            continue
        print(mod_file)
        model = next(SubCellularModel.find_by(name=name), None)
        if model is None:
            print('Creating mod: %s' % name)
            model_script = next(SubCellularModelScript.find_by(name=name), None)
            if model_script is None:
                model_script = SubCellularModelScript(name=name)
                model_script = model_script.publish(person=person)
                with open(mod_file) as f:
                    # pylint: disable=maybe-no-member
                    model_script.attach(mod_name, f, 'application/neuron-mod')
            model = SubCellularModel(name=name,
                                     isPartOf=[mod_release],
                                     modelScript=model_script,
                                     brainRegion=SSC,
                                     species=RAT)
            model = model.publish(person=person)
        sub_cellular_models[name] = model

    for emname in morphs.keys():
        print(emname)
        emodel = next(EModel.find_by(name=emname), None)
        if emodel is None:
            emodel_script = EModelScript(name=emname)
            emodel_script = emodel_script.publish(person=person)

            hoc_file = hocs[emname]
            with open(hoc_file) as f:
                # pylint: disable=maybe-no-member
                emodel_script.attach(basename(hoc_file), f, 'application/neuron-hoc')

            file_name = morphs[emname]
            cell = next(ReconstructedCell.find_by(originalFileName=file_name))

            with TemporaryDirectory() as tmp_path:
                cell.download(tmp_path)
                morphology = Morphology(splitext(file_name)[0])
                morphology = morphology.publish(person=person)
                with open(f'{tmp_path}/{file_name}') as f:
                    # pylint: disable=maybe-no-member
                    morphology.attach(file_name, f, 'application/neurolucida')

            trace_collection = next(TraceCollection.find_by(name=f'{emname} traces'), None)
            if trace_collection is None:
                batch_size = 50
                trace_list = []
                for trace_batch in grouper(traces[emname], batch_size):
                    trace_iterator = Trace.find_by(all_organizations=True,
                                                   name=('in', list(trace_batch)))
                    trace_iterator.page_size = batch_size
                    trace_list.extend(trace_iterator)
                    print(len(trace_list))

                trace_collection = TraceCollection(name=f'{emname} traces', hadMember=trace_list)
                trace_collection = trace_collection.publish(person=person)

            emodel_building = EModelBuilding(used=morphology,
                                             wasAssociatedWith=[blue_py_opt_agent])
            mechanisms = [sub_cellular_models[splitext(m)[0]]
                          for m in os.listdir('{}/mechanisms'.format(dirname(hocs[emname])))
                          if m.endswith('.mod')]

            emodel = EModel(name=emname,
                            modelScript=[emodel_script],
                            subCellularMechanism=mechanisms,
                            brainRegion=SSC,
                            species=RAT,
                            wasDerivedFrom=[cell, trace_collection])
            emodel = emodel.publish(activity=emodel_building, person=person)


if __name__ == '__main__':
    main()
