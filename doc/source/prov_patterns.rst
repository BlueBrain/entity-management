Provenance patterns
===================

Entity/Activity in the context of bbp-workflow
----------------------------------------------

When creating entities in the context of bbp-workflow if no ``wasGeneratedBy`` attribute was
explicitly provided then it will be initialized with the current WorkflowExecution activity.
Same applies to activities just the corresponting attribute linking to the WorkflowExecution
activity will be ``wasInfluencedBy``.

Many specific workflow tasks will explicitly override ``wasGeneratedBy`` attribute when
creating entities in order to link them directly to the specific activity in the context
of which they were created. The link to the WorkflowExecution activity then can be traced
through activity ``wasInfluencedBy`` attribute.

.. graphviz::

    digraph EntityActivityInWorkflow {
        graph [fontname = "Liberation Mono"];
        node [fontname = "Liberation Mono"];
        edge [fontname = "Liberation Mono"];
        Entity [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        Activity [
            shape = record style = filled fillcolor = lightblue
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "../generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        i1 [ shape=point; width=0 ];
        Entity -> i1 [label = "wasGeneratedBy"];
        i1 -> Activity;
        i1 -> WorkflowExecution;
        Activity -> WorkflowExecution [label = "wasInfluencedBy"];
    }


Model runtime parameters
------------------------

Attach metadata to the model entities in order to know what parameters to use when running simulations/visualizations.

.. graphviz::

    digraph ModelRuntimeParameters {
        graph [fontname = "Liberation Mono"];
        node [fontname = "Liberation Mono"];
        edge [fontname = "Liberation Mono"];
        Entity [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        ModelRuntimeParameters [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{ModelRuntimeParameters|name\lpurpose=viz\|sim\lmodelBuildingSteps\lallocationPartition\lnumberOfNodes\lnodeConstraint\l}"
            href = "../generated/entity_management.core.html#entity_management.core.ModelRuntimeParameters"
            target = "_top"
        ]
        ModelRuntimeParameters -> Entity [label = "model"];
    }


Simulation campaign analysis
----------------------------

.. graphviz::

    digraph SimulationCampaignAnalysis {
        graph [fontname = "Liberation Mono"];
        node [fontname = "Liberation Mono"];
        edge [fontname = "Liberation Mono"];
        VariableReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{VariableReport|variable=voltage\ltarget=soma\ldistribution=soma.bbp\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.VariableReport"
            target = "_top"
        ]
        AnalysisConfiguration [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisConfiguration|distribution=config}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.AnalysisConfiguration"
            target = "_top"
        ]
        DetailedCircuit [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{DetailedCircuit|circuitBase\lcircuitType\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.DetailedCircuit"
            target = "_top"
        ]
        Simulation [
            shape = record style = filled fillcolor = lightblue
            label = "{Simulation|status\ljobId\lpath\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.Simulation"
            target = "_top"
        ]
        SimulationCampaign [
            shape = record style = filled fillcolor = lightblue
            href = "../generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaign"
            target = "_top"
        ]
        SimWriterConfiguration [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimWriterConfiguration|configuration\ltemplate\ltarget\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.SimWriterConfiguration"
            target = "_top"
        ]
        Analysis [
            shape = record style = filled fillcolor = lightblue
            label = "{Analysis| \l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.Analysis"
            target = "_top"
        ]
        AnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisReport|distribution=image.png\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.AnalysisReport"
            target = "_top"
        ]
        CampaignAnalysis [
            shape = record style = filled fillcolor = lightblue
            label = "{CampaignAnalysis| \l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.CampaignAnalysis"
            target = "_top"
        ]
        i1 [ shape=point; width=0 ];
        i2 [ shape=point; width=0 ];
        AnalysisReport -> i1 [label = "wasGeneratedBy"];
        i1 -> Analysis;
        i1 -> CampaignAnalysis;
        VariableReport -> Simulation [label = "wasGeneratedBy"];
        Simulation -> SimulationCampaign [label = "wasInformedBy"];
        SimulationCampaign -> DetailedCircuit [label = "used"];
        SimulationCampaign -> SimWriterConfiguration [label = "used"];
        Analysis -> i2 [label = "used"];
        i2 -> VariableReport;
        i2 -> AnalysisConfiguration;
        Analysis -> Analysis [label = "wasInformedBy"];
        Analysis -> CampaignAnalysis [label = "wasInformedBy"];
        CampaignAnalysis -> SimulationCampaign [label = "wasInformedBy"];
    }
