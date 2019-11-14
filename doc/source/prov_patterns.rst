Provenance patterns
===================

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
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "../generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        Simulation -> SimulationCampaign [label = "wasStartedBy"];
        Simulation -> VariableReport [label = "generated"];
        SimulationCampaign -> DetailedCircuit [label = "used"];
        SimulationCampaign -> SimWriterConfiguration [label = "used"];
        Analysis -> VariableReport [label = "used"];
        Analysis -> AnalysisReport [label = "generated"];
        Analysis -> CampaignAnalysis [label = "wasStartedBy"];
        CampaignAnalysis -> SimulationCampaign [label = "wasInformedBy"];
        CampaignAnalysis -> AnalysisReport [label = "generated"];
        CampaignAnalysis -> WorkflowExecution [label = "wasStartedBy"];
        SimulationCampaign -> WorkflowExecution [label = "wasStartedBy"];
    }
