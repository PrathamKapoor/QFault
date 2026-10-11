# Local judging rehearsal

Start from the verified workspace using README.md commands. The built interface is served on http://127.0.0.1:8000/ by the localhost API. No credentials or network calls are needed. Browser interactions remain manually unverified; CLI and HTTP paths below were executed.

Run powershell -NoProfile -ExecutionPolicy Bypass -File scripts/local.ps1 qfault demo. The latest real output is benchmarks/demo.json; IDs resolve under artifacts/investigations.

- Healthy Bell: no significant failure evidence, 4,096 shots.
- Bell remove: logical defect; one-edit repair independently VERIFIED, 7,168 shots / 28 evaluations.
- Bell readout: noise-consistent degradation, 5,120 shots; no automatic circuit repair.
- GHZ mixed: mixed/ambiguous conclusion, 5,120 shots.
- QFT clean with fixed policy: passes the fixed-input contract checks.
- Bell phase with fixed policy: logical defect detected using the privileged simulator-state probe despite matching computational-basis probabilities; independently verified repair.
- Dedicated integrity control: original valid, modified counts invalid, restored original bytes valid.

In the UI choose Bell and Missing gate, run, inspect actual counts and diagnostic evidence, then inspect recovery verification and export JSON. Use Readout noise to show the noise control and GHZ/Mixed to show ambiguity. Review requires a name and reason and creates a self-declared local decision. The benchmark tab shows the measured comparison, including the fixed policy win and threshold tie at lower cost.

Explain the scientific boundary: all runs are simulated; contracts are fixed-input states; noise consistency is not unique causal proof; state probes are unavailable on hardware without additional measurements; the evidence policy has no demonstrated advantage. No result proves general unitary equivalence.

The latest HTTP rehearsal is benchmarks/http-smoke.json. Release tests, limitations and next engineering work are recorded in handoff.md.
