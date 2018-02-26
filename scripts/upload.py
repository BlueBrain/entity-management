#!/usr/bin/env python
'''Upload data to nexus'''

from pprint import pprint

from entity_management.base import Distribution
from entity_management.simulation.cell import MorphologyRelease


morphology_release = MorphologyRelease.from_name('2012 Morphology release')
if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name='2012 Morphology release',
        description='Morphology release used for the O1.V5 microcircuit',
        distribution=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531',
            mediaType='application/swc,'
                      'application/neurolucida,'
                      'application/h5,'
                      'application/neuroml'),
        morphologyIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/release/l2/2012.07.23/morphologies/'
                        'morphology_release/release_20120531/neuronDB.dat',
            mediaType='application/mvd3'))

    morphology_release.save()
    pprint('MorphologyRelease created: 2012 Morphology release')


morphology_release = MorphologyRelease.from_name('2017 Morphology release')
if morphology_release is None:
    pprint('MorphologyRelease creating...')
    morphology_release = MorphologyRelease(
        name='2017 Morphology release',
        description='Morphology release used for the O1.V6 and S1.V6',
        distribution=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/proj59/entities/morphologies/'
                        '2017.10.31',
            mediaType='application/swc,'
                      'application/neurolucida,'
                      'application/h5,'
                      'application/neuroml'),
        morphologyIndex=Distribution(
            downloadURL='file:///gpfs/bbp.cscs.ch/project/'
                        'proj59/entities/morphologies/2017.10.31/neurondb.dat',
            mediaType='application/mvd3'))
    morphology_release.save()
    pprint('MorphologyRelease created: 2017 Morphology release')
