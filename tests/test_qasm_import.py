"""Boundary tests: no rewrite may hide unsupported source semantics."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from qiskit import qasm2
from qiskit.circuit.library import CSwapGate
from qiskit.quantum_info import Operator

from qfault.lab import CustomCircuit


def source(body, n=2):
    return f'OPENQASM 2.0; include "qelib1.inc"; qreg q[{n}]; creg c[{n}]; {body}'


def importer():
    # A missing importer is an assertion failure during the initial red phase.
    import qfault
    assert (Path(qfault.__file__).parent / "qasm_import.py").exists(), "bounded importer missing"
    from qfault.qasm_import import import_qasm2
    return import_qasm2


def test_terminal_measurements_and_barriers_have_explicit_provenance():
    text = source("h q[1]; barrier q; cx q[1],q[0]; measure q[1] -> c[0]; measure q[0] -> c[1];")
    result = importer()(text, name="external")
    circuit = CustomCircuit.model_validate(result["circuit"])
    assert [(g.name, g.qubits) for g in circuit.gates] == [("h", (1,)), ("cx", (1, 0))]
    assert circuit.input.bitstring == "00"
    provenance = result["provenance"]
    assert provenance["sha256"] == hashlib.sha256(text.encode()).hexdigest()
    assert provenance["measurement_mapping"] == [{"qubit": 1, "classical_bit": 0}, {"qubit": 0, "classical_bit": 1}]
    assert provenance["barriers_removed"] == [{"instruction_index": 1, "qubits": [0, 1]}]
    assert provenance["operator_equivalent"] is True
    assert provenance["basis_inputs_checked"] == 4


@pytest.mark.parametrize("body,code", [
    ("measure q[0] -> c[0]; x q[1];", "interior_measurement"),
    ("reset q[0];", "reset"),
    ("if(c==0) x q[0];", "classical_control"),
    ("gate mine a { x a; } mine q[0];", "custom_gate_definition"),
    ("opaque mine a; mine q[0];", "opaque_definition"),
    ("mystery q[0];", "unsupported_operation"),
    ('include "../secret.inc"; x q[0];', "arbitrary_include"),
    ("while(c==0) x q[0];", "dynamic_operation"),
])
def test_rejects_unsupported_semantics_before_translation(body, code):
    run = importer()
    from qfault.qasm_import import QASMImportError
    with pytest.raises(QASMImportError) as caught:
        run(source(body))
    assert caught.value.code == code


@pytest.mark.parametrize("body,n", [("t q[0]; tdg q[1]; sdg q[0];", 2),
                                       ("u1(pi/3) q[0]; u2(pi/7,pi/2) q[1];", 2),
                                       ("u3(pi/3,pi/7,pi/2) q[0];", 2),
                                       ("ccx q[0],q[1],q[2];", 3),
                                       ("cswap q[0],q[1],q[2];", 3)])
def test_decomposition_preserves_full_operator_and_each_basis_input(body, n):
    text = source(body, n)
    result = importer()(text)
    circuit = CustomCircuit.model_validate(result["circuit"])
    original = qasm2.loads(text, custom_instructions=(qasm2.CustomInstruction("cswap", 0, 3, CSwapGate, builtin=True),))
    assert Operator(original).equiv(Operator(circuit.subject().native()))
    a, b = Operator(original).data, Operator(circuit.subject().native()).data
    phase = np.vdot(b.ravel(), a.ravel()) / (2**n)
    assert np.allclose(a, phase * b, atol=1e-10, rtol=0)
    assert result["provenance"]["basis_inputs_checked"] == 2**n
    assert result["provenance"]["transformations"]


@pytest.mark.parametrize("text,code", [(source("", 6), "qubit_limit"),
    (source("h q[0];" * 33), "transformed_gate_limit"),
    (source("u3(pi/3,pi/7,pi/2) q[0];" * 12), "transformed_gate_limit"),
    (source("//" + "x" * 65536), "source_size_limit"),
    (source("barrier q;" * 1025), "source_instruction_limit"),
    (source("rz(99) q[0];"), "angle_limit")], ids=["qubits", "raw-gates", "expanded-gates", "bytes", "statements", "angle"])
def test_resource_guards_reject_without_simplifying(text, code):
    run = importer()
    from qfault.qasm_import import QASMImportError
    with pytest.raises(QASMImportError) as caught:
        run(text)
    assert caught.value.code == code


def test_disjoint_source_order_is_preserved():
    result = importer()(source("x q[1]; h q[0]; z q[1]; s q[0];"))
    assert [(g["name"], g["qubits"]) for g in result["circuit"]["gates"]] == [
        ("x", [1]), ("h", [0]), ("z", [1]), ("s", [0])]


def test_controlled_phase_alias_and_standard_swap_remain_single_gates():
    result = importer()(source("cu1(pi/2) q[1],q[0]; swap q[0],q[1]; cp(pi/4) q[0],q[1];"))
    assert [g["name"] for g in result["circuit"]["gates"]] == ["cp", "swap", "cp"]
    assert result["provenance"]["operator_equivalent"]


def test_standard_include_accepts_legal_whitespace_and_comments():
    text = 'OPENQASM 2.0; include /* standard library */\n "qelib1.inc"; qreg q[2]; x q[0];'
    result = importer()(text)
    assert result["circuit"]["gates"][0]["name"] == "x"


def test_inventory_accounts_for_entire_pinned_tree_and_keeps_duplicate_scope_separate():
    import scripts
    assert (Path(scripts.__file__).parent / "external_corpus.py").exists(), "corpus inventory missing"
    from scripts.external_corpus import build_inventory
    inventory = build_inventory()
    entries = inventory["entries"]
    assert len(entries) == 252
    assert len({e["source_path"] for e in entries}) == 252
    assert all(e["reason"] for e in entries if e["status"] == "excluded")
    assert all(e["split"] is None for e in entries if e["variant"] == "transpiled_duplicate")
    eligible = sorted((e for e in entries if e["status"] == "eligible"), key=lambda e: e["source_path"])
    assert all(e["split"] == ("development" if i % 3 == 0 else "holdout") for i, e in enumerate(eligible))
    outside = [e for e in entries if e["reason_code"] == "qubit_limit"]
    assert outside and all(e["raw_depth"] is None and e["raw_gate_counts"] is None for e in outside)
