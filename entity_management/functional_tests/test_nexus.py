''' test nexus integration '''
import nose.tools as nt
import entity_management.nexus as nx


def _filter_nexus_keys(d):
    ''' remove nexus keys '''
    return {k: d[k] for k in d.iterkeys() if k not in nx.WHITE_LIST_NEXUS}


def _check_keys(data_to_check, reference_data):
    filtered_data = _filter_nexus_keys(data_to_check)
    filtered_ref = _filter_nexus_keys(reference_data)

    for k in filtered_ref.iterkeys():
        nt.eq_(filtered_ref[k], filtered_data[k])

    nt.eq_(set(filtered_data.keys()), set(filtered_ref.keys()))


def test_create_circuit():
    ''' test creation of a circuit '''

    circuit_data = {
        'cells': 'foo_cells',
        'connectome': 'foo_connectome',
        'targets': ['foo_target'],
    }
    circuit_id = nx.register_entity('fakecircuit', circuit_data)

    returned_data = nx.get_entity(circuit_id)
    nt.ok_('@id' in returned_data)
    nt.eq_(returned_data['@type'], 'bbprod:circuit')
    nt.eq_(returned_data['rev'], 1)
    _check_keys(returned_data, circuit_data)


def test_update_circuit():
    ''' update the circuit '''
    circuit_data = {
        'cells': 'foo_cells_update',
        'connectome': 'foo_connectome_update',
        'targets': ['foo_target_update'],
    }
    circuit_id = nx.register_entity('fakecircuit', circuit_data)

    updated_data = nx.get_entity(circuit_id)
    updated_data['cells'] = 'updated_foo'
    returned_ids = nx.update_entity(circuit_id, updated_data)
    returned_data = nx.get_entity(returned_ids)
    nt.eq_(returned_data['@id'], circuit_id['@id'])
    nt.eq_(returned_data['@type'], 'bbprod:circuit')
    nt.eq_(returned_ids['rev'], 2)
    _check_keys(returned_data, updated_data)

# TODO find a way to test that
# def test_get_entities():
#     nx.get_entities('fakecircuit', 0, 10)
