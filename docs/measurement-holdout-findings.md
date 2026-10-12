# Measurement-boundary holdout findings

Executed once from implementation commit `f7a832be853faa263280cc6fe08fddd2becc275f`, after protocol commit `3dbf423e9d9b133e57738e7ee65236a5a75aa744`. No diagnostic/recovery algorithm changed after these outcomes. Later error-redaction and evidence-transfer fixes do not change diagnosis. All 208 runs completed, with no execution errors; all raw investigation manifests were independently checked.

52 matched cases per policy: Bell2, GHZ3 and QFT3; two prespecified new seeds; clean, missing gate, phase, two readout levels, two depolarizing levels and mixed controls, plus two QFT angle settings. These are new parameter settings of known architectures, not unseen-architecture generalization. Frozen historical results are separate.

## Capability and cost comparison

| Policy | Strict category successes / 52 | Attribution abstentions / 52 | Supported discrepancy / 52 | Total shots | Additional shots beyond baseline + observation | Executions | Budgeted evaluations | Run-time sum (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| measurement_complementary | 16/52 | 20/52 | 30/52 | 372,736 | 159,744 | 208 | 208 | 3.913 |
| measurement_z | 16/52 | 8/52 | 14/52 | 266,240 | 53,248 | 156 | 156 | 3.161 |
| simulator_fixed | 32/52 | 0/52 | 14/52 | 266,240 | 53,248 | 156 | 208 | 4.230 |
| simulator_phase | 38/52 | 0/52 | 30/52 | 372,736 | 159,744 | 208 | 238 | 5.714 |

Strict success requires a non-abstaining prediction equal to evaluator category. A measurement-only MIXED_OR_AMBIGUOUS result counts as attribution abstention, even when that string matches evaluator truth. Simulator MIXED_OR_AMBIGUOUS is an attributed mixed category supported by privileged state calculations. Therefore the raw category-match and causal-abstention semantics must not be conflated.

Both measurement-only plans make zero exact faulty-state evaluations; recovery is disabled. Analytical reference expectations use only the declared target. The simulator policies can inspect exact candidate states; their results are not measurement-only performance. All shot totals include initial clean reference + hidden observation, complementary measurements and readout controls. One zero-shot state calculation still counts as a budgeted evaluation.

## Negative results and observability

Complementary measurements increased supported-discrepancy detections from 14/52 to 30/52 and logical-case discrepancy detection from 4/12 to 12/12. Strict measurement-only category successes stayed 16/52; abstentions increased from 8/52 to 20/52. Added evidence does not uniquely distinguish gate noise from logical faults. No measurement-only logical attribution or repair success is claimed.

Phase-assisted classification improved from 32/52 to 38/52 at 40% more shots than fixed. Both miss all six low-readout and six low-gate-noise labels; phase additionally calls two Bell mixed cases logical-only. The evaluator labels any configured nonzero noise, even where the evidence cannot establish it at the tolerance and shot budget. These label mismatches are not proof of detectable degradation.

The four QFT angle changes are evaluator-correct controls: the selected rotation acts on a known basis component and changes only an unobservable phase for this fixed input. Mutation identity is not itself a failure label. The ten evaluator-correct controls comprise six clean runs and those four angle controls. Each policy has 0/10 clean false diagnoses on these controls; this is not a zero population false-alarm guarantee.

Non-abstaining category mismatches, a derived descriptive measure distinct from clean false alarms, are 28/52 for measurement_z, 16/52 for measurement_complementary, 20/52 for simulator_fixed and 14/52 for simulator_phase. Some are missed sub-threshold noise, rather than false fault assertions. All failure case IDs and full rows are retained in the result file.

## Per-class recall and confusion matrices

Abbreviations: C = no significant failure; L = logical defect; N = noise-consistent degradation; A = mixed/ambiguous. Rows are evaluator classes, columns are raw predicted labels. Strict recall excludes attribution abstentions; therefore A/A in a measurement-only matrix is not a success.

### measurement_complementary

| Truth | C | L | N | A | Strict recall |
|---|---:|---:|---:|---:|---:|
| C | 10 | 0 | 0 | 0 | 10/10 |
| L | 0 | 0 | 0 | 12 | 0/12 |
| N | 12 | 0 | 6 | 6 | 6/24 |
| A | 0 | 0 | 4 | 2 | 0/6 |
### measurement_z

| Truth | C | L | N | A | Strict recall |
|---|---:|---:|---:|---:|---:|
| C | 10 | 0 | 0 | 0 | 10/10 |
| L | 8 | 0 | 0 | 4 | 0/12 |
| N | 16 | 0 | 6 | 2 | 6/24 |
| A | 0 | 0 | 4 | 2 | 0/6 |
### simulator_fixed

| Truth | C | L | N | A | Strict recall |
|---|---:|---:|---:|---:|---:|
| C | 10 | 0 | 0 | 0 | 10/10 |
| L | 0 | 12 | 0 | 0 | 12/12 |
| N | 18 | 0 | 6 | 0 | 6/24 |
| A | 0 | 2 | 0 | 4 | 4/6 |
### simulator_phase

| Truth | C | L | N | A | Strict recall |
|---|---:|---:|---:|---:|---:|
| C | 10 | 0 | 0 | 0 | 10/10 |
| L | 0 | 12 | 0 | 0 | 12/12 |
| N | 12 | 0 | 12 | 0 | 12/24 |
| A | 0 | 2 | 0 | 4 | 4/6 |

## Paired descriptive comparison

Fixed versus phase-assisted: both correct 32, phase-only correct 6, fixed-only correct 0, neither correct 14. Phase costs 106,496 additional shots. Measurement Z versus complementary: both strictly correct 16, neither 36, no strict success differences, with 106,496 extra shots for complementary. Complementary measurement versus phase-assisted uses equal shots; privileged attribution adds 22 category successes. This does not show free hardware-accessible information.

No inferential p-values or population intervals are claimed. Repeated circuits and seeds are correlated; the measured run-time sum and 25.692-second runner wall time include local machine conditions, not controlled hardware throughput. No seed replacement, failure removal or tuning occurred.

## Reproduce and inspect

Install from pyproject.toml and use `python -m scripts.measurement_holdout --out artifacts/new-measurement-holdout`. The destination must not exist. The committed protocol fixes all cases. Do not tune on this now-observed set and continue calling it untouched. `benchmarks/measurement-boundary-holdout-20261013.json` includes the frozen provenance, all 208 rows, confusion matrices, costs, failure IDs and descriptive pairs. Raw records remain under `artifacts/measurement-boundary-holdout-20261013/investigations`; the evidence collector now includes this separately named summary and validates its manifest_sha256 references.

Historical reproduction: 300 original rows, 340 final rows and 12 selected recovery trials match all scientific fields (floating tolerance 1e-12), excluding generated identity/path/digest/time/provenance fields. All 23 earlier benchmark summaries remain byte-identical. The 68-case phase result remains 66/68 versus fixed 58/68; shots and 10/12 recovery results are unchanged.
