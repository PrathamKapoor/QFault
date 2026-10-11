# Verified release boundaries

Assessment date: 2026-10-11. Implementation: d1f81b669808550a81eec4519cba4462469f71ed. Evidence: benchmarks/verification.json, benchmarks/results.json, benchmarks/demo.json and benchmarks/http-smoke.json.

| Gate | Status | Evidence / limit |
|---|---|---|
| Local executable demo | PASS in verified workspace | CLI demo and real HTTP workflow executed |
| Fresh installation | NOT VERIFIED | Runtime bridge required; offline isolated install not rehearsed |
| Actual quantum core | PASS | Qiskit 2.3.1 BasicSimulator and DensityMatrix/Kraus |
| Requested Aer scenario | UNAVAILABLE | cp311 binary incompatible with accessible cp313; explicit valid fallback |
| Contracts and negative repair | PASS within fixed-input scope | Analytic states, rejection and phase-observability tests |
| Evaluator-label exclusion | PASS for declared API boundary | Allowlist poisoning test; predictions frozen before truth |
| Separate clean/noisy/faulty evaluation | PASS | 75 cases per policy, confusion matrices, honest misses |
| Recovery | PASS for bounded selected cases | Six independently checked missing-gate repairs; no general success claim |
| Resource enforcement | PASS | Budget rejection, shot consistency, exact calculation ledger tests |
| Baseline comparison | PASS with negative finding | Fixed wins; threshold ties evidence with fewer shots |
| Reproducibility | PASS locally | Three runs match scientific metrics |
| Reporting/provenance | PASS locally | Row-level raw record paths/manifest digests; reports export actual evidence |
| Input/security scope | PASS for localhost template API | Bounded inputs; no arbitrary code uploads; secret-pattern scan clear |
| Integrity | PASS relative to intact manifest | Counts, malformed artifacts, review changes/deletion fail verification |
| Visual interaction/presentation QA | NOT VERIFIED in browser | Built interface and HTTP serving pass; browser unavailable |
| Optional QCEC/PQC/mitigation/temporal/hardware | UNAVAILABLE | Not advertised as implemented |

This is a working local product with explicit scientific limits, not a claim that every submission acceptance condition is satisfied. No first-place, scientific novelty, hardware or quantum-advantage result is claimed.
