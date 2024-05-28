# SPDX-License-Identifier: Apache-2.0

"""Simulation domain entities."""

from datetime import datetime
from typing import List, Union

from attr.validators import in_

from entity_management import morphology
from entity_management.atlas import AtlasRelease
from entity_management.base import (
    BrainLocation,
    Frozen,
    Identifiable,
    OntologyTerm,
    _NexusBySparqlIterator,
    attributes,
)
from entity_management.core import Activity, DataDownload, Entity, MultiDistributionEntity, Subject
from entity_management.electrophysiology import Trace
from entity_management.state import get_base_url
from entity_management.util import AttrOf
from entity_management.workflow import BbpWorkflowActivity, BbpWorkflowConfig


@attributes(
    {
        "modelOf": AttrOf(str, default=None),
        "brainLocation": AttrOf(BrainLocation, default=None),
        "subject": AttrOf(Subject, default=None),
    }
)
class ModelInstance(Entity):
    """Abstract model instance.

    Args:
        modelOf (str): Specifies the model.
        brainLocation (BrainLocation): Brain location.
        subject (Subject): Species ontology term.
    """


@attributes(
    {
        "brainLocation": AttrOf(BrainLocation, default=None),
        "subject": AttrOf(Subject, default=None),
    }
)
class ModelRelease(Entity):
    """Release base entity"""


class ModelScript(Entity):
    """Base entity for the scripts attached to the model."""


class ModelReleaseIndex(Entity):
    """Index files attached to release entities"""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "morphologyIndex": AttrOf(ModelReleaseIndex, default=None),
    }
)
class MorphologyRelease(ModelRelease):
    """Morphology release can be located at the external location or constituted from individual
    :class:`Morphology` entities.

    .. deprecated:: 1.0.19
        Use :class:`ReconstructedCellCollection` instead.

    Args:
        distribution (DataDownload): Data download url should point to the ``v1`` folder with
            morphologies in H5v1 format.
        morphologyIndex (ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    """


@attributes({"morphologyIndex": AttrOf(ModelReleaseIndex, default=None)})
class ReconstructedCellCollection(ModelRelease):
    """Reconstructed cell collection produced by the morphology release.

    Args:
        distribution (DataDownload): Data download url should point to the ``v1`` folder with
            morphologies in H5v1 format.
        morphologyIndex (ModelReleaseIndex): Morphology index is a compact representation of the
            morphology properties (MType, region ids) for the performance purposes. This attribute
            should provide a path to locate this file(such as neurondb.dat).
    """


@attributes()
class IonChannelMechanismRelease(ModelRelease):
    """Ion channel models release represents a collection of mod files."""


@attributes({"distribution": AttrOf(DataDownload)})
class SynapseRelease(ModelRelease):
    """Synapse release represents a collection of mod files.

    Args:
        distribution(DataDownload): Location of the synapse release/mod files.
    """


@attributes()
class Configuration(Entity):
    """Configuration file"""


@attributes(
    {
        "distribution": AttrOf(DataDownload, default=None),
        "mType": AttrOf(OntologyTerm, default=None),
        "isPartOf": AttrOf(MorphologyRelease, default=None),
        "view2d": AttrOf(Identifiable, default=None),
        "view3d": AttrOf(Identifiable, default=None),
    }
)
class Morphology(ModelInstance):
    """Neuron morphology.
    Actual morphology file can be stored as the attachment of this entity or stored at the location
    provided in the distribution attribute.

    Args:
        distribution (DataDownload): If morphology is stored at the external location
            distribution should provide the path to it.
        mType (OntologyTerm): Morphological cell type.
        isPartOf (MorphologyRelease): Release this morphology is part of.
        view2d (Identifiable): Morphology view in 2D.
        view3d (Identifiable): Morphology view in 3D.
    """


@attributes(
    {
        "description": AttrOf(str, default=None),
    }
)
class SingleCellTraceGeneration(Activity):
    """Single cell simulation trace genaration activity"""


@attributes()
class SingleCellSimulationTrace(Entity):
    """Single cell simulation trace file"""


@attributes({"hadMember": AttrOf(List[Trace], default=None)})
class TraceCollection(Entity):
    """Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    """


@attributes({"hadMember": AttrOf(List[Trace], default=None)})
class CoreTraceCollection(Entity):
    """Collection of traces

    Args:
        hadMember(List[Trace]): List of traces.
    """


@attributes(
    {
        "name": AttrOf(str),
        "channel": AttrOf(int),
        "description": AttrOf(str, default=None),
    }
)
class ExperimentalCell(Frozen):
    """Experimental cell.

    Args:
        name(str): TODO.
        channel(int): TODO.
        description(str): TODO.
    """


@attributes(
    {
        "features": AttrOf(Entity),
        "hadProtocol": AttrOf(Entity),
        "eType": AttrOf(str),
        "hypampThreshold": AttrOf(Entity, default=None),
    }
)
class BluePyEfeFeatures(Entity):
    """BluePyEfe configuration entity"""


@attributes(
    {
        "brainLocation": AttrOf(BrainLocation),
        "subject": AttrOf(Subject, default=None),
        "mType": AttrOf(OntologyTerm),
        "eType": AttrOf(OntologyTerm),
        "experimentalCell": AttrOf(List[ExperimentalCell]),
        "featureExtractionConfiguration": AttrOf(dict),
        "stimuliToExperimentMap": AttrOf(dict, default=None),
    }
)
class BluePyEfeConfiguration(Entity):
    """BluePyEfe configuration entity"""


@attributes({"distribution": AttrOf(DataDownload)})
class CircuitCellProperties(Entity):
    """Cell properties provides locationd of the MVD3 file with cell properties.

    Args:
        distribution (DataDownload): Location of the cell placement file.
    """


@attributes(
    {
        "circuitCellProperties": AttrOf(CircuitCellProperties),
    }
)
class NodeCollection(Entity):
    """Node collection represents circuit nodes(positions, orientations)

    Args:
        circuitCellProperties(CircuitCellProperties): Cell properties which are used in this node
                                                      collection.
    """


@attributes({"edgePopulation": AttrOf(Entity), "synapseRelease": AttrOf(SynapseRelease)})
class EdgeCollection(Entity):
    """Edge collection represents circuit connectivity(synapses, projections)

    Args:
        edgePopulation(core.Entity): DataDownload providing path to the collection of nrn
            files or syn2.
        synapseRelease(SynapseRelease): Synapse release used for this edge collection.
    """


@attributes({"distribution": AttrOf(DataDownload)})
class Target(Entity):
    """Location of the text file defining cell targets (i.e. named collections of cell GIDs)

    Args:
        distribution (DataDownload): Location of the target file.
    """


@attributes(
    {
        "circuitBase": AttrOf(DataDownload, default=None),
        "circuitConfigPath": AttrOf(DataDownload, default=None),
        "circuitType": AttrOf(str, default=None),
        "nodeCollection": AttrOf(NodeCollection, default=None),
        "edgeCollection": AttrOf(EdgeCollection, default=None),
        "target": AttrOf(Target, default=None),
        "atlasRelease": AttrOf(AtlasRelease, default=None),
    }
)
class DetailedCircuit(ModelInstance):
    """Detailed circuit.

    Args:
        circuitBase (DataDownload): Path to the CircuitConfig.

            .. deprecated:: 1.2.7
                Use ``circuitConfigPath`` instead.

        circuitConfigPath (DataDownload): Full path to the CircuitConfig including file name.
        circuitType (str): Circuit type. For example:

            * ``O1 circuit`` (e.g. circuit with central column + 6 surrounding columns)
            * ``Atlas-based``

        nodeCollection (NodeCollection): Node collection.
        edgeCollection (EdgeCollection): Edge collection.
        target (Target): Target.
        atlasRelease (AtlasRelease): AtlasRelease associated with the circuit.
    """


@attributes(
    {
        "gitHash": AttrOf(str),
        "inputMechanisms": AttrOf(IonChannelMechanismRelease),
        "bluePyOptParameters": AttrOf(Configuration, default=None),
        "bluePyOptProtocol": AttrOf(Configuration, default=None),
        "bluePyOptRecipe": AttrOf(Configuration, default=None),
        "experimentalFeatures": AttrOf(BluePyEfeFeatures, default=None),
        "morphology": AttrOf(morphology.Entity, default=None),
    }
)
class BluePyOptRun(Entity):
    """Release base entity"""


@attributes()
class ETypeFeatureProtocol(Entity):
    """Trace protocol."""


@attributes()
class TraceFeature(Entity):
    """Trace feature."""


@attributes()
class Threshold(Entity):
    """Threshold."""


@attributes({"activity": AttrOf(Activity)})
class EModelGenerationShape(Entity):
    """EModel generation."""


@attributes(
    {
        "used": AttrOf(List[Union[CoreTraceCollection, BluePyEfeConfiguration]]),
        "generated": AttrOf(BluePyEfeFeatures, default=None),
    }
)
class TraceFeatureExtraction(Activity):
    """Trace feature extraction activity.

    Args:
        used (List[Union[CoreTraceCollection, BluePyEfeConfiguration]]): Used resources.
        generated (BluePyEfeFeatures): Extracted features.
    """


@attributes()
class Report(Entity):
    """Generic report."""


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class SpikeReport(Report):
    """Spike report.

    Args:
        distribution (DataDownload): Spike report file ``out.dat``.
    """


@attributes(
    {
        "variable": AttrOf(str, validators=in_(["voltage", "curent"])),
        "target": AttrOf(
            str, validators=in_(["compartment", "soma", "summation", "extra cellular recording"])
        ),
    }
)
class VariableReport(Report):
    """Variable report.

    Args:
        variable (str): Variable shape(voltage, curent).
        target (str): The variable report target
            (compartment, soma, summation, extra cellular recording).
    """


@attributes(
    {
        "parameter": AttrOf(dict),
        "startedAtTime": AttrOf(datetime, default=None),
        "endedAtTime": AttrOf(datetime, default=None),
        "status": AttrOf(
            str, default=None, validators=in_([None, "Pending", "Running", "Done", "Failed"])
        ),
        "log_url": AttrOf(str, default=None),
        "config_file": AttrOf(str, default=None),
    }
)
class Simulation(Entity):
    """Simulation of the campaign entity.

    Args:
        parameter (dict): Dictionary of specific coords within the campaign.
        startedAtTime (datetime): Start time.
        endedAtTime (datetime): End time.
        status (str): Status of the simulation.
        log_url (str): URL at which log file can be viewed.
        config_file (): Full path to the simulation configuration file.
    """


@attributes(
    {
        "circuit": AttrOf(DetailedCircuit, default=None),
    }
)
class SimulationConfiguration(Entity):
    """Simulation configuration in terms of BlueConfig.

    Args:
        circuit (DetailedCircuit): reference to the detailed circuit.
    """


@attributes(
    {
        "configuration": AttrOf(DataDownload),
        "template": AttrOf(DataDownload),
        "target": AttrOf(DataDownload, default=None),
    }
)
class SimulationCampaignConfiguration(Entity):
    """Simulation campaign configuration entity.

    Args:
        configuration (DataDownload): Dictionary of the parameters for the simulation campaign
            stored in a json file.
        template (DataDownload): BlueConfig template file.
        target (DataDownload): Optional user target file to include with the simulations.
    """


@attributes(
    {
        "used": AttrOf(DetailedCircuit, default=None),
        "generated": AttrOf(SimulationCampaignConfiguration, default=None),
        "used_config": AttrOf(BbpWorkflowConfig, default=None),  # FIXME default=None
        "used_rev": AttrOf(
            int, default=None
        ),  # FIXME same default to support old use cases(non OBP)
    }
)
class SimulationCampaignGeneration(BbpWorkflowActivity):
    """Simulation campaign generation activity.

    Args:
        used (DetailedCircuit): Detailed circuit used for the simulation campaign.
        generated (SimulationCampaignConfiguration): Configuration of the simulation campaign that
            is produced as a result of running this activity.
    """

    @classmethod
    def used(cls, detailed_circuit, **kwargs):
        """List all sim campaign generation activities which used the specified detailed circuit.

        Args:
            detailed_circuit: Detailed circuit that was used in the simulation campaign.

        Returns:
            Iterator through the found resources.
        """
        type_ = f"{get_base_url()}/{cls.__name__}"
        # pylint: disable=consider-using-f-string
        query = """
            PREFIX prov: <http://www.w3.org/ns/prov#>
            SELECT ?entity
            WHERE {{
                ?entity a <{}> ;
                prov:used <{}> .
            }}
        """.format(
            type_, detailed_circuit.get_id()
        )

        return _NexusBySparqlIterator(cls, query, **kwargs)


@attributes(
    {
        "hadMember": AttrOf(List[Report], default=None),
    }
)
class SimulationCampaignReportCollection(Entity):
    """Simulation campaign.

    Groups multiple simulations when same circuit is tested under different conditions.

    Args:
        hadMember (List[Report]): Collection of simulation reports(spikes, soma voltage report).
    """


# @attributes({
#     'used': AttrOf(SimulationCampaignConfiguration, default=None),
#     'generated': AttrOf(SimulationCampaignReportCollection, default=None),
# })
# class SimulationCampaign(Activity):
#     '''Simulation campaign activity.
#
#     Groups multiple simulations when same circuit is tested under different conditions.
#
#     Args:
#         used (SimulationCampaignConfiguration): Used simulation campaign configuration.
#         generated (SimulationCampaignReportCollection): Generated simulation reports.
#     '''


@attributes(
    {
        "distribution": AttrOf(DataDownload),
        "image": AttrOf(DataDownload, default=None),
    }
)
class AnalysisReport(Entity):
    """Analysis report.

    Args:
        distribution (DataDownload): Generated report.
        image (DataDownload): Generated report image preview when applicable.
    """


@attributes(
    {
        "distribution": AttrOf(DataDownload),
    }
)
class AnalysisConfiguration(Entity):
    """Simulation analysis configuration.

    Args:
        distribution (DataDownload): Json representation of the configuration.
    """


@attributes(
    {
        "used": AttrOf(List[Identifiable], default=None),
    }
)
class Analysis(Activity):
    """Simulation analysis activity.

    Args:
        used (Identifiable): Used variable report/analysis configuration.
    """


@attributes(
    {
        "used": AttrOf(List[VariableReport], default=None),
        "generated": AttrOf(AnalysisReport, default=None),
        # 'wasInformedBy': AttrOf(SimulationCampaign, default=None),
    }
)
class CampaignAnalysis(Activity):
    """Simulation campaign analysis activity.

    Args:
        used (List[VariableReport]): Used simulation campaign variable reports.
        generated (AnalysisReport): Generated analysis report.
        wasInformedBy (entity_management.simulation.SimulationCampaign): Links to the simulation
            campaign which generated simulations used for the analysis.
    """


@attributes()
class DetailedCircuitValidation(Activity):
    """Detailed circuit validation activity."""


@attributes()
class DetailedCircuitValidationReport(AnalysisReport):
    """Detailed circuit validation report."""


class PlotCollection(MultiDistributionEntity):
    """Collection of plots."""


@attributes(
    {
        "simulations": AttrOf(DataDownload),
        "parameter": AttrOf(dict, default={}),
    }
)
class SimulationCampaign(Entity):
    """Simulation campaign entity that was executed.

    Args:
        simulations (DataDownload): serialized simulations xarray.
        parameter (dict): Parameters corresponding to the specific simulation.
    """


class SimulationCampaignExecution(BbpWorkflowActivity):
    """Simulation campagn execution activity."""


class SimulationCampaignAnalysis(BbpWorkflowActivity):
    """Simulation campaign analysis entity."""
