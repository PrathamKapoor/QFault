# Frozen small-benchmark protocol

Written before the first benchmark run. No policy tuning on reported results.

- Families: Bell (2), GHZ (3), QFT (3).
- Scenarios: clean, readout, gate, remove, replace, rewire, mixed, phase; QFT also angle.
- Seeds: 11, 29, 47. These are independent sampling replications of a small, fixed scenario corpus, not independent circuit families.
- Policies: evidence-triggered, fixed plan, random admissible, simple threshold.
- Each investigation: 2,048 baseline shots + 2,048 observation shots; 6,144-shot and 4-evaluation ceilings. Recovery disabled in policy comparison. No policy can exceed these ceilings. Unused budget is reported rather than charged fictitiously.
- Fixed plan always requests ideal-state analysis and a 1,024-shot readout probe. Evidence policy requests them on significant measurement disagreement. Threshold requests the ideal-state calculation when raw TV exceeds 0.10. Random chooses ideal-state or calibration when failure triggers, with the recorded seed.
- State analysis is a privileged simulator calculation, costing one circuit evaluation and zero shots. There is no hardware-compatible tomography claim.
- Primary outcomes: category confusion matrix, category accuracy, abstention, selective accuracy, logical-defect detection, clean false diagnosis, shots and evaluations.
- Truth: evaluator computes fixed-input infidelity after the prediction is frozen. Equivalent mutations are not assumed defective. Noise-only reference labels indicate configured degradation, even if a restricted measurement cannot observe it; this deliberately exposes observability limits.
- Recovery evaluation: separate Bell/GHZ missing-gate cases, same three seeds, 12,000-shot / 384-evaluation ceilings. Denominators include every selected faulty case. Report rejected/inconclusive proposals.
- Confidence: Wilson 95% intervals for event counts. Treat intervals as descriptive sampling uncertainty over this finite corpus; repeated seeds on the same circuit are clustered, so broad population inference is not justified.
- No performance or novelty superiority claim. All losing cases remain in the results.
