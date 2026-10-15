"""Bounded static OpenQASM 2 adapter; independent of the diagnostic engine.

Only qelib1.inc is accepted. No source definitions, dynamic operations or
interior measurements are interpreted. Each accepted gate is translated in
source order at optimization level zero; identity/cancellation passes are not
run. The returned circuit declares the canonical all-zero computational input.
"""
from collections import Counter
import hashlib
import math
import re

import numpy as np
from pydantic import ValidationError
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.circuit.library import CPhaseGate, CSwapGate, SwapGate
from qiskit.quantum_info import Operator

from .lab import CustomCircuit

MAX_SOURCE_BYTES = 65536
MAX_SOURCE_INSTRUCTIONS = 1024
MAX_TRANSFORMED_GATES = 32
BASIS = ("h", "x", "z", "s", "rx", "ry", "rz", "cx", "cz", "cp", "swap")
# Explicit standard-library vocabulary. Being in qelib1 is not sufficient.
STANDARD_GATES = frozenset(BASIS) | {"y", "t", "tdg", "sdg", "u1", "u2", "u3", "U", "CX",
                                      "cu1", "cu3", "crz", "ch", "cy", "ccx", "cswap"}


class QASMImportError(ValueError):
    def __init__(self, code, message, metadata=None):
        super().__init__(message)
        self.code = code
        self.metadata = metadata or {}


def _fail(code, message, metadata):
    raise QASMImportError(code, message, dict(metadata))


def _without_comments(text):
    return re.sub(r'"[^"\n]*"|//[^\n]*|/\*.*?\*/',
                  lambda m: m[0] if m[0].startswith('"') else " ", text, flags=re.S)


def _preflight(source):
    raw = source.encode("utf-8") if isinstance(source, str) else source
    if not isinstance(raw, bytes):
        raise TypeError("source must be str or bytes")
    meta = {"sha256": hashlib.sha256(raw).hexdigest(), "source_bytes": len(raw),
            "raw_n_qubits": None, "raw_depth": None, "raw_gate_counts": None,
            "raw_vocabulary": None, "has_measurements": None, "has_classical_control": None,
            "inspection_level": "bytes"}
    if len(raw) > MAX_SOURCE_BYTES:
        _fail("source_size_limit", f"source exceeds {MAX_SOURCE_BYTES} bytes", meta)
    try:
        clean = _without_comments(raw.decode("utf-8"))
    except UnicodeDecodeError:
        _fail("invalid_encoding", "source must be UTF-8", meta)
    declarations = re.findall(r"\bqreg\s+[A-Za-z_]\w*\s*\[\s*(\d+)\s*\]\s*;", clean)
    meta["raw_n_qubits"] = sum(map(int, declarations)) if declarations else None
    meta["inspection_level"] = "lexical"
    if meta["raw_n_qubits"] is None or not 2 <= meta["raw_n_qubits"] <= 5:
        _fail("qubit_limit", "declared qubit count must be between 2 and 5", meta)
    if sum(map(int, re.findall(r"\bcreg\s+\w+\s*\[\s*(\d+)\s*\]", clean))) > 32:
        _fail("classical_bit_limit", "at most 32 classical bits are accepted", meta)
    statements = [s.strip() for s in clean.split(";") if s.strip()]
    if len(statements) > MAX_SOURCE_INSTRUCTIONS:
        _fail("source_instruction_limit", f"source exceeds {MAX_SOURCE_INSTRUCTIONS} statements", meta)
    operations = []
    for statement in statements:
        token = re.match(r"[A-Za-z_]\w*", statement)
        if token and token[0] not in {"OPENQASM", "include", "qreg", "creg"}:
            operations.append(token[0])
    meta.update(raw_vocabulary=sorted(set(operations)),
                raw_gate_counts=dict(sorted(Counter(operations).items())),
                has_measurements="measure" in operations, has_classical_control="if" in operations)
    for pattern, code, message in [
        (r"\bgate\b", "custom_gate_definition", "custom gate definitions are unsupported"),
        (r"\bopaque\b", "opaque_definition", "opaque definitions are unsupported"),
        (r"\breset\b", "reset", "reset is unsupported"),
        (r"\bif\s*\(", "classical_control", "classical conditions are unsupported"),
        (r"\b(?:while|for|switch|delay|box|def|defcal)\b", "dynamic_operation", "dynamic operations are unsupported"),
    ]:
        if re.search(pattern, clean):
            _fail(code, message, meta)
    for statement in statements:
        if re.match(r"include\b", statement) and not re.fullmatch(r'include\s+"qelib1\.inc"', statement):
            _fail("arbitrary_include", "only built-in qelib1.inc is permitted", meta)
    unsupported = sorted(set(operations) - STANDARD_GATES - {"measure", "barrier"})
    if unsupported:
        _fail("unsupported_operation", "unsupported operations: " + ", ".join(unsupported), meta)
    seen_measurement = False
    for operation in operations:
        if operation == "measure":
            seen_measurement = True
        elif seen_measurement and operation != "barrier":
            _fail("interior_measurement", "unitary operations after any measurement are unsupported, including disjoint qubits", meta)
    return raw, clean, meta


def _parse(source):
    raw, clean, meta = _preflight(source)
    try:
        # Qiskit handles qelib1.inc internally; the empty include path blocks file lookup.
        parsed = qasm2.loads(clean, include_path=(), custom_instructions=(
            qasm2.CustomInstruction("cswap", 0, 3, CSwapGate, builtin=True),
            qasm2.CustomInstruction("swap", 0, 2, SwapGate, builtin=True),
            qasm2.CustomInstruction("cp", 1, 2, CPhaseGate, builtin=True)))
    except qasm2.QASM2ParseError as error:
        _fail("parse_error", str(error), meta)
    if len(parsed.data) > MAX_SOURCE_INSTRUCTIONS:
        _fail("expanded_instruction_limit", "register expansion exceeds instruction limit", meta)
    meta.update(inspection_level="parsed", raw_n_qubits=parsed.num_qubits,
                raw_depth=parsed.depth(), raw_gate_counts=dict(sorted(parsed.count_ops().items())),
                raw_vocabulary=sorted(parsed.count_ops()))
    return parsed, meta


def inspect_qasm2(source):
    """Return bounded source metadata, or an error carrying partial metadata."""
    _, metadata = _parse(source)
    return metadata


def import_qasm2(source, *, name="imported"):
    """Return CustomCircuit JSON and auditable transformation provenance.

    Full operators (all columns/basis inputs, with one common global phase) are
    compared before acceptance. This is an import check, not an expected-output
    oracle or evidence that a candidate meets an independent specification.
    """
    parsed, meta = _parse(source)
    original = QuantumCircuit(parsed.num_qubits)
    translated = QuantumCircuit(parsed.num_qubits)
    mappings, barriers, transformations = [], [], []
    for index, item in enumerate(parsed.data):
        operation = item.operation
        qubits = [parsed.find_bit(q).index for q in item.qubits]
        if operation.name == "measure":
            mappings.append({"qubit": qubits[0], "classical_bit": parsed.find_bit(item.clbits[0]).index})
            continue
        if operation.name == "barrier":
            barriers.append({"instruction_index": index, "qubits": qubits})
            continue
        original.append(operation, qubits)
        if operation.name == "cu1":
            part = QuantumCircuit(parsed.num_qubits)
            part.cp(float(operation.params[0]), *qubits)
            transformations.append({"kind": "standard_gate_alias", "instruction_index": index,
                                    "source_gate": "cu1", "output_gates": ["cp"]})
        elif operation.name in BASIS:
            part = QuantumCircuit(parsed.num_qubits)
            part.append(operation, qubits)
        else:
            part = QuantumCircuit(parsed.num_qubits)
            part.append(operation, qubits)
            try:
                part = transpile(part, basis_gates=list(BASIS), optimization_level=0,
                                 seed_transpiler=0)
            except Exception as error:
                _fail("translation_error", f"cannot translate {operation.name}: {error}", meta)
            transformations.append({"kind": "standard_gate_decomposition", "instruction_index": index,
                                    "source_gate": operation.name,
                                    "output_gates": [i.operation.name for i in part.data],
                                    "optimization_level": 0})
        if len(translated.data) + len(part.data) > MAX_TRANSFORMED_GATES:
            meta["transformed_gate_count_lower_bound"] = len(translated.data) + len(part.data)
            _fail("transformed_gate_limit", "translation exceeds 32 gates; no cancellation or simplification applied", meta)
        translated.compose(part, inplace=True)
    gates = []
    for item in translated.data:
        gate = {"name": item.operation.name,
                "qubits": [translated.find_bit(q).index for q in item.qubits], "angle": None}
        if item.operation.params:
            gate["angle"] = float(item.operation.params[0])
            if not math.isfinite(gate["angle"]) or abs(gate["angle"]) > 8 * math.pi:
                _fail("angle_limit", "translated angles must be finite and within +/-8 pi", meta)
        gates.append(gate)
    try:
        circuit = CustomCircuit.model_validate({"schema_version": 1, "name": name,
                   "n_qubits": parsed.num_qubits,
                   "input": {"kind": "computational_basis", "bitstring": "0" * parsed.num_qubits},
                   "gates": gates})
    except ValidationError as error:
        _fail("custom_circuit_validation", str(error), meta)
    # Compare the actual serialized QFAULT circuit, including float conversion.
    a, b = Operator(original).data, Operator(circuit.subject().native()).data
    phase = np.vdot(b.ravel(), a.ravel()) / (2**parsed.num_qubits)
    equivalent = bool(abs(abs(phase) - 1) < 1e-10 and np.allclose(a, phase * b, atol=1e-10, rtol=0))
    if not equivalent:
        _fail("operator_mismatch", "translated circuit does not preserve the complete operator up to one global phase", meta)
    if barriers:
        transformations.append({"kind": "strip_barriers", "count": len(barriers)})
    if mappings:
        transformations.append({"kind": "strip_terminal_measurements", "count": len(mappings)})
    return {"circuit": circuit.model_dump(mode="json"), "provenance": {
        **meta, "transformations": transformations, "measurement_mapping": mappings,
        "barriers_removed": barriers, "original_depth": parsed.depth(),
        "original_gate_counts": dict(sorted(parsed.count_ops().items())),
        "transformed_gate_count": len(gates), "transformed_depth": translated.depth(),
        "operator_equivalent": equivalent, "operator_tolerance": 1e-10,
        "basis_inputs_checked": 2**parsed.num_qubits,
        "global_phase_real_imag": [float(phase.real), float(phase.imag)],
        "canonical_input": "0" * parsed.num_qubits,
        "order_policy": "each source unitary translated individually in source order",
    }}
