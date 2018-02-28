BASE=https://bbp-nexus.epfl.ch/dev

http -v -j PUT $BASE/v0/organizations/neurosciencegraph <<< {"@context":{"schema":"http://schema.org/"},"schema:name":"neurosciencegraph"}
http -v -j PUT $BASE/v0/domains/neurosciencegraph/simulation 'Accept:application/ld+json' description='Simulation domain'



http -v -j PUT $BASE/v0/domains/neurosciencegraph/commons 'Accept:application/ld+json' description='Commons domain'
http PUT $BASE/v0/schemas/neurosciencegraph/commons/entity/v0.1.0 'Accept:application/ld+json' < modules/commons/target/exported/neurosciencegraph/commons/entity/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/commons/entity/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http -v -j PUT $BASE/v0/domains/neurosciencegraph/core 'Accept:application/ld+json' description='Core domain'
http PUT $BASE/v0/contexts/neurosciencegraph/core/data/v0.1.0 'Accept:application/ld+json' < modules/commons/target/exported/contexts/v0.1.0.json
http PATCH $BASE/v0/contexts/neurosciencegraph/core/data/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'



http PUT $BASE/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/morphologyrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/morphologyrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/modelinstance/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/modelinstance/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/modelinstance/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/modelscript/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/modelscript/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/modelscript/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/subcellularmodel/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/subcellularmodel/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/subcellularmodel/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/emodel/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/emodel/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/emodel/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/emodelrelease/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/emodelrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/emodelrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/morphology/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/morphology/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/morphology/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/memodelrelease/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/memodelrelease/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/memodelrelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/cellplacement/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/cellplacement/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/cellplacement/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/nodecollection/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/nodecollection/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/nodecollection/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/synapserelease/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/synapserelease/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/synapserelease/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/edgecollection/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/edgecollection/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/edgecollection/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/target/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/target/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/target/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'

http PUT $BASE/v0/schemas/neurosciencegraph/simulation/detailedcircuit/v0.1.0 'Accept:application/ld+json' < modules/simulation/target/exported/neurosciencegraph/simulation/detailedcircuit/v0.1.0.json
http PATCH $BASE/v0/schemas/neurosciencegraph/simulation/detailedcircuit/v0.1.0/config rev==1 published:=true 'Accept:application/ld+json'
