'''Simulation domain entities.'''

from typing import List, Union

from attr.validators import in_

import entity_management.morphology as morphology
from entity_management.base import (Identifiable, attributes, Frozen, OntologyTerm,
                                    QuantitativeValue, BrainLocation)
from entity_management.core import (Entity, Activity, Agent, EntityMixin,
                                    SoftwareAgent, DataDownload, Subject)
from entity_management.electrophysiology import Trace
from entity_management.util import AttrOf


@attributes({
    'name': AttrOf(str, default=None),
    'description': AttrOf(str, default=None),
    'distribution': AttrOf(DataDownload, default=None),
})
class _Entity(EntityMixin, Identifiable):
    '''Base abstract class for many things having `name` and `description`

    Args:
        name (str): Entity name.
        description (str): Short description of the entity.
        distribution (DataDownload): Data download.
        wasDerivedFrom (List[Identifiable]): List of associated provenance entities.
    '''


@attributes({
    'modelOf': AttrOf(str, default=None),
    'brainLocation': AttrOf(BrainLocation, default=None),
    'subject': AttrOf(Subject, default=None),
})
class ModelInstance(_Entity):
    '''Abstract model instance.

    Args:
        modelOf (str): Specifies the model.
        brainLocation (BrainLocation): Brain location.
        subject (Subject): Species ontology term.
    '''


@attributes({
    'brainLocation': AttrOf(BrainLocation, default=None),
    'subject': AttrOf(Subject, default=None),
})
class ModelRelease(_Entity):
    '''Release base entity'''


@attributes()
class ModelScript(_Entity):
    '''Base entity for the scripts attached to the model.'''


@attributes()
class ModelReleaseIndex(_Entity):
    '''Index files attached to release entities'''


@attributes({'distribution': AttrOf(DataDownload),
             'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class MorphologyRelease(ModelRelease):
    '''Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    .. deprecated:: 1.0.19
        Use :class:`ReconstructedCellCollection` instead.

    Args:
        distribution (DataDownload): Data download url should point to the ``v1`` folder with
            morphologies in H5v1 format.
        morphologyIndex (ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''


@attributes({'morphologyIndex': AttrOf(ModelReleaseIndex, default=None)})
class ReconstructedCellCollection(ModelRelease):
    '''Reconstructed cell collection produced by the morphology release.

    Args:
        distribution (DataDownload): Data download url should point to the ``v1`` folder with
            morphologies in H5v1 format.
        morphologyIndex (ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    '''


@attributes()
class IonChannelMechanismRelease(ModelRelease):
    '''Ion channel models release represents a collection of mod files.
    '''


@attributes({'distribution': AttrOf(DataDownload)})
class SynapseRelease(ModelRelease):
    '''Synapse release represents a collection of mod files.

    Args:
        distribution(DataDownload): Location of the synapse release/mod files.
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
    'distribution': AttrOf(DataDownload, default=None),
    'emodelIndex': AttrOf(ModelReleaseIndex, default=None),
    'isPartOf': AttrOf(Identifiable, default=None)
})
class EModelRelease(ModelRelease):
    '''Electrical model release

    Args:
        distribution (DataDownload): EModel release location provides a path to ``hoc`` files.
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


@attributes({'distribution': AttrOf(DataDownload, default=None),
             'mType': AttrOf(OntologyTerm, default=None),
             'isPartOf': AttrOf(MorphologyRelease, default=None),
             'view2d': AttrOf(Identifiable, default=None),
             'view3d': AttrOf(Identifiable, default=None)})
class Morphology(ModelInstance):
    '''Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution (DataDownload): If morphology is stored at the external location
            distribution should provide the path to it.
        mType (OntologyTerm): Morphological cell type.
        isPartOf (MorphologyRelease): Release this morphology is part of.
        view2d (Identifiable): Morphology view in 2D.
        view3d (Identifiable): Morphology view in 3D.
    '''


@attributes()
class SubCellularModelScript(ModelScript):
    '''Scripts attached to the model: ``mod`` file.

    Args:
        distribution (DataDownload): Distribution should provide the path to the model script.
    '''


@attributes()
class EModelScript(ModelScript):
    '''Scripts attached to the model: ``hoc``, ``neuroml`` file.

    Args:
        distribution (DataDownload): Provides path to get the relevant scripts.
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


@attributes({'hadMember': AttrOf(List[Trace], default=None)})
class CoreTraceCollection(_Entity):
    '''Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    '''


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
    'brainLocation': AttrOf(BrainLocation),
    'subject': AttrOf(Subject, default=None),
    'mType': AttrOf(OntologyTerm),
    'eType': AttrOf(OntologyTerm),
    'experimentalCell': AttrOf(List[ExperimentalCell]),
    'featureExtractionConfiguration': AttrOf(dict),
    'stimuliToExperimentMap': AttrOf(dict, default=None),
})
class BluePyEfeConfiguration(_Entity):
    '''BluePyEfe configuration entity'''


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


@attributes({'distribution': AttrOf(DataDownload)})
class CircuitCellProperties(_Entity):
    '''Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution (DataDownload): Location of the cell placement file.
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


@attributes({'distribution': AttrOf(DataDownload)})
class Target(_Entity):
    '''Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution (DataDownload): Location of the target file.
    '''


@attributes({'circuitBase': AttrOf(DataDownload),
             'circuitType': AttrOf(str, default=None),
             'nodeCollection': AttrOf(NodeCollection, default=None),
             'edgeCollection': AttrOf(EdgeCollection, default=None),
             'target': AttrOf(Target, default=None)})
class DetailedCircuit(ModelInstance):
    '''Detailed circuit.

    Args:
        circuitBase (DataDownload): Path to the CircuitConfig.
        circuitType (str): Circuit type. For example:

            * ``O1 circuit`` (e.g. circuit with central column + 6 surrounding columns)
            * ``Atlas-based``

        nodeCollection (NodeCollection): Node collection.
        edgeCollection (EdgeCollection): Edge collection.
        target (Target): Target.
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


@attributes()
class Report(_Entity):
    '''Generic report.'''


@attributes({
    'distribution': AttrOf(DataDownload),
})
class SpikeReport(Report):
    '''Spike report.

    Args:
        distribution (DataDownload): Spike report file ``out.dat``.
    '''


@attributes({
    'variable': AttrOf(str, validators=in_(['voltage', 'curent'])),
    'target': AttrOf(str, validators=in_(['compartment',
                                          'soma',
                                          'summation',
                                          'extra cellular recording'])),
})
class VariableReport(Report):
    '''Variable report.

    Args:
        variable (str): Variable shape(voltage, curent).
        target (str): The variable report target
            (compartment, soma, summation, extra cellular recording).
    '''


@attributes({
    'used': AttrOf(DetailedCircuit, default=None),
    'spikes': AttrOf(SpikeReport, default=None),
    'generated': AttrOf(List[Report], default=None),
    'jobId': AttrOf(str, default=None),
    'path': AttrOf(str, default=None),
    'params': AttrOf(DataDownload, default=None),
})
class Simulation(Activity):
    '''Simulation activity.

    Args:
        used (DetailedCircuit): Detailed circuit used to run the simulation.
        spikes (SpikeReport): Generated spike report.
        generated (List[Report]): Generated reports by the simulation. This will include
            mandatory SpikeReport and other VariableReport's.
        jobId (str): SLURM job id.
        path (str): Location of the simulation BlueConfig and the SLURM log.
        params (DataDownload): If simulation is part of the campaign, ``params``
            will contain all the parameters used to instantiate this simulation.
    '''


@attributes({
    'circuit': AttrOf(DetailedCircuit, default=None),
})
class SimulationConfiguration(_Entity):
    '''Simulation configuration in terms of BlueConfig.

    Args:
        circuit (DetailedCircuit): reference to the detailed circuit.
    '''


@attributes({
    'configuration': AttrOf(DataDownload),
    'template': AttrOf(DataDownload),
    'target': AttrOf(DataDownload, default=None),
})
class SimulationCampaignConfiguration(_Entity):
    '''Simulation campaign configuration entity.

    Args:
        configuration (DataDownload): Dictionary of the parameters for the simulation campaign
            stored in a json file.
        template (DataDownload): BlueConfig template file.
        target (DataDownload): Optional user target file to include with the simulations.
    '''


@attributes({
    'used': AttrOf(DetailedCircuit, default=None),
    'generated': AttrOf(SimulationCampaignConfiguration, default=None),
})
class SimulationCampaignGeneration(Activity):
    '''Simulation campaign generation activity.

    Args:
        used (DetailedCircuit): Detailed circuit used for the simulation campaign.
        generated (SimulationCampaignConfiguration): Configuration of the simulation campaign that
            is produced as a result of running this activity.
    '''


@attributes({
    'hadMember': AttrOf(List[Report], default=None),
})
class SimulationCampaignReportCollection(_Entity):
    '''Simulation campaign.

    Groups multiple simulations when same circuit is tested under different conditions.

    Args:
        hadMember (List[Report]): Collection of simulation reports(spikes, soma voltage report).
    '''


@attributes({
    'used': AttrOf(SimulationCampaignConfiguration, default=None),
    'generated': AttrOf(SimulationCampaignReportCollection, default=None),
})
class SimulationCampaign(Activity):
    '''Simulation campaign activity.

    Groups multiple simulations when same circuit is tested under different conditions.

    Args:
        used (SimulationCampaignConfiguration): Used simulation campaign configuration.
        generated (SimulationCampaignReportCollection): Generated simulation reports.
    '''


@attributes({
    'distribution': AttrOf(DataDownload),
    'image': AttrOf(DataDownload, default=None),
})
class AnalysisReport(_Entity):
    '''Analysis report.

    Args:
        distribution (DataDownload): Generated report.
        image (DataDownload): Generated report image preview when applicable.
    '''


@attributes({
    'distribution': AttrOf(DataDownload),
})
class AnalysisConfiguration(_Entity):
    '''Simulation analysis configuration.

    Args:
        distribution (DataDownload): Json representation of the configuration.
    '''


@attributes({
    'used': AttrOf(List[Identifiable], default=None),
})
class Analysis(Activity):
    '''Simulation analysis activity.

    Args:
        used (Identifiable): Used variable report/analysis configuration.
    '''


@attributes({
    'used': AttrOf(List[VariableReport], default=None),
    'generated': AttrOf(AnalysisReport, default=None),
    'wasInformedBy': AttrOf(SimulationCampaign, default=None),
})
class CampaignAnalysis(Activity):
    '''Simulation campaign analysis activity.

    Args:
        used (List[VariableReport]): Used simulation campaign variable reports.
        generated (AnalysisReport): Generated analysis report.
        wasInformedBy (SimulationCampaign): Links to the simulation campaign which
            generated simulations used for the analysis.
    '''


@attributes()
class DetailedCircuitValidation(Activity):
    '''Detailed circuit validation activity.'''


@attributes()
class DetailedCircuitValidationReport(AnalysisReport):
    '''Detailed circuit validation report.  '''
