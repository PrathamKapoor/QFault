# Bring a small circuit into QFault

The local Python converter accepts supported `QuantumCircuit` objects. It never
loads a user Python file or pickle through the API. Declare expected behavior
separately from the candidate; successful conversion is not a correctness verdict.

```python
from qiskit import QuantumCircuit
from qfault.qasm_import import from_qiskit
from qfault.lab import LabRequest, investigate_lab

candidate = QuantumCircuit(2)
candidate.h(0)
candidate.z(0)  # observable only with a phase-sensitive contract
circuit = from_qiskit(candidate, name="Phase test", input_bitstring="00")
request = LabRequest(circuit=circuit, backend="aer", contract={
    "kind": "pauli_expectations",
    "observables": [{"pauli": "IX", "expected": 1.0, "tolerance": 0.2}]
})
result = investigate_lab(request)
```

This explicitly declares the reference output |0⟩|+⟩. The converter never derives
that contract from the submitted candidate. Save `request.model_dump_json()` to
a file to use the CLI, or paste `circuit.model_dump_json()` into Custom Circuit →
Circuit JSON. The API/browser use the same validated request and engine.

```powershell
python -m qfault lab request.json --validate-only
python -m qfault lab request.json
python -m qfault measured-recovery recovery-request.json
python -m qfault export EXPERIMENT_ID report.json
python -m qfault verify-report report.json
```

For local OpenQASM2 files:

```powershell
python -m qfault import-qasm circuit.qasm --out circuit.json
```

Only built-in `qelib1.inc` is permitted; source definitions, external includes,
dynamic control, reset and interior measurements are rejected. Optional
`--strip-barriers`, `--strip-terminal-measurements` and `--allow-decomposition`
make transformations explicit. No cancellation/optimization pass runs. The
bounded adapter checks the converted full operator up to common global phase;
this import check does not validate the user's behavioral contract.

Native gates: H, X, Z, S, Rx, Ry, Rz, CX, CZ, CP and SWAP only, with finite real
angles in ±8π radians. Native conversion never decomposes custom instructions,
even if their name matches an allowed gate. Unsupported operations identify the
zero-based instruction index. Unbound parameters, dynamic control and reset are
rejected. Maximum: 2–5 qubits, 32 subject gates, 32 classical bits, 1,024 source
instructions. Measurements must be terminal across the whole circuit. Removal
of measurements/barriers is opt-in; global phase is recorded and does not affect
supported fixed-input state/distribution claims.

Qiskit order is retained: q0 is the rightmost bit/Pauli character; amplitude
index i names the binary basis string for i. The lab adds X preparation for
declared nonzero input bits exactly once. Do not also prepend those X gates
unless they are intended subject operations.

ImportProvenance version 1 records original instructions or QASM bytes,
measurement mappings, transformations, source representation SHA-256, Qiskit
version, options and converted structural identity. It survives request storage,
export and replay. Derived edits retain that original ancestry; they are not
claimed to equal the original imported gate list. Hashes are unsigned consistency
checks, not proof of authorship, authenticity or semantic correctness.

Same-seed API replay creates a new parent-linked record labelled
`deterministic_replay`. An explicit body `{"seed": 91234}` creates a
`new_seed_rerun` when that seed differs. Neither removes shared simulator bias.
