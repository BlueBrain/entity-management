'''Simulation domain entities'''

from typing import List, Union

import entity_management.morphology as morphology
from entity_management.base import (Distribution, Identifiable, attributes, Frozen,
                                    OntologyTerm, QuantitativeValue)
from entity_management.core import (Entity as CoreEntity, Activity, Agent, ProvenanceMixin,
                                    SoftwareAgent)
from entity_management.electrophysiology import Trace
from entity_management.mixins import DistributionMixin
from entity_management.util import AttrOf


@attributes({
    'name': AttrOf(str),
    'description': AttrOf(str, default=None),
})
class Entity(ProvenanceMixin, DistributionMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name(str): Required entity name which can later be used for retrieval.
        description(str): Short description of the entity.
        wasDerivedFrom(List[Identifiable]): List of associated provenance entities.
    '''
    _url_version = 'v1.0.0'


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
    _url_version = 'v0.1.2'


@attributes({'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelRelease(Entity):
    '''Release base entity'''
    _url_version = 'v0.1.3'


@attributes()
class ModelScript(Entity):
    '''Base entity for the scripts attached to the model.'''
    _url_version = 'v0.1.1'


@attributes()
class ModelReleaseIndex(Entity):
    '''Index files attached to release entities'''
    _url_version = 'v0.1.2'


@attributes({'distribution': AttrOf(List[Distribution]),
             'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class MorphologyRelease(ModelRelease):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    Args:
        distribution(List[Distribution]): If morphology release is provided at the external
            location distribution should provide the path to locate it. It should contain

            * ``v1`` folder with morphologies in H5v1 format
            * ``ascii`` folder with morphologies in ASC format
            * ``annotations`` folder with morphology annotations used for placement

        morphologyIndex(ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''
    _url_version = 'v0.1.2'


@attributes()
class IonChannelMechanismRelease(ModelRelease):
    '''Ion channel models release represents a collection of mod files.
    '''
    _url_version = 'v0.1.3'


@attributes({'distribution': AttrOf(List[Distribution])})
class SynapseRelease(ModelRelease):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(List[Distribution]): Location of the synapse release/mod files.
    '''
    _url_version = 'v0.1.1'


@attributes()
class Configuration(Entity):
    '''Configuration file'''
    _url_version = 'v0.1.1'


@attributes({'used': AttrOf(List[Configuration])})
class MorphologyDiversification(Activity):
    '''Morphology release building activity.

    Args:
        used(List[Identifiable]): Configurations(neurondb.xml, placement_rules.xml) which were used
            to generate the emodel.
    '''
    _url_version = 'v0.1.4'
    _url_domain = 'simulation'  # need to override as Activity will set it to 'core'


@attributes({
    'distribution': AttrOf(List[Distribution], default=None),
    'emodelIndex': AttrOf(ModelReleaseIndex, default=None),
    'isPartOf': AttrOf(Identifiable, default=None)
})
class EModelRelease(ModelRelease):
    '''Electrical model release

    Args:
        distribution (List[Distribution]): EModel release location provides a path to ``hoc`` files.
        emodelIndex (ModelReleaseIndex): EModel release index file.
        isPartOf (Identifiable): Dataset this release is part of.
    '''
    _url_version = 'v0.1.3'


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
    _url_version = 'v0.1.2'


@attributes({'distribution': AttrOf(List[Distribution], default=None),
             'mType': AttrOf(OntologyTerm, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None),
             'view2d': AttrOf(Identifiable, default=None),
             'view3d': AttrOf(Identifiable, default=None)})
class Morphology(ModelInstance):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution(List[Distribution]): If morphology is stored at the external location
            distribution should provide the path to it.
        mType(OntologyTerm): Morphological cell type.
        isPartOf(MorphologyRelease): Release this morphology is part of.
        view2d(Identifiable): Morphology view in 2D.
        view3d(Identifiable): Morphology view in 3D.
    '''
    _url_version = 'v0.1.4'


@attributes()
class SubCellularModelScript(ModelScript):
    '''Scripts attached to the model: ``mod`` file.

    Args:
        distribution(List[Distribution]): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    _url_version = 'v0.1.1'


@attributes()
class EModelScript(ModelScript):
    '''Scripts attached to the model: ``hoc``, ``neuroml`` file.

    Args:
        distribution(List[Distribution]): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''
    _url_version = 'v0.1.1'


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
    _url_version = 'v0.1.3'


@attributes({
    'subCellularMechanism': AttrOf(List[SubCellularModel], default=None),
    'modelScript': AttrOf(List[EModelScript], default=None),
    'isPartOf': AttrOf(EModelRelease, default=None),
})
class EModel(ModelInstance):
    '''Electrical model

    Args:
        subCellularMechanism(List[SubCellularModel]): SubCellular mechanism collection.
        modelScript(List[EModelScript]): Model script collection. Scripts defining neuron model,
            e.g. a ``hoc`` files.
        isPartOf (EModelRelease): EModel release this emodel is part of.
    '''
    _url_version = 'v0.1.2'


@attributes({'used': AttrOf(morphology.ReconstructedCell),
             'generated': AttrOf(EModel, default=None),
             'wasAssociatedWith': AttrOf(List[Union[Agent, SoftwareAgent]], default=None),
             'bestScore': AttrOf(QuantitativeValue, default=None)})
class EModelBuilding(Activity):
    '''EModel building activity.

    Args:
        bestScore(QuantitativeValue): Best score.
        used(morphology.ReconstructedCell): Morphology which was used to generate the emodel.
        generated(EModel): EModel which was produced.
        wasAssociatedWith(List[SoftwareAgent]): Agents associated with
            this activity.
    '''
    _url_version = 'v0.1.4'
    _url_domain = 'simulation'  # need to override as Activity will set it to 'core'


@attributes()
class SingleCellSimulationTrace(Entity):
    '''Single cell simulation trace file'''
    _url_version = 'v0.1.4'


@attributes({'hadMember': AttrOf(List[Trace], default=None)})
class TraceCollection(Entity):
    '''Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    '''
    _url_version = 'v0.1.2'
    _type_name = 'Collection'


@attributes({'hadMember': AttrOf(List[Trace], default=None)})
class CoreTraceCollection(Entity):
    '''Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    '''
    _url_domain = 'core'
    _url_name = 'tracecollection'
    _url_version = 'v0.1.0'
    _type_name = 'TraceCollection'


@attributes({'name': AttrOf(str),
             'channel': AttrOf(int),
             'description': AttrOf(str, default=None)})
class ExperimentalCell(Frozen):
    '''Experimental cell.

    Args:
        name(str): TODO.
        channel(int): TODO.
        description(str): TODO.
    '''
    pass


@attributes({'features': AttrOf(CoreEntity),
             'hadProtocol': AttrOf(CoreEntity),
             'hypampThreshold': AttrOf(CoreEntity, default=None)})
class BluePyEfeFeatures(Entity):
    '''BluePyEfe configuration entity'''
    _url_version = 'v0.1.3'


@attributes({'brainRegion': AttrOf(OntologyTerm),
             'species': AttrOf(OntologyTerm),
             'mType': AttrOf(OntologyTerm),
             'experimentalCell': AttrOf(List[ExperimentalCell]),
             'featureExtractionConfiguration': AttrOf(dict),
             'stimuliToExperimentMap': AttrOf(dict, default=None),
             'masterListConfiguration': AttrOf(CoreEntity, default=None)})
class BluePyEfeConfiguration(Entity):
    '''BluePyEfe configuration entity'''
    _url_version = 'v0.1.4'
    _type_name = 'Configuration'


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
    _url_version = 'v0.1.3'


@attributes({'distribution': AttrOf(List[Distribution])})
class CircuitCellProperties(Entity):
    '''Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution(List[Distribution]): Location of the cell placement file.
    '''
    _url_version = 'v0.1.1'


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'circuitCellProperties': AttrOf(CircuitCellProperties)})
class NodeCollection(Entity):
    '''Node collection represents circuit nodes(positions, orientations)

    Args:
        memodelRelease(MEModelRelease): MEModel release this node collection is using.
        circuitCellProperties(CircuitCellProperties): Cell properties which are used in this node
                                                      collection.
    '''
    _url_version = 'v0.1.2'


@attributes({'edgePopulation': AttrOf(CoreEntity),
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)

    Args:
        edgePopulation(core.Entity): Distribution providing path to the collection of nrn
            files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    '''
    _url_version = 'v0.1.2'


@attributes({'distribution': AttrOf(List[Distribution])})
class Target(Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution(List[Distribution]): Location of the target file.
    '''
    _url_version = 'v0.1.1'


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
    _url_version = 'v0.1.2'


@attributes({'gitHash': AttrOf(str),
             'inputMechanisms': AttrOf(IonChannelMechanismRelease),
             'bluePyOptParameters': AttrOf(Configuration, default=None),
             'bluePyOptProtocol': AttrOf(Configuration, default=None),
             'bluePyOptRecipe': AttrOf(Configuration, default=None),
             'experimentalFeatures': AttrOf(BluePyEfeFeatures, default=None),
             'morphology': AttrOf(morphology.Entity, default=None),
             'hasOutput': AttrOf(EModelRelease, default=None)})
class BluePyOptRun(Entity):
    '''Release base entity'''
    _url_version = 'v0.1.12'


@attributes()
class ETypeFeatureProtocol(Entity):
    '''Trace protocol.'''
    _url_version = 'v0.1.2'


@attributes()
class TraceFeature(Entity):
    '''Trace feature.'''
    _url_version = 'v0.1.1'


@attributes()
class Threshold(Entity):
    '''Threshold.'''
    _url_version = 'v0.1.2'


@attributes({'activity': AttrOf(Activity)})
class EModelGenerationShape(Entity):
    '''EModel generation.'''
    _url_version = 'v0.1.1'
    _type_name = 'TraceGeneration'


@attributes({
    'used': AttrOf(List[Union[CoreTraceCollection, BluePyEfeConfiguration]]),
    'generated': AttrOf(BluePyEfeFeatures, default=None),
})
class TraceFeatureExtraction(Activity):
    '''Trace feature extraction activity.

    Args:
        used (List[Union[CoreTraceCollection, BluePyEfeConfiguration]]): Used resources.
        generated (BluePyEfeFeatures): Extracted features.
    '''
    _url_version = 'v0.1.2'
    _url_domain = 'simulation'  # need to override as Activity will set it to 'core'
