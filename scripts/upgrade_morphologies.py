#!/usr/bin/env python
'''Update morphologies to have 2d/3d previews and belong to morphology release

Loop through all the morphologies, deprecate the old one, create the new morphologies
with previews and update the links to this new morphology.
'''
import os
import requests
import sh

from tempfile import NamedTemporaryFile

from neurom import viewer, load_neuron
from neurom.view import common
from neurom.exceptions import NeuroMError

from entity_management.base import OntologyTerm
from entity_management.core import Entity
from entity_management.simulation import (Morphology, MorphologyRelease)

TOKEN = os.getenv('NEXUS_TOKEN')

HIPPOCAMPUS = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                           label='field CA1 of the hippocampus')
RAT = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116', label='Rattus norvegicus')

CORTEX = OntologyTerm(url='http://api.brain-map.org/api/v2/data/Structure/322',
                      label='Primary somatosensory area')
MOUSE = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10088', label='Mouse')

RAT_RELEASE = next(MorphologyRelease.find_by(name='Rat hippocampus morphology release',
                                             use_auth=TOKEN))
MOUSE_RELEASE = next(MorphologyRelease.find_by(
    name='Mouse primary somatosensory area morphology release', use_auth=TOKEN))


def make_view2d(file_location):
    '''Make morphology preview in 2d'''
    try:
        morph_tmp = NamedTemporaryFile()
        nrn = load_neuron(file_location)
        fig, ax = viewer.draw(nrn, mode='2d')
        ax.set_title('')
        ax.set_xlabel('x $\\mu$m')
        ax.set_ylabel('y $\\mu$m')
        fig.savefig(morph_tmp.name, dpi=300, bbox_inches='tight', format='png')
        common.plt.close()

        view2d = Entity(name='view2d')
        view2d = view2d.publish(use_auth=TOKEN)
        with open(morph_tmp.name) as f:
            view2d.attach('view2d.png', f, 'image/png', TOKEN) # pylint: disable=maybe-no-member
        return view2d
    except (AssertionError, NeuroMError):
        print(file_location, 'IGNORING!')


def make_view3d(file_location):
    '''Make morphology preview in 3d'''
    try:
        morph_tmp = NamedTemporaryFile()
        morph_viewer = sh.Command('morphology_viewer.py')
        morph_viewer(file_location, no_pick=True, inline=morph_tmp.name, _fg=True)

        view3d = Entity(name='view3d')
        view3d = view3d.publish(use_auth=TOKEN)
        with open(morph_tmp.name) as f:
            view3d.attach('view3d.html', f, 'text/html', TOKEN) # pylint: disable=maybe-no-member
        return view3d
    except sh.ErrorReturnCode:
        pass


def upgrade_morphology(name, file_name, file_location, brain_region, species, morpho_release):
    '''Upgrade morphology with 2d/3d views and MorphologyRelease'''
    view2d = make_view2d(file_location)
    view3d = make_view3d(file_location)

    # find old morphology
    response = requests.get(
            'https://nexus-int.humanbrainproject.org/v0/data/brainsimulation/'
            'simulation/morphology/v0.1.1',
            params={
                'deprecated': 'false',
                'fields': 'all',
                'filter': '{"op":"eq","path":"schema:name","value":"%s"}' % name},
            headers={'accept': 'application/ld+json', 'authorization': TOKEN})

    if len(response.json()['results']) == 0:
        return

    morph_id = response.json()['results'][0]['resultId']
    morph_rev = response.json()['results'][0]['source']['nxv:rev']

    # create new version of the morphology
    morphology = Morphology(name=name, brainRegion=brain_region, species=species,
                            view2d=view2d, view3d=view3d, isPartOf=morpho_release)
    morphology = morphology.publish(use_auth=TOKEN)
    with open(file_location) as f:
        # pylint: disable=maybe-no-member
        morphology.attach(file_name, f, 'application/neurolucida', TOKEN)

    # update all incoming connection to the old morphology to point to the new morphology
    response = requests.get(morph_id + '/incoming',
                            params={'fields': 'all'},
                            headers={'accept': 'application/ld+json', 'authorization': TOKEN})

    for result in response.json()['results']:
        data = result['source']
        if 'morphology' in data:
            # pylint: disable=maybe-no-member
            data['morphology']['@id'] = morphology.id
        elif 'used' in data:
            # pylint: disable=maybe-no-member
            data['used']['@id'] = morphology.id
        response = requests.put(result['resultId'],
                                headers={'accept': 'application/ld+json',
                                         'authorization': TOKEN},
                                params={'rev': data['nxv:rev']},
                                json=data)
        response.raise_for_status()

    # deprecate old morphology
    response = requests.delete(morph_id,
                               headers={'accept': 'application/ld+json', 'authorization': TOKEN},
                               params={'rev': morph_rev})
    response.raise_for_status()


models_dir = 'scripts/models'
for model_name in os.listdir(models_dir):
    model_dir = '%s/%s' % (models_dir, model_name)
    if os.path.isdir(model_dir):
        morphology_name = os.listdir('%s/morphology' % model_dir)[0]
        morphology_file = '%s/morphology/%s' % (model_dir, morphology_name)
        assert os.path.isfile(morphology_file)

        upgrade_morphology(model_name, morphology_name, morphology_file,
                           HIPPOCAMPUS, RAT, RAT_RELEASE)

models_dir = 'scripts/memodel_dirs'
for model_dir, dirs, files in os.walk(models_dir):
    if 'mechanisms' in dirs and 'morphology' in dirs:
        model_name = os.path.basename(model_dir)

        morphology_name = os.listdir('%s/morphology' % model_dir)[0]
        morphology_file = '%s/morphology/%s' % (model_dir, morphology_name)
        assert os.path.isfile(morphology_file)
        upgrade_morphology(model_name, morphology_name, morphology_file,
                           CORTEX, MOUSE, MOUSE_RELEASE)
