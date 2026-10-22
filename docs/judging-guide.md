# Demonstrating QFault

QFault helps a developer compare a small quantum circuit with independently
declared behavior, inspect measured disagreement, test permitted edits and
verify a selected edit using fresh measurements. It integrates those steps with
explicit budgets, abstentions and consistency-checkable exports. Gate-edit repair
and measured assertions have substantial prior work; no first-of-its-kind claim
is made.

Start the documented local server, then run:

```powershell
python -m scripts.judging_demo --out artifacts/my-native-demo
python -m qfault verify-report artifacts/my-native-demo/fresh_recovery-report.json
```

The script uses an actual native QuantumCircuit, not a stored success response.
Its development fixture is H(0), Z(0) on two qubits, seed 7241. The independent
reference behavior is |0⟩|+⟩. It retains every executed export and checks outcomes:

1. Z-only distribution: the phase defect is invisible. Explain that satisfying
   this inadequate contract does not establish circuit correctness.
2. Declare IX=+1 with tolerance 0.2: real complementary measurements detect
   disagreement. The contract was independently declared, not inferred from the
   faulty circuit.
3. Run bounded measured recovery: inspect candidate edits, overlaps and costs,
   selection order, fresh original/candidate evidence and the contract-scoped
   verdict. The original is preserved. An improving edit does not prove cause.
4. Readout-noise control: show why an edit is withheld.
5. Insufficient budget: show the explicit refusal before a search can be funded.
6. Verify the exported record independently, then demonstrate parent-linked
   replay. A new seed is a rerun, not identical replay or hardware independence.

For a real external source in the editor, use `scripts.external_demo` and
`scripts.external_demo_e2e`; provenance, exclusions and current raw evidence are
in [external validation](external-validation.md). For the new native fixture,
paste the circuit/contract returned by `scripts.judging_demo.example` into the
same editor. The [import guide](native-import.md) shows the conversion API.

Current external results are descriptive: conservative and point ranking both
verified 10/90 overall, 10/41 eligible; conservative rejected 8 versus 31 and
used fewer shots. Repeated seeds and nine small source programs do not establish
population superiority. All attempted cases, unsupported cases and negative
outcomes remain visible. The landing fetches these values from the recorded
summary; historical results are separately labelled.

This is local simulation with no provider charge; it consumes CPU, memory and
measured runtime/resources. No hardware validation, universal unitary verification,
unique causal localization or guaranteed competition outcome is claimed. No
specific competition/rules/eligibility were assumed and no submission was made.

Browser captures are evidence only when taken against the real server. Existing
raw silent footage is historical. A new narrated final video has not been
recorded; do not describe screenshots or raw footage as that deliverable.
