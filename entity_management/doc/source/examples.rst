*************
Code examples
*************

.. contents::


TOKEN is the OAuth2 optional authorization token. Provide it in case the endpoint you are trying
to access has restricted access.

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


Synapse release
***************

Prepare the mod file release object(:class:`SynapseRelease<entity_management.simulation.cell.SynapseRelease>`):

.. code-block:: python

    from entity_management.simulation.cell import SynapseRelease

    synapse_release = SynapseRelease(name='Release', brainRegion=BRAIN_REGION, species=SPECIES)
    synapse_release = synapse_release.save(TOKEN)


Channel mechanisms
******************

Create and upload the mod file which is part of synapse release:

.. code-block:: python

    from entity_management.simulation.cell import SubCellularModelScript, SubCellularModel,

    mechanisms = []
    model_script = SubCellularModelScript(name='Script name', description='Some description')
    model_script = model_script.save(TOKEN)
    with open('cacumm.mod') as f:
        model_script.attach('cacumm.mod', f, 'application/neuron-mod', TOKEN)
    model = SubCellularModel(name='cacumm',
                             isPartOf=synapse_release,
                             modelScript=model_script,
                             brainRegion=BRAIN_REGION,
                             species=SPECIES)
    model = model.save(TOKEN)
    mechanisms.append(model)


Cell hoc script
***************

Create :class:`emodel script <entity_management.simulation.cell.EModelScript>` entity with attached hoc file:

.. code-block:: python

    from entity_management.simulation.cell import EModelScript

    emodel_script = EModelScript(name='Cell hoc model script')
    emodel_script = emodel_script.save(TOKEN)
    with open(hoc_file) as f:
        emodel_script.attach('cell.hoc', f, 'application/neuron-hoc', TOKEN)


Neuron morphology
*****************

Create :class:`morphology <entity_management.simulation.cell.Morphology>` with the attached morphology file content:

.. code-block:: python

    from entity_management.simulation.cell import Morphology

    morphology = Morphology(name='Morphology name',
                            description='Morphology description',
                            brainRegion=BRAIN_REGION,
                            species=SPECIES)
    morphology = morphology.save(TOKEN)
    with open('/path/to/morphology.asc') as f:
        morphology.attach('morphology.asc', f, 'application/neurolucida', TOKEN)


Cell emodel
***********

Create :class:`emodel <entity_management.simulation.cell.EModel>` with required set of subcellular mechanisms:

.. code-block:: python

    from entity_management.simulation.cell import EModel

    emodel = EModel(name='Model name',
                    subCellularMechanism=mechanisms,
                    brainRegion=BRAIN_REGION,
                    species=SPECIES)
    emodel = emodel.save(TOKEN)


Cell memodel
************

Create :class:`single cell model <entity_management.simulation.cell.MEModel>` with linked emodel, morphology
and model instantiation hoc script:

.. code-block:: python

    from entity_management.simulation.cell import EModel

    memodel = MEModel(name='Model name',
                      description='Model description',
                      eModel=emodel,
                      morphology=morphology,
                      modelScript=emodel_script,
                      brainRegion=BRAIN_REGION,
                      species=SPECIES)
    memodel = memodel.save(TOKEN)


Quering entities
################

Retrieve entity by UUID
***********************

.. code-block:: python

    from entity_management.simulation.cell import MEModel

    memodel = MEModel.from_uuid('546ffb86-370e-4e6b-9e4f-20e7d3e979d0', TOKEN)


Retrieve entity by Name
***********************

.. code-block:: python

    from entity_management.simulation.cell import MEModel

    memodel = MEModel.from_name('Model name', TOKEN)


Retrieve memodel by name and save in a folder
*********************************************

The code below will save single cell model represented by
:class:`MEModel <entity_management.simulation.cell.MEModel>` in the ``model_dir`` folder:

.. code-block:: python

    from entity_management.simulation.cell import MEModel

    model_dir = 'model_dir'
    os.makedirs(model_dir)

    memodel = MEModel.from_name('Model name', TOKEN)
    if memodel is not None:
        memodel.modelScript.download(model_dir, TOKEN)
        memodel.morphology.download(model_dir, TOKEN)
        [s.modelScript.download(model_dir, TOKEN) for s in memodel.eModel.subCellularMechanism]
