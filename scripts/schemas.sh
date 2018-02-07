http -v -j PUT https://bbp-nexus.epfl.ch/dev/v0/organizations/hbphackaton <<< {"@context":{"schema":"http://schema.org/"},"schema:name":"hbphackaton"}
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/morphologyrelease/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/emodelrelease/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/emodelrelease/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphology/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/morphology/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/memodelrelease/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/memodelrelease/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/cellplacement/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/cellplacement/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/nodecollection/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/nodecollection/v0.1.0.json
http PUT https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/synapserelease/v0.1.0 < modules/bbp-simulation/target/exported/hbphackaton/simulation/synapserelease/v0.1.0.json

http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/detailedcircuit/v0.0.1/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/emodelrelease/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/morphology/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/memodelrelease/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/cellplacement/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/nodecollection/v0.1.0/config rev==1 published:=true
http PATCH https://bbp-nexus.epfl.ch/dev/v0/schemas/hbphackaton/simulation/synapserelease/v0.1.0/config rev==1 published:=true
