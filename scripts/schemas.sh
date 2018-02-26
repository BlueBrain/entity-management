BASE=https://bbp-nexus.epfl.ch/dev

http -v -j PUT $BASE/v0/organizations/hbphackaton <<< {"@context":{"schema":"http://schema.org/"},"schema:name":"hbphackaton"}

http PUT $BASE/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/morphologyrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/morphologyrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/modelinstance/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/modelinstance/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/modelinstance/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/modelscript/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/modelscript/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/modelscript/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/subcellularmodel/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/subcellularmodel/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/subcellularmodel/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/emodel/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/emodel/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/emodel/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/emodelrelease/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/emodelrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/emodelrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/morphology/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/morphology/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/morphology/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/memodelrelease/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/memodelrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/memodelrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/cellplacement/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/cellplacement/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/cellplacement/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/nodecollection/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/nodecollection/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/nodecollection/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/synapserelease/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/synapserelease/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/synapserelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/edgecollection/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/edgecollection/v0.1.0.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/edgecollection/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/hbphackaton/simulation/detailedcircuit/v0.1.0 'Accept:application/ld+json' < modules/bbp-simulation/target/exported/hbphackaton/simulation/detailedcircuit/v0.0.1.json
http PATCH $BASE/v0/schemas/hbphackaton/simulation/detailedcircuit/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'
