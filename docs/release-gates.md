# Verified release boundaries

Assessment: 2026-10-11. Status: PARTIALLY COMPLETE. Current evidence supplements the preserved original benchmarks; it does not retroactively change them.

| Gate | Status | Executed evidence / remaining limit |
|---|---|---|
| Fresh isolated Python installation | BLOCKED | LibreOffice venv launchers missing; official registry downloads denied; bridge remains |
| Fresh frontend installation / lockfile | BLOCKED | Offline metadata ENOTCACHED, online registry EACCES; no own node_modules or lockfile |
| Actual quantum core | PASS locally | Qiskit2.3.1 reference and Aer0.17.2 executed Bell/GHZ/QFT |
| Aer compatibility | PASS locally | Matching cp313 Windows x64 binary;8 tests;9 paired circuit/noise cases; saved densities agree |
| Core/API/CLI regression tests | PASS locally |94 passed,1 Starlette/httpx deprecation warning |
| TypeScript / production build | PASS with bridge | TypeScript6.0.3 and Vite8.2.2; own dependency installation still blocked |
| Browser E2E / responsive / console | BLOCKED | Browser discovery empty; no screenshots or E2E success claimed |
| Original benchmark reproducibility | PASS locally |75 cases/policy and6 selected repairs match, authoritative artifacts unchanged |
| Frozen new evaluation | PASS locally |68 cases/policy, five policies, equal ceilings; full metrics reproduced |
| Phase evidence / global phase | PASS within declared scope | Actual complementary counts; global-phase invariance; incomplete witnesses documented |
| Truth isolation | PASS for API boundary | Measured allowlist and poisoned phase metadata tests; no hostile-Python sandbox claim |
| Recovery | PASS for selected bounded cases |10/12 verified,2 inconclusive;2 negative controls rejected; fresh Z/phase validation |
| Clean false diagnosis | PASS for tested corpus |0/10 evaluator-correct cases/policy, Wilson upper27.8%; not zero population rate |
| Cost ceilings | PASS | Reservations and shot/execution consistency; basis-gate and exact-evaluation costs retained |
| Export / integrity | PASS relative to supplied manifest | Standalone verify-report; covered tampering fails; restoration passes; no signatures |
| Local demo and HTTP journey | PASS |Aer healthy/fault/noise/phase/abstention; export verified; production assets served |
| Scientific presentation | PARTIAL |Measured charts, bases, costs, negative findings in UI; browser presentation still unverified |
| Local authorship / attribution | Checked at delivery |Requested author/committer; notices retained; no donor code copied or remote push |
| QCEC / mitigation / ML-DSA / temporal / hardware | NOT IMPLEMENTED |Explicitly excluded from functional claims |

See docs/environment-stabilization.md for exact blockers, docs/diagnostic-findings.md for all confusion matrices and negative findings, and handoff.md for commands. No fresh installation, browser, winning result, scientific novelty or quantum-advantage claim is made.
