'''Simulation domain entities'''

from typing import List, Union

from attr.validators import in_

import entity_management.morphology as morphology
from entity_management.base import (Identifiable, attributes, Frozen, OntologyTerm,
                                    QuantitativeValue)
from entity_management.core import (Entity, Activity, Agent, ProvenanceMixin,
                                    SoftwareAgent, DataDownload)
from entity_management.electrophysiology import Trace
# from entity_management.atlas import CellAtlas
from entity_management.util import AttrOf


@attributes({
    'name': AttrOf(str, default=None),
    'description': AttrOf(str, default=None),
    'distribution': AttrOf(DataDownload, default=None),
})
class _Entity(ProvenanceMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name (str): Entity name.
        description (str): Short description of the entity.
        wasDerivedFrom (List[Identifiable]): List of associated provenance entities.
    '''


@attributes({'modelOf': AttrOf(str, default=None),
             'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelInstance(_Entity):
    '''Abstract model instance.

    Args:
        modelOf(str): Specifies the model.
        brainRegion(OntologyTerm): Brain region ontology term.
        species(OntologyTerm): Species ontology term.
    '''


@attributes({'brainRegion': AttrOf(OntologyTerm, default=None),
             'species': AttrOf(OntologyTerm, default=None)})
class ModelRelease(_Entity):
    '''Release base entity'''


@attributes()
class ModelScript(_Entity):
    '''Base entity for the scripts attached to the model.'''


@attributes()
class ModelReleaseIndex(_Entity):
    '''Index files attached to release entities'''


@attributes({'distribution': AttrOf(List[DataDownload]),
             'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class MorphologyRelease(ModelRelease):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    Args:
        distribution(List[DataDownload]): If morphology release is provided at the external
            location distribution should provide the path to locate it. It should contain

            * ``v1`` folder with morphologies in H5v1 format
            * ``ascii`` folder with morphologies in ASC format
            * ``annotations`` folder with morphology annotations used for placement

        morphologyIndex(ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''


@attributes()
class IonChannelMechanismRelease(ModelRelease):
    '''Ion channel models release represents a collection of mod files.
    '''


@attributes({'distribution': AttrOf(List[DataDownload])})
class SynapseRelease(ModelRelease):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(List[DataDownload]): Location of the synapse release/mod files.
    '''


@attributes()
class Configuration(_Entity):
    '''Configuration file'''


@attributes({'used': AttrOf(List[Configuration])})
class MorphologyDiversification(Activity):
    '''Morphology release building activity.

    Args:
        used(List[Identifiable]): Configurations(neurondb.xml, placement_rules.xml) which were used
            to generate the emodel.
    '''
    _url_domain = 'simulation'  # need to override as Activity will set it to 'core'


@attributes({
    'distribution': AttrOf(List[DataDownload], default=None),
    'emodelIndex': AttrOf(ModelReleaseIndex, default=None),
    'isPartOf': AttrOf(Identifiable, default=None)
})
class EModelRelease(ModelRelease):
    '''Electrical model release

    Args:
        distribution (List[DataDownload]): EModel release location provides a path to ``hoc`` files.
        emodelIndex (ModelReleaseIndex): EModel release index file.
        isPartOf (Identifiable): Dataset this release is part of.
    '''


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


@attributes({'distribution': AttrOf(List[DataDownload], default=None),
             'mType': AttrOf(OntologyTerm, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None),
             'view2d': AttrOf(Identifiable, default=None),
             'view3d': AttrOf(Identifiable, default=None)})
class Morphology(ModelInstance):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution(List[DataDownload]): If morphology is stored at the external location
            distribution should provide the path to it.
        mType(OntologyTerm): Morphological cell type.
        isPartOf(MorphologyRelease): Release this morphology is part of.
        view2d(Identifiable): Morphology view in 2D.
        view3d(Identifiable): Morphology view in 3D.
    '''


@attributes()
class SubCellularModelScript(ModelScript):
    '''Scripts attached to the model: ``mod`` file.

    Args:
        distribution(List[DataDownload]): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''


@attributes()
class EModelScript(ModelScript):
    '''Scripts attached to the model: ``hoc``, ``neuroml`` file.

    Args:
        distribution(List[DataDownload]): If model script is provided at the external location then
            distribution should provide the path to that location. Otherwise model script must
            be in the attachment of the entity.
    '''


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


@attributes({
    'description': AttrOf(str, default=None),
})
class SingleCellTraceGeneration(Activity):
    '''Single cell simulation trace genaration activity'''


@attributes()
class SingleCellSimulationTrace(_Entity):
    '''Single cell simulation trace file'''


@attributes({'hadMember': AttrOf(List[Trace], default=None)})
class TraceCollection(_Entity):
    '''Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    '''
    _type_name = 'Collection'


@attributes({'hadMember': AttrOf(List[Trace], default=None)})
class CoreTraceCollection(_Entity):
    '''Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    '''
    _url_domain = 'core'
    _url_name = 'tracecollection'
    _type_name = 'TraceCollection'


@attributes({
    'name': AttrOf(str),
    'channel': AttrOf(int),
    'description': AttrOf(str, default=None),
})
class ExperimentalCell(Frozen):
    '''Experimental cell.

    Args:
        name(str): TODO.
        channel(int): TODO.
        description(str): TODO.
    '''


@attributes({
    'features': AttrOf(Entity),
    'hadProtocol': AttrOf(Entity),
    'eType': AttrOf(str),
    'hypampThreshold': AttrOf(Entity, default=None),
    'isPartOf': AttrOf(EModelRelease, default=None),
})
class BluePyEfeFeatures(_Entity):
    '''BluePyEfe configuration entity'''


@attributes({
    'brainRegion': AttrOf(OntologyTerm),
    'species': AttrOf(OntologyTerm),
    'mType': AttrOf(OntologyTerm),
    'eType': AttrOf(OntologyTerm),
    'experimentalCell': AttrOf(List[ExperimentalCell]),
    'featureExtractionConfiguration': AttrOf(dict),
    'stimuliToExperimentMap': AttrOf(dict, default=None),
})
class BluePyEfeConfiguration(_Entity):
    '''BluePyEfe configuration entity'''
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


@attributes({'distribution': AttrOf(List[DataDownload])})
class CircuitCellProperties(_Entity):
    '''Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution(List[DataDownload]): Location of the cell placement file.
    '''


@attributes({'memodelRelease': AttrOf(MEModelRelease),
             'circuitCellProperties': AttrOf(CircuitCellProperties)})
class NodeCollection(_Entity):
    '''Node collection represents circuit nodes(positions, orientations)

    Args:
        memodelRelease(MEModelRelease): MEModel release this node collection is using.
        circuitCellProperties(CircuitCellProperties): Cell properties which are used in this node
                                                      collection.
    '''


@attributes({'edgePopulation': AttrOf(Entity),
             'synapseRelease': AttrOf(SynapseRelease)})
class EdgeCollection(_Entity):
    '''Edge collection represents circuit connectivity(synapses, projections)

    Args:
        edgePopulation(core.Entity): DataDownload providing path to the collection of nrn
            files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    '''


@attributes({'distribution': AttrOf(List[DataDownload])})
class Target(_Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution(List[DataDownload]): Location of the target file.
    '''


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


@attributes({'gitHash': AttrOf(str),
             'inputMechanisms': AttrOf(IonChannelMechanismRelease),
             'bluePyOptParameters': AttrOf(Configuration, default=None),
             'bluePyOptProtocol': AttrOf(Configuration, default=None),
             'bluePyOptRecipe': AttrOf(Configuration, default=None),
             'experimentalFeatures': AttrOf(BluePyEfeFeatures, default=None),
             'morphology': AttrOf(morphology.Entity, default=None),
             'hasOutput': AttrOf(EModelRelease, default=None)})
class BluePyOptRun(_Entity):
    '''Release base entity'''


@attributes()
class ETypeFeatureProtocol(_Entity):
    '''Trace protocol.'''


@attributes()
class TraceFeature(_Entity):
    '''Trace feature.'''


@attributes()
class Threshold(_Entity):
    '''Threshold.'''


@attributes({'activity': AttrOf(Activity)})
class EModelGenerationShape(_Entity):
    '''EModel generation.'''
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


@attributes({
    'configuration': AttrOf(dict),
    'template': AttrOf(DataDownload),
})
class SimWriterConfiguration(_Entity):
    '''SimWriter configuration entity.

    Args:
        configuration (dict): Dictionary of the parameters for the simwriter.
        template (DataDownload): Template file.
    '''


@attributes({
    'variable': AttrOf(str, validators=in_(['voltage', 'curent'])),
    'target': AttrOf(str, validators=in_(['compartment',
                                          'soma',
                                          'summation',
                                          'extra cellular recording'])),
})
class VariableReport(_Entity):
    '''Variable report.

    Args:
        variable (str): Variable shape(voltage, curent).
        target (str): The variable report target
            (compartment, soma, summation, extra cellular recording).
    '''


@attributes({
    'used': AttrOf(List[Union[SimWriterConfiguration, DetailedCircuit]]),
    'generated': AttrOf(VariableReport, default=None),
})
class Simulation(Activity):
    '''Simulation activity.

    Args:
        used (List[Union[CoreTraceCollection, BluePyEfeConfiguration]]): Used resources.
        generated (BluePyEfeFeatures): Extracted features.
    '''


# @attributes({
#     'name': AttrOf(str),
#     'description': AttrOf(str),
# })
# class PointNeuronModel(_Entity):
#     '''Point neuron model.
#
#     Args:
#         name (str): Name.
#         description (str): Reference to literature, params, doi.
#     '''


# @attributes({
#     'name': AttrOf(str),
#     'description': AttrOf(str),
# })
# class PointNeuronSynapseModel(_Entity):
#     '''Synapse model of the point neurons.
#
#     Args:
#         name (str): Name.
#         description (str): Reference to literature, params, doi.
#     '''


@attributes({
    'version': AttrOf(str),
    'neuronCount': AttrOf(int),
    'synapseCount': AttrOf(int),
    # 'neuronModels': AttrOf(List[PointNeuronModel]),
    # 'synapseModels': AttrOf(List[PointNeuronSynapseModel]),
})
class PointNeuronNetwork(ModelInstance):
    '''Point neuron network.

    Args:
        version (str): Point neuron network version.
        neuronCount (int): Neuron count in the point neuron network.
        synapseCount (int): Synapse count in the point neuron network.
    '''


# @attributes({
#     'name': AttrOf(str),
#     'description': AttrOf(str),
#     'used': AttrOf(CellAtlas),
#     'generated': AttrOf(PointNeuronNetwork),
# })
# class GenBrainActivity(Activity):
#     '''Generates point neuron network of the scarfold whole brain model.
#
#     Args:
#         name (str): Name.
#         description (str): Metadata, parameters, version of the algorithm.
#         used (CellAtlas): Used cell atlas.
#         generated (PointNeuronNetwork): Generated point neuron network.
#     '''
