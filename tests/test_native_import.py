import json
from math import pi

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.quantum_info import Statevector

from qfault import qasm_import
from qfault.lab import LabRequest, investigate_lab
from qfault.storage import ArtifactStore, verify_export


def convert(circuit, **options):
    function = getattr(qasm_import, 'from_qiskit', None)
    assert callable(function), 'a bounded QuantumCircuit conversion API is required'
    return function(circuit, **options)


def test_native_all_supported_gates_preserve_complex_state_and_nonzero_input():
    q = QuantumCircuit(3)
    q.h(0); q.x(1); q.z(2); q.s(0)
    q.rx(.3, 1); q.ry(-.6, 2); q.rz(.4, 0)
    q.cx(0, 2); q.cz(2, 1); q.cp(pi / 3, 1, 0); q.swap(0, 2)
    q.global_phase = .27
    converted = convert(q, input_bitstring='101')
    prepared = QuantumCircuit(3)
    prepared.x(0); prepared.x(2)
    prepared.compose(q, inplace=True)
    actual = Statevector.from_instruction(converted.subject().native())
    expected = Statevector.from_instruction(prepared)
    assert actual.equiv(expected)
    assert len(converted.preparation()) == 2
    assert len(converted.gates) == len(q.data)
    provenance = converted.import_provenance.model_dump(mode='json')
    assert json.loads(provenance['source_representation'])['global_phase'] == pytest.approx(.27)
    assert provenance['converted_circuit_id'] == converted.circuit_id


def test_native_measurement_and_barrier_removal_are_opt_in_and_recorded():
    q = QuantumCircuit(2, 2)
    q.h(0); q.barrier(); q.measure(0, 1); q.measure(1, 0)
    with pytest.raises(ValueError, match='instruction 1.*barrier'):
        convert(q)
    with pytest.raises(ValueError, match='instruction 2.*measure'):
        convert(q, strip_barriers=True)
    imported = convert(q, strip_barriers=True, strip_terminal_measurements=True)
    source = json.loads(imported.import_provenance.source_representation)
    assert source['instructions'][-1]['clbits'] == [0]
    assert imported.import_provenance.strip_terminal_measurements
    assert len(imported.gates) == 1


@pytest.mark.parametrize('operation', ['reset', 'custom', 'parameter', 'interior_measurement', 'control_flow', 'too_many'])
def test_native_rejects_unsupported_semantics_with_index(operation):
    q = QuantumCircuit(2, 1)
    q.h(0)
    if operation == 'reset': q.reset(0)
    elif operation == 'custom': q.append(Gate('x', 1, []), [0])
    elif operation == 'parameter': q.rx(Parameter('theta'), 0)
    elif operation == 'interior_measurement': q.measure(0, 0); q.x(1)
    elif operation == 'control_flow':
        with q.if_test((q.clbits[0], 1)): q.x(0)
    elif operation == 'too_many':
        for _ in range(32): q.x(0)
    with pytest.raises(ValueError, match='instruction [0-9]+'):
        convert(q, strip_terminal_measurements=True)


def test_native_provenance_survives_measurement_export_and_saved_request(tmp_path):
    q = QuantumCircuit(2); q.x(0)
    circuit = convert(q, input_bitstring='10')
    request = LabRequest(circuit=circuit, contract={'kind':'measurement_distribution', 'basis':'Z',
        'expected_probabilities':{'11':1.}, 'tolerance':.2}, batch_shots=1024, max_shots=4096)
    result = investigate_lab(request)
    store = ArtifactStore(tmp_path / 'investigations')
    eid = store.save(result)
    report = store.export(eid)
    assert verify_export(report)['valid']
    saved = report['investigation']['replay']['request']['circuit']
    assert saved['import_provenance']['source_sha256'] == circuit.import_provenance.source_sha256
    restored = LabRequest.model_validate({**request.model_dump(mode='json'), 'circuit':saved})
    np.testing.assert_allclose(Statevector.from_instruction(restored.circuit.subject().native()).probabilities(), [0,0,0,1])


def test_legacy_circuit_serialization_stays_byte_compatible():
    from qfault.lab import CustomCircuit
    circuit = CustomCircuit(schema_version=1, name='legacy', n_qubits=2,
        input={'kind':'computational_basis','bitstring':'00'}, gates=[])
    assert 'import_provenance' not in circuit.model_dump(mode='json')
