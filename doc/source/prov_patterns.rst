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
        Entity [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        Activity [
            shape = record style = filled fillcolor = lightblue
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
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
        Entity [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        ModelRuntimeParameters [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{ModelRuntimeParameters|name\lpurpose=viz\|sim\lmodelBuildingSteps\lallocationPartition\lnumberOfNodes\lnodeConstraint\l}"
            href = "./generated/entity_management.core.html#entity_management.core.ModelRuntimeParameters"
            target = "_top"
        ]
        ModelRuntimeParameters -> Entity [label = "model"];
    }


Detailed circuit registration
-----------------------------

.. graphviz::

    digraph DetailedCircuitRegistration {
        DetailedCircuit [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{DetailedCircuit|circuitBase\lcircuitType\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.DetailedCircuit"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        DetailedCircuit -> WorkflowExecution [label = "wasGeneratedBy"];
    }


Simulation campaign
-------------------

.. graphviz::

    digraph SimulationCampaignGeneration {
        DataDownload [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.core.html#entity_management.core.DataDownload"
            target = "_top"
        ]
        DetailedCircuit [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{DetailedCircuit|circuitBase\lcircuitType\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.DetailedCircuit"
            target = "_top"
        ]
        SimulationCampaignConfiguration [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimulationCampaignConfiguration|name,description\lconfiguration,template,target\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignConfiguration"
            target = "_top"
        ]
        SimulationCampaignGeneration [
            shape = record style = filled fillcolor = lightblue
            label = "{SimulationCampaignGeneration|startedAtTime,endedAtTime\lstatus\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignGeneration"
            target = "_top"
        ]
        BbpWorkflowConfig [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.core.BbpWorkflowConfig"
            target = "_top"
        ]
        SimulationCampaign [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimulationCampaign|name,description\lcoords\lattrs\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaign"
            target = "_top"
        ]
        SimulationCampaignExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{SimulationCampaignExecution|startedAtTime,endedAtTime\lstatus\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignExecution"
            target = "_top"
        ]
        Simulation [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{Simulation|coords\lstartedAtTime,endedAtTime\lstatus,log_url\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.Simulation"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        # simulation
        SimulationCampaignGeneration -> BbpWorkflowConfig [label = "used_config"];
        SimulationCampaignGeneration -> DetailedCircuit [label = "used"];
        SimulationCampaignConfiguration -> SimulationCampaignGeneration [label = "wasGeneratedBy"];
        SimulationCampaignGeneration -> SimulationCampaignConfiguration [label = "generated"];
        SimulationCampaignGeneration -> WorkflowExecution [label = "wasInfluencedBy"];
        SimulationCampaignExecution -> BbpWorkflowConfig [label = "used_config"];
        SimulationCampaignExecution -> SimulationCampaignConfiguration [label = "used"];
        SimulationCampaignExecution -> SimulationCampaign [label = "generated"];
        SimulationCampaignExecution -> WorkflowExecution [label = "wasInfluencedBy"];
        SimulationCampaign -> SimulationCampaignExecution [label = "wasGeneratedBy"];
        SimulationCampaign -> Simulation [label = "hasPart"];
        SimulationCampaign -> DataDownload [label = "simulations"];
        Simulation -> SimulationCampaignExecution [label = "wasGeneratedBy"];
    }

Simulation campaign analysis (single)
-------------------------------------

.. graphviz::

    digraph SimulationCampaignGeneration {
        DataDownload [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.core.html#entity_management.core.DataDownload"
            target = "_top"
        ]
        BbpWorkflowConfig [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.core.BbpWorkflowConfig"
            target = "_top"
        ]
        SimulationCampaign [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimulationCampaign|name,description\lcoords\lattrs\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaign"
            target = "_top"
        ]
        Simulation [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{Simulation|coords\lstartedAtTime,endedAtTime\lstatus,log_url\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.Simulation"
            target = "_top"
        ]
        SimulationCampaignAnalysis [
            shape = record style = filled fillcolor = lightblue
            label = "{SimulationCampaignAnalysis|startedAtTime,endedAtTime\lstatus\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignAnalysis"
            target = "_top"
        ]
        AnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisReport|name,description\lcategories,types\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.AnalysisReport"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        # simulation
        SimulationCampaign -> Simulation [label = "hasPart"];
        SimulationCampaign -> DataDownload [label = "simulations"];
        # analysis
        SimulationCampaignAnalysis -> BbpWorkflowConfig [label = "used_config"];
        SimulationCampaignAnalysis -> SimulationCampaign [label = "used"];
        SimulationCampaignAnalysis -> WorkflowExecution [label = "wasInfluencedBy"];
        AnalysisReport -> Simulation [label = "derivation"];
        AnalysisReport -> SimulationCampaignAnalysis [label = "wasGeneratedBy"];
        AnalysisReport -> DataDownload [label = "distribution"];
    }


Simulation campaign analysis (multiple)
---------------------------------------

.. graphviz::

    digraph MultiCumulativeSimulationCampaign {
        DataDownload [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.core.html#entity_management.core.DataDownload"
            target = "_top"
        ]
        BbpWorkflowConfig [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.core.BbpWorkflowConfig"
            target = "_top"
        ]
        SimulationCampaign [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimulationCampaign|name,description\lcoords\lattrs\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaign"
            target = "_top"
        ]
        Simulation [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{Simulation|coords\lstartedAtTime,endedAtTime\lstatus,log_url\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.Simulation"
            target = "_top"
        ]
        MultiCumulativeSimulationCampaignAnalysis [
            shape = record style = filled fillcolor = lightblue
            label = "{MultiCumulativeSimulationCampaignAnalysis|startedAtTime,endedAtTime\lstatus\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.MultiCumulativeSimulationCampaignAnalysis"
            target = "_top"
        ]
        AnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisReport|name,description\lcategories,types\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.AnalysisReport"
            target = "_top"
        ]
        CumulativeAnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{CumulativeAnalysisReport|name,description\lcategories,types\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.CumulativeAnalysisReport"
            target = "_top"
        ]
        MultiCumulativeAnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.simulation.MultiCumulativeAnalysisReport"
            target = "_top"
        ]
        AnalysisSoftwareSourceCode [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisSoftwareSourceCode|name,description\lcodeRepository,commit\lsubdirectory,command\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.AnalysisSoftwareSourceCode"
            target = "_top"
        ]
        Contribution [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        { rank=max MultiCumulativeAnalysisReport }
        # simulation
        SimulationCampaign -> Simulation [label = "hasPart"];
        SimulationCampaign -> DataDownload [label = "simulations"];
        # analysis
        MultiCumulativeSimulationCampaignAnalysis -> BbpWorkflowConfig [label = "used_config"];
        MultiCumulativeSimulationCampaignAnalysis -> SimulationCampaign [label = "used"];
        MultiCumulativeSimulationCampaignAnalysis -> WorkflowExecution [label = "wasInfluencedBy"];
        MultiCumulativeSimulationCampaignAnalysis -> MultiCumulativeAnalysisReport [label = "generated"];
        AnalysisReport -> Simulation [label = "derivation"];
        AnalysisReport -> MultiCumulativeSimulationCampaignAnalysis [label = "wasGeneratedBy"];
        AnalysisReport -> DataDownload [label = "distribution"];
        CumulativeAnalysisReport -> SimulationCampaign [label = "derivation"];
        CumulativeAnalysisReport -> MultiCumulativeSimulationCampaignAnalysis [label = "wasGeneratedBy"];
        CumulativeAnalysisReport -> AnalysisReport [label = "hasPart"];
        CumulativeAnalysisReport -> Contribution [label = "contribution"];
        Contribution -> AnalysisSoftwareSourceCode [label = "agent"];
        MultiCumulativeAnalysisReport -> MultiCumulativeSimulationCampaignAnalysis [label = "wasGeneratedBy"];
        MultiCumulativeAnalysisReport -> CumulativeAnalysisReport [label = "hasPart"];
    }


EModel analysis (multiple)
--------------------------

.. graphviz::

    digraph MultiEModelAnalysis {
        DataDownload [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.core.html#entity_management.core.DataDownload"
            target = "_top"
        ]
        EModel [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{EModel|etype,iteration,seed\l}"
            href = "./generated/entity_management.emodel.html#entity_management.emodel.EModel"
            target = "_top"
        ]
        BbpWorkflowConfig [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.core.BbpWorkflowConfig"
            target = "_top"
        ]
        MultiEModelAnalysis [
            shape = record style = filled fillcolor = lightblue
            label = "{MultiEModelAnalysis|startedAtTime,endedAtTime\lstatus\l}"
            href = "./generated/entity_management.emodel.html#entity_management.emodel.MultiEModelAnalysis"
            target = "_top"
        ]
        AnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisReport|name,description\lcategories,types\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.AnalysisReport"
            target = "_top"
        ]
        CumulativeAnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{CumulativeAnalysisReport|name,description\lcategories,types\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.CumulativeAnalysisReport"
            target = "_top"
        ]
        MultiCumulativeAnalysisReport [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "./generated/entity_management.simulation.html#entity_management.simulation.MultiCumulativeAnalysisReport"
            target = "_top"
        ]
        AnalysisSoftwareSourceCode [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{AnalysisSoftwareSourceCode|name,description\lcodeRepository,commit\lsubdirectory,command\l}"
            href = "./generated/entity_management.simulation.html#entity_management.simulation.AnalysisSoftwareSourceCode"
            target = "_top"
        ]
        Contribution [
            shape = Mrecord style = filled fillcolor = lemonchiffon
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "./generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        { rank=max MultiCumulativeAnalysisReport }
        MultiEModelAnalysis -> BbpWorkflowConfig [label = "used_config"];
        MultiEModelAnalysis -> EModel [label = "used"];
        MultiEModelAnalysis -> WorkflowExecution [label = "wasInfluencedBy"];
        MultiEModelAnalysis -> MultiCumulativeAnalysisReport [label = "generated"];
        AnalysisReport -> EModel [label = "derivation"];  # FIXME: is it needed?
        AnalysisReport -> MultiEModelAnalysis [label = "wasGeneratedBy"];
        AnalysisReport -> DataDownload [label = "distribution"];
        CumulativeAnalysisReport -> EModel [label = "derivation"];
        CumulativeAnalysisReport -> MultiEModelAnalysis [label = "wasGeneratedBy"];
        CumulativeAnalysisReport -> AnalysisReport [label = "hasPart"];
        CumulativeAnalysisReport -> Contribution [label = "contribution"];
        Contribution -> AnalysisSoftwareSourceCode [label = "agent"];
        MultiCumulativeAnalysisReport -> MultiEModelAnalysis [label = "wasGeneratedBy"];
        MultiCumulativeAnalysisReport -> CumulativeAnalysisReport [label = "hasPart"];
    }
