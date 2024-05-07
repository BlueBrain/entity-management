*************
Code examples
*************

.. contents::


TOKEN is the OAuth2 optional access token. Provide it in case the endpoint has OAuth2 protected
access control. If token is available in the environment variable `NEXUS_TOKEN` it will be used
by default unless it was explicitly provided in the method argument.

Creating entities
#################

Ontology terms
**************

Create brain region and species :class:`ontology terms<entity_management.base.OntologyTerm>`:

.. code-block:: python

    from entity_management.base import OntologyTerm

    BRAIN_REGION = OntologyTerm(url='http://uri.interlex.org/paxinos/uris/rat/labels/322',
                                label='field CA1 of the hippocampus')

    SPECIES = OntologyTerm(url='http://purl.obolibrary.org/obo/NCBITaxon_10116',
                           label='Rattus norvegicus')


IonChannelMechanismRelease
**************************

Prepare the mod file release object(:class:`IonChannelMechanismRelease<entity_management.simulation.IonChannelMechanismRelease>`):

.. code-block:: python

    from entity_management.simulation import IonChannelMechanismRelease

    mod_release = IonChannelMechanismRelease(name='Release', brainRegion=BRAIN_REGION, species=SPECIES)
    mod_release = mod_release.publish(use_auth=TOKEN)


Channel mechanisms
******************

Create and upload the mod file which is part of ion channel mechanism(mod_release) or synapse release:

.. code-block:: python

    from entity_management.core import DataDownload
    from entity_management.simulation import SubCellularModelScript, SubCellularModel,

    mechanisms = []
    model_script = SubCellularModelScript(
        name='Script name',
        description='Some description'
        distribution=DataDownload.from_file(file_path='cacumm.mod',
                                            content_type='application/neuron-mod',
                                            use_auth=TOKEN))
    model_script = model_script.publish(use_auth=TOKEN)
    model = SubCellularModel(name='cacumm',
                             isPartOf=[mod_release],
                             modelScript=model_script,
                             brainRegion=BRAIN_REGION,
                             species=SPECIES)
    model = model.publish(use_auth=TOKEN)
    mechanisms.append(model)


Cell hoc script
***************

Create :class:`emodel script <entity_management.simulation.EModelScript>` entity with attached hoc file:

.. code-block:: python

    from entity_management.core import DataDownload
    from entity_management.simulation import EModelScript

    emodel_script = EModelScript(
        name='Cell hoc model script',
        distribution=DataDownload.from_file(file_path='cell.hoc',
                                            content_type='application/neuron-hoc',
                                            use_auth=TOKEN))
    emodel_script = emodel_script.publish(use_auth=TOKEN)


Neuron morphology
*****************

Create :class:`morphology <entity_management.simulation.Morphology>` with the attached morphology file content:

.. code-block:: python

    from entity_management.core import DataDownload
    from entity_management.simulation import Morphology

    morphology = Morphology(
        name='Morphology name',
        description='Morphology description',
        brainRegion=BRAIN_REGION,
        species=SPECIES,
        distribution=DataDownload.from_file(file_path='/path/to/morphology.asc',
                                            content_type='application/neurolucida',
                                            use_auth=TOKEN))
    morphology = morphology.publish(use_auth=TOKEN)


Cell emodel
***********

Create :class:`emodel <entity_management.simulation.EModel>` with required set of subcellular mechanisms:

.. code-block:: python

    from entity_management.simulation import EModel

    emodel = EModel(name='Model name',
                    subCellularMechanism=mechanisms,
                    brainRegion=BRAIN_REGION,
                    species=SPECIES)
    emodel = emodel.publish(use_auth=TOKEN)


Cell memodel
************

Create :class:`single cell model <entity_management.simulation.MEModel>` with linked emodel, morphology
and model instantiation hoc script:

.. code-block:: python

    from entity_management.simulation import EModel

    memodel = MEModel(name='Model name',
                      description='Model description',
                      eModel=emodel,
                      morphology=morphology,
                      modelScript=emodel_script,
                      brainRegion=BRAIN_REGION,
                      species=SPECIES)
    memodel = memodel.publish(use_auth=TOKEN)


Unconstrained json
******************

Upload raw json using :class:`Unconstrained<entity_management.base.Unconstrained>`:

.. code-block:: python

    from entity_management.base import Unconstrained

    obj = Unconstrained(json=dict(key1='value1', key2='value2'))
    obj = obj.publish(use_auth=TOKEN)
    # retrieve it back
    obj = Unconstrained.from_id(resource_id=obj._id)


Quering entities
################

Retrieve entity by ID
*********************

.. code-block:: python

    from entity_management.simulation import MEModel

    memodel = MEModel.from_id(resource_id='546ffb86-370e-4e6b-9e4f-20e7d3e979d0', use_auth=TOKEN)
