'''Simulation domain entities'''

from typing import List, Union

from entity_management.base import Distribution, Identifiable, OntologyTerm, QuantitativeValue
from entity_management.core import Activity, Agent, SoftwareAgent
from entity_management.mixins import DistributionMixin
from entity_management.util import attributes, AttrOf


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
    })
class Entity(DistributionMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
    '''
    _type_namespace = 'nsg'

    def __attrs_post_init__(self):
        super(Entity, self).__attrs_post_init__()
        self._type.append('prov:Entity')


@attributes({'modelOf': AttrOf(str, default=None),
             'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelInstance(Entity):
    '''Abstract model instance.

    Args:
        modelOf(str): Specifies the model.
        brainRegion(OntologyTerm): Brain region ontology term.
        species(OntologyTerm): Species ontology term.
    '''
    pass


@attributes({'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelRelease(Entity):
    '''Release base entity'''
    _url_version = 'v0.1.1'


@attributes()
class ModelScript(Entity):
    '''Base entity for the scripts attached to the model.'''
    pass


@attributes()
class ModelReleaseIndex(Entity):
    '''Index files attached to release entities'''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution),
             'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class MorphologyRelease(ModelRelease):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    Args:
        distribution(Distribution): If morphology release is provided at the external
            location distribution should provide the path to locate it. It should contain

            * ``v1`` folder with morphologies in H5v1 format
            * ``ascii`` folder with morphologies in ASC format
            * ``annotations`` folder with morphology annotations used for placement

        morphologyIndex(ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''
    _url_version = 'v0.1.1'


@attributes()
class IonChannelMechanismRelease(ModelRelease):
    '''Ion channel models release represents a collection of mod files.
    '''
    _url_version = 'v0.1.2'


@attributes({'distribution': AttrOf(Distribution)})
class SynapseRelease(ModelRelease):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(Distribution): Location of the synapse release/mod files.
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution),
             'emodelIndex': AttrOf(ModelReleaseIndex)})
class EModelRelease(ModelRelease):
    '''Electrical model release

    Args:
        distribution(Distribution): EModel release location provides a path to ``hoc`` files.
        emodelIndex(ModelReleaseIndex): EModel release index file.
    '''
    _url_version = 'v0.1.1'


@attributes({'emodelRelease': AttrOf(EModelRelease),
             'morphologyRelease': AttrOf(MorphologyRelease),
             'memodelIndex': AttrOf(ModelReleaseIndex, default=None)})
class MEModelRelease(ModelRelease):
    '''MorphoElectrical model release

    Args:
        emodelRelease(EModelRelease): electrical model release
        morphologyRelease(MorphologyRelease): morphology model release
        memodelIndex(ModelReleaseIndex): optional morpho-electrical model index
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None),
             'view2d': AttrOf(Entity, default=None),
             'view3d': AttrOf(Entity, default=None)})
class Morphology(ModelInstance):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution(Distribution): If morphology is stored at the external location distribution
            should provide the path to it.
        isPartOf(MorphologyRelease): Release this morphology is part of.
        view2d(Entity): Morphology view in 2D.
        view3d(Entity): Morphology view in 3D.
    '''
    _url_version = 'v0.1.2'


@attributes()
class SubCellularModelScript(ModelScript):
    '''Scripts attached to the model: ``mod`` file.

    Args:
        distribution(Distribution): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    pass


@attributes()
class EModelScript(ModelScript):
    '''Scripts attached to the model: ``hoc``, ``neuroml`` file.

    Args:
        distribution(Distribution): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    pass


@attributes({'modelScript': AttrOf(SubCellularModelScript),
             'isPartOf': AttrOf(List[Union[IonChannelMechanismRelease, SynapseRelease]],
                                default=None)})
class SubCellularModel(ModelInstance):
    '''SubCellular model

    Args:
        modelScript(SubCellularModelScript): SubCellular model script such as mod file
        isPartOf(List[Union[IonChannelMechanismRelease, SynapseRelease]]): Optional list of synapse
            releases or ion channel releases this model is part of.
    '''
    _url_version = 'v0.1.2'


@attributes({'subCellularMechanism': AttrOf(List[SubCellularModel], default=None),
             'modelScript': AttrOf(List[EModelScript], default=None)})
class EModel(ModelInstance):
    '''Electrical model

    Args:
        subCellularMechanism(List[SubCellularModel]): SubCellular mechanism collection.
        modelScript(List[EModelScript]): Model script collection. Scripts defining neuron model,
            e.g. a ``hoc`` files.
    '''
    _url_version = 'v0.1.1'


@attributes({
    'used': AttrOf(Morphology),
    'generated': AttrOf(EModel),
    'wasAssociatedWith': AttrOf(List[Union[Agent, SoftwareAgent]]),
    'bestScore': AttrOf(QuantitativeValue, default=None)
    })
class EModelBuilding(Activity):
    '''EModel building activity.

    Args:
        bestScore(QuantitativeValue): Best score.
        used(Morphology): Morphology which was used to generate the emodel.
        generated(EModel): EModel which was produced.
        wasAssociatedWith(List[Union[Agent, SoftwareAgent]]): Agents associated with
            this activity.
    '''
    _url_version = 'v0.1.2'


@attributes()
class SingleCellSimulationTrace(Entity):
    '''Single cell simulation trace file'''
    _url_version = 'v0.1.2'


@attributes({'experimentalCellList': AttrOf(str),
             'masterListConfiguration': AttrOf(str),
             'experimentalTraceLocation': AttrOf(str)})
class BluePyEfeConfiguration(Entity):
    '''BluePyEfe configuration entity'''
    _url_version = 'v0.1.2'


@attributes({'eModel': AttrOf(EModel),
             'morphology': AttrOf(Morphology),
             'mainModelScript': AttrOf(EModelScript)})
class MEModel(ModelInstance):
    '''Detailed Neuron model with morphology and electrical models.

    Args:
        eModel(EModel): Electrical model.
        morphology(Morphology): Neuron morphology.
        mainModelScript(EModelScript): Model script which instantiates neuron with specified
            morphology and electrical model. Expected to have single NEURON template with the
            first argument being the folder where neuron morphology is located. Template is
            responsible for loading that morphology from the folder specified in the first
            template argument.
    '''
    _url_version = 'v0.1.2'


@attributes({'distribution': AttrOf(Distribution)})
class CircuitCellProperties(Entity):
    '''Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution(Distribution): Location of the cell placement file.
    '''
    pass


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'circuitCellProperties': AttrOf(CircuitCellProperties)})
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)

    Args:
        memodelRelease(MEModelRelease): MEModel release this node collection is using.
        circuitCellProperties(CircuitCellProperties): Cell properties which are used in this node
                                                      collection.
    '''
    _url_version = 'v0.1.1'


@attributes({'edgePopulation': AttrOf(ModelReleaseIndex), # FIXME make it work for now, check schema
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)

    Args:
        edgePopulation(Distribution): Distribution providing path to the collection of nrn
            files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    '''
    _url_version = 'v0.1.1'


@attributes({'distribution': AttrOf(Distribution)})
class Target(Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution(Distribution): Location of the target file.
    '''
    pass


@attributes({'nodeCollection': AttrOf(NodeCollection),
             'edgeCollection': AttrOf(EdgeCollection),
             'target': AttrOf(Target, default=None)})
class DetailedCircuit(ModelInstance):
    '''Detailed circuit

    Args:
        nodeCollection(NodeCollection): Node collection.
        edgeCollection(EdgeCollection): Edge collection.
        target(Target): Target.
    '''
    _url_version = 'v0.1.1'