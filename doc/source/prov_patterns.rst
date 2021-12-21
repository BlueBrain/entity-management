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


Detailed circuit registration
-----------------------------

.. graphviz::

    digraph DetailedCircuitRegistration {
        DetailedCircuit [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{DetailedCircuit|circuitBase\lcircuitType\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.DetailedCircuit"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            href = "../generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        DetailedCircuit -> WorkflowExecution [label = "wasGeneratedBy"];
    }


Simulation campaign generation
------------------------------

.. graphviz::

    digraph SimulationCampaignGeneration {
        DetailedCircuit [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{DetailedCircuit|circuitBase\lcircuitType\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.DetailedCircuit"
            target = "_top"
        ]
        SimulationCampaignConfiguration [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{SimulationCampaignConfiguration|name\ldescription\lconfiguration\ltemplate\ltarget\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignConfiguration"
            target = "_top"
        ]
        SimulationCampaignGeneration [
            shape = record style = filled fillcolor = lightblue
            href = "../generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignGeneration"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            label = "{WorkflowExecution|module\ltask\lversion\lparameters\l}"
            href = "../generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        { rank=same SimulationCampaignConfiguration DetailedCircuit }
        SimulationCampaignGeneration -> WorkflowExecution [label = "wasInfluencedBy"];
        SimulationCampaignGeneration -> DetailedCircuit [label = "used"];
        SimulationCampaignConfiguration -> SimulationCampaignGeneration [label = "wasGeneratedBy"];
        SimulationCampaignGeneration -> SimulationCampaignConfiguration [label = "generated"];
    }


Simulation campaign analysis
----------------------------

.. graphviz::

    digraph SimulationCampaignAnalysis {
        PlotCollection [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            label = "{PlotCollection|distribution=[ca_scan_1.png, ca_scan_2.png, ...]\l}"
            href = "../generated/entity_management.simulation.html#entity_management.simulation.PlotCollection"
            target = "_top"
        ]
        SimulationCampaignConfiguration [
            shape = Mrecord style = filled fillcolor = lemonchiffon
            href = "../generated/entity_management.simulation.html#entity_management.simulation.SimulationCampaignConfiguration"
            target = "_top"
        ]
        WorkflowExecution [
            shape = record style = filled fillcolor = lightblue
            href = "../generated/entity_management.core.html#entity_management.core.WorkflowExecution"
            target = "_top"
        ]
        PlotCollection -> WorkflowExecution [label = "wasGeneratedBy"];
        PlotCollection -> SimulationCampaignConfiguration [label = "wasDerivedFrom"];
    }
