# Dense-target development finding — 2026-10-23

No new production witness policy is adopted. The matched development experiment
in [dense-target-development-v1.json](../benchmarks/dense-target-development-v1.json)
retains all 16 real Aer executions at the case level, including each group's
raw counts, shot allocation and evaluator fidelity. There is one architecture:
the existing two-qubit development `rotation_entangler` reference, clean and
with a terminal Z intervention, seeds 301/302, budgets 8,192/32,768 shots.
Repeated variants/seeds are not independent circuit families.

The tested bounded alternative allocates a fixed total across the same compatible
groups to minimize the conservative L1 uncertainty proxy
Σ_g w_g / √N_g, where w_g=Σ_{P in g}|a_P|/2^n. Lagrange multipliers give
N_g proportional to w_g^(2/3); the implementation clips at 64–10,000 shots per
job and rounds using exact discrete marginal improvements. Allocation depends
only on the declared target, never on the candidate state or evaluator truth.
Both schedules use one look per term and the same simultaneous error allocation.

At seed 301 on the clean development circuit, uniform/coefficient allocation
proxy radii are 0.1833/0.1591 at 8,192 shots and 0.0916/0.0795 at 32,768 shots.
The corresponding measured lower bounds are 0.8326/0.8453 and 0.9146/0.9284.
All 16 measured intervals cover the independently evolved evaluator fidelity.
Both schedules confirm 4/8 cases: smaller proxy width does not establish a
verified-yield benefit, broad superiority or a valid reason to replace the engine.

A separate target-only inspection of the already observed three-qubit dense
design (not a new untouched experiment) finds 49 nonidentity terms, 19
compatible groups and a nonstabilizer target. At 32,768 shots/40 evaluations,
the existing feasibility construction returns lower bound 0.7823152869 against
threshold 0.8, even when affordable measured means equal their target values.
The inspected fixed, coefficient and adaptive settings share that feasibility
construction. This is evidence that finite allocation, omitted/unmeasured mass
and conservative simultaneous bounds constrain confirmation; it is not a proof
no other valid schedule or estimator could succeed. More favorable plug-in
completion cannot be substituted into the rigorous criterion.

Reproduce the development experiment into a new file:

```powershell
python -m scripts.dense_target_study --out artifacts/my-dense-development.json
python -m pytest tests/test_witness_allocation.py -q
```

This study neither modifies the old holdout nor supplies independent performance
evidence for a revised production algorithm. Negative findings remain explicit.
