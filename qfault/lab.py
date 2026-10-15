"""Custom circuit laboratory: validated circuits, declared contracts, budgeted evidence planning.

Conventions (single source of truth, verified against Qiskit in tests):
- Bitstrings and Pauli strings use Qiskit order: the LEFTMOST character acts on the HIGHEST
  qubit index; the rightmost character acts on qubit 0. "XZI" = X on q2, Z on q1, I on q0.
- The submitted circuit starts in the declared computational-basis input; preparation X gates
  are added by this module and are never part of the user's gate list.
- The expected behaviour is declared by the contract and is never derived from the candidate.
"""
import random
from dataclasses import dataclass
from math import log, pi, sqrt
from time import perf_counter
from typing import Annotated, Literal, Union
import numpy as np
from pydantic import Field, model_validator
from qiskit.quantum_info import Pauli, Statevector
from scipy.optimize import linprog
from .quantum import Strict, Gate, Circuit, Noise, execute, resources
from .diagnostics import ExecutionBudget, EvidenceCollector, tv_radius
from .evidence import digest, identifier, timestamp
from .target import (TargetStateContract, TARGET_POLICIES, CATALOG_VERSION, POLICY_VERSION, catalog,
                     bounds, decide, marginal_gains, fidelity)

PROB_SUM_TOLERANCE = 1e-6
CONTROL_TOLERANCE = 0.10


class _LabCircuit(Circuit):
    """Preparation + submitted gates + at most 2 basis gates per qubit."""
    gates: tuple[Gate, ...] = Field(max_length=48)


class ComputationalInput(Strict):
    kind: Literal["computational_basis"]
    bitstring: str = Field(pattern=r"^[01]{2,5}$")


class CustomCircuit(Strict):
    schema_version: Literal[1]
    name: str = Field(min_length=1, max_length=80)
    n_qubits: int = Field(ge=2, le=5, strict=True)
    input: ComputationalInput
    gates: tuple[Gate, ...] = Field(max_length=32)

    @model_validator(mode="after")
    def valid(self):
        if len(self.input.bitstring) != self.n_qubits:
            raise ValueError("input bitstring length must equal n_qubits")
        if any(max(g.qubits) >= self.n_qubits for g in self.gates):
            raise ValueError("qubit index outside circuit")
        if not self.name.isprintable():
            raise ValueError("name must be printable text")
        return self

    @property
    def circuit_id(self):
        """Structural identity of qubits, input and ordered gates (name excluded).

        sha256 over canonical JSON (sorted keys, shortest-repr IEEE-754 angles). Not an
        equivalence proof: different gate lists may implement the same unitary.
        """
        body = {"n_qubits": self.n_qubits, "input": self.input.model_dump(),
                "gates": [g.model_dump(mode="json") for g in self.gates]}
        return "custom_" + digest(body)[:20]

    def preparation(self):
        bits = self.input.bitstring[::-1]  # bits[q] is the input of qubit q
        return tuple(Gate(name="x", qubits=(q,)) for q in range(self.n_qubits) if bits[q] == "1")

    def subject(self):
        return _LabCircuit(n_qubits=self.n_qubits, gates=self.preparation() + self.gates)


class PauliObservable(Strict):
    pauli: str = Field(pattern=r"^[IXYZ]{2,5}$")
    expected: float = Field(ge=-1, le=1)
    tolerance: float = Field(gt=0, le=1)


class PauliContract(Strict):
    kind: Literal["pauli_expectations"]
    environment: Literal["ideal"] = "ideal"
    observables: tuple[PauliObservable, ...] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def valid(self):
        labels = [o.pauli for o in self.observables]
        if len(set(labels)) != len(labels):
            raise ValueError("duplicate Pauli observable")
        if len({len(x) for x in labels}) != 1:
            raise ValueError("observables must all have the same length")
        if any(set(x) == {"I"} for x in labels):
            raise ValueError("the identity observable is always +1 and is not a measurable claim")
        _check_consistency(self.observables)
        return self


class DistributionContract(Strict):
    kind: Literal["measurement_distribution"]
    environment: Literal["ideal"] = "ideal"
    basis: Literal["X", "Y", "Z"] = "Z"
    expected_probabilities: dict[str, float] = Field(min_length=1, max_length=32)
    tolerance: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def valid(self):
        keys = list(self.expected_probabilities)
        if len({len(k) for k in keys}) != 1 or any(set(k) - {"0", "1"} for k in keys):
            raise ValueError("outcome keys must be equal-length bitstrings")
        if not 2 <= len(keys[0]) <= 5:
            raise ValueError("outcome keys must have 2-5 bits")
        values = list(self.expected_probabilities.values())
        if any(v < 0 or v > 1 for v in values):
            raise ValueError("probabilities must lie in [0,1]")
        if abs(sum(values) - 1) > PROB_SUM_TOLERANCE:
            raise ValueError(f"probabilities must sum to 1 within {PROB_SUM_TOLERANCE}; they are not normalized silently")
        return self


Contract = Annotated[Union[PauliContract, DistributionContract, TargetStateContract], Field(discriminator="kind")]


def _interval(o):
    return max(-1., o.expected - o.tolerance), min(1., o.expected + o.tolerance)


def _check_consistency(observables):
    """Reject contracts no quantum state can satisfy (pairwise necessary conditions)."""
    for i, a in enumerate(observables):
        for b in observables[i + 1:]:
            pa, pb = Pauli(a.pauli), Pauli(b.pauli)
            la = max(0., abs(a.expected) - a.tolerance)
            lb = max(0., abs(b.expected) - b.tolerance)
            if not pa.commutes(pb):
                if la ** 2 + lb ** 2 > 1 + 1e-12:  # <A>^2 + <B>^2 <= 1 for anticommuting Paulis
                    raise ValueError(f"contradictory claims: {a.pauli} and {b.pauli} anticommute and cannot both be near their expectations")
                continue
            product = pa.to_matrix() @ pb.to_matrix()
            for c in observables:
                m = Pauli(c.pauli).to_matrix()
                s = float(np.real(np.trace(product @ m)) / m.shape[0])
                if abs(abs(s) - 1) > 1e-9:
                    continue
                (alo, ahi), (blo, bhi), (clo, chi) = _interval(a), _interval(b), _interval(c)
                clo, chi = (clo, chi) if s > 0 else (-chi, -clo)  # E[ab] = s * <C>
                # variables xa, xb, xc=E[ab]; correlation polytope: |xa+xb|<=1+xc, |xa-xb|<=1-xc
                A = [[1, 1, -1], [-1, -1, -1], [1, -1, 1], [-1, 1, 1]]
                res = linprog(c=[0, 0, 0], A_ub=A, b_ub=[1, 1, 1, 1],
                              bounds=[(alo, ahi), (blo, bhi), (clo, chi)], method="highs")
                if res.status == 2:
                    raise ValueError(f"contradictory claims among {a.pauli}, {b.pauli}, {c.pauli}")


def check_pair(circuit, contract):
    n = circuit.n_qubits
    if isinstance(contract, PauliContract):
        if len(contract.observables[0].pauli) != n:
            raise ValueError("Pauli observable length must equal n_qubits")
    elif isinstance(contract, TargetStateContract):
        if contract.n_qubits != n:
            raise ValueError("target amplitude count must equal 2**n_qubits")
    elif len(next(iter(contract.expected_probabilities))) != n:
        raise ValueError("outcome key length must equal n_qubits")


def _setting_for(pauli, n):
    return "".join(c for c in pauli)  # same Qiskit order; I means unconstrained


def group_paulis(labels):
    """Greedy qubit-wise-commuting grouping in the given order. Returns [(pattern, [labels])]."""
    groups = []
    for need in labels:
        for g in groups:
            if all(a == "*" or b == "I" or a == b for a, b in zip(g[0], need)):
                g[0] = "".join(b if a == "*" and b != "I" else a for a, b in zip(g[0], need))
                g[1].append(need)
                break
        else:
            groups.append(["".join("*" if c == "I" else c for c in need), [need]])
    return groups


def plan(n, contract):
    """Claims and qubit-wise-commuting measurement groups (greedy, declared order)."""
    claims, groups = [], []
    if isinstance(contract, TargetStateContract):
        cat = catalog(contract.amplitudes)
        claims.append({"claim_id": "target:fidelity", "kind": "target_fidelity", "threshold": contract.threshold,
                       "tolerance": contract.fidelity_tolerance})
        groups = [{"pattern": pat, "claims": [], "terms": members} for pat, members in group_paulis([t for t, _ in cat["terms"]])]
    elif isinstance(contract, PauliContract):
        for o in contract.observables:
            claims.append({"claim_id": "obs:" + o.pauli, "kind": "pauli_expectation", "pauli": o.pauli,
                           "expected": o.expected, "tolerance": o.tolerance})
        groups = [{"pattern": pat, "claims": ["obs:" + m for m in members]}
                  for pat, members in group_paulis([_setting_for(o.pauli, n) for o in contract.observables])]
    else:
        claims.append({"claim_id": "dist:" + contract.basis, "kind": "distribution", "basis": contract.basis,
                       "tolerance": contract.tolerance})
        groups.append({"pattern": contract.basis * n, "claims": [claims[0]["claim_id"]]})
    for i, g in enumerate(groups):
        g["setting"] = g.pop("pattern").replace("*", "Z")
        g["group_id"] = f"group{i}:{g['setting']}"
        g["basis_gates"] = sum({"X": 1, "Y": 2, "Z": 0}[c] for c in g["setting"])
    return claims, groups


def alpha_slot(n_claims, looks, alpha_total):
    """Union bound over every interval the procedure may compute: claims x looks, plus one control."""
    return alpha_total / (n_claims * looks + 1)


def feasibility(circuit, contract, request):
    if isinstance(contract, TargetStateContract):
        return target_feasibility(contract, request)
    claims, groups = plan(circuit.n_qubits, contract)
    slot = alpha_slot(len(claims), request.max_looks, request.alpha_total)
    claim_shots = request.max_shots - request.batch_shots
    looks_afforded = max(0, min(request.max_looks, claim_shots // request.batch_shots))
    out = []
    for c in claims:
        n = looks_afforded * request.batch_shots
        if c["kind"] == "pauli_expectation":
            radius = hoeffding_radius(n, slot) if n else None
        else:
            radius = tv_radius(n, 2 ** circuit.n_qubits, slot) if n else None
        out.append({**c, "supported": True, "best_case_radius": radius,
                    "confirmable_within_tolerance": bool(radius is not None and radius < c["tolerance"]),
                    "note": None if radius is not None and radius < c["tolerance"] else
                    "Budget cannot confirm this claim inside its tolerance; only a large violation could be detected."})
    return {"claims": out, "groups": groups, "alpha_per_interval": slot, "alpha_total": request.alpha_total,
            "claim_shots_available": claim_shots, "reserved_control_shots": request.batch_shots,
            "limitations": ["A satisfied declared claim does not establish circuit correctness",
                            "Z-basis distributions are blind to relative phase",
                            "Violations do not identify a faulty gate or distinguish logic from noise"]}


def hoeffding_radius(n, alpha):
    """Two-sided Hoeffding radius for the mean of n i.i.d. +-1 outcomes."""
    return sqrt(2 * log(2 / alpha) / n)


class LabRequest(Strict):
    circuit: CustomCircuit
    contract: Contract
    diagnostic_mode: Literal["measurement_only", "simulator_assisted"] = "measurement_only"
    policy: Literal["adaptive", "fixed", "random", "complementary_schedule", "adaptive_witness",
                    "coefficient_weighted"] = "adaptive"
    backend: Literal["reference", "aer"] = "reference"
    environment: Noise = Noise()
    batch_shots: int = Field(default=1024, ge=64, le=10000, strict=True)
    max_shots: int = Field(default=8192, ge=128, le=100000, strict=True)
    max_evaluations: int = Field(default=24, ge=2, le=100, strict=True)
    max_looks: int = Field(default=4, ge=1, le=8, strict=True)
    alpha_total: float = Field(default=0.01, gt=1e-6, le=0.1)
    seed: int = Field(default=42, ge=0, lt=2 ** 32, strict=True)

    @model_validator(mode="before")
    @classmethod
    def default_policy(cls, data):
        if isinstance(data, dict) and "policy" not in data:
            kind = data.get("contract", {}).get("kind") if isinstance(data.get("contract"), dict) else None
            if kind == "target_state":
                data = {**data, "policy": "adaptive_witness"}
        return data

    @model_validator(mode="after")
    def valid(self):
        check_pair(self.circuit, self.contract)
        target = isinstance(self.contract, TargetStateContract)
        if target and self.policy not in TARGET_POLICIES:
            raise ValueError(f"target_state contracts support policies {TARGET_POLICIES}")
        if not target and self.policy in {"adaptive_witness", "coefficient_weighted"}:
            raise ValueError("witness policies require a target_state contract")
        if self.max_shots < 2 * self.batch_shots:
            raise ValueError("budget must fund one claim batch and one reserved control batch")
        return self


@dataclass(frozen=True)
class PolicyConfig:
    """Analyst settings only; excludes the candidate, executor and noise model."""
    policy: str
    batch_shots: int
    max_shots: int
    max_evaluations: int
    max_looks: int
    alpha_total: float
    seed: int

    @classmethod
    def from_request(cls, request):
        return cls(**{name: getattr(request, name) for name in cls.__dataclass_fields__})


def exact_expectations(circuit, contract):
    """PRIVILEGED simulator operation: exact ideal values of the declared claims."""
    state = Statevector.from_instruction(circuit.subject().native())
    n = circuit.n_qubits
    if isinstance(contract, TargetStateContract):
        return {"target:fidelity": fidelity(contract.vector(), state)}
    if isinstance(contract, PauliContract):
        return {"obs:" + o.pauli: float(np.real(state.expectation_value(Pauli(o.pauli)))) for o in contract.observables}
    rotated = state.evolve(basis_rotation(contract.basis * n, n).native())
    probs = rotated.probabilities_dict()
    full = {format(i, f"0{n}b"): float(probs.get(format(i, f"0{n}b"), 0.)) for i in range(2 ** n)}
    expected = contract.expected_probabilities
    tv = .5 * sum(abs(full[k] - expected.get(k, 0.)) for k in full)
    return {"dist:" + contract.basis: tv}


def basis_rotation(setting, n):
    """Gates mapping each measured Pauli basis onto Z. Y uses rz(-pi/2) = S^dagger up to global phase."""
    gates = []
    for q in range(n):
        letter = setting[n - 1 - q]
        if letter == "Y":
            gates.append(Gate(name="rz", qubits=(q,), angle=-pi / 2))
        if letter in "XY":
            gates.append(Gate(name="h", qubits=(q,)))
    return _LabCircuit(n_qubits=n, gates=tuple(gates))


def measurement_circuit(subject, setting):
    n = subject.n_qubits
    return _LabCircuit(n_qubits=n, gates=subject.gates + basis_rotation(setting, n).gates)


def parity_expectation(counts, shots, pauli):
    n = len(pauli)
    support = [n - 1 - q for q in range(n) if pauli[n - 1 - q] != "I"]
    plus = sum(c for k, c in counts.items() if sum(k[i] == "1" for i in support) % 2 == 0)
    return (2 * plus - shots) / shots


class _State:
    """Cumulative evidence for one claim, evaluated only on the prespecified shot grid."""
    def __init__(self, claim, n, expected_probs=None):
        self.claim, self.n, self.expected_probs = claim, n, expected_probs
        self.shots, self.counts, self.looks = 0, {}, 0
        self.status, self.estimate, self.radius = "UNRESOLVED", None, None

    def add(self, counts, shots, slot):
        for k, v in counts.items():
            self.counts[k] = self.counts.get(k, 0) + v
        self.shots += shots
        self.looks += 1
        c = self.claim
        if c["kind"] == "pauli_expectation":
            self.estimate = parity_expectation(self.counts, self.shots, c["pauli"])
            self.radius = hoeffding_radius(self.shots, slot)
            dist = abs(self.estimate - c["expected"])
        else:
            keys = {format(i, f"0{self.n}b") for i in range(2 ** self.n)}
            self.estimate = .5 * sum(abs(self.counts.get(k, 0) / self.shots - self.expected_probs.get(k, 0.)) for k in keys)
            self.radius = tv_radius(self.shots, 2 ** self.n, slot)
            dist = self.estimate
        tol = c["tolerance"]
        if dist - self.radius > tol:
            self.status = "VIOLATED"
        elif dist + self.radius <= tol:
            self.status = "SATISFIED_WITHIN_TOLERANCE"
        else:
            self.status = "UNRESOLVED"

    @property
    def resolved(self):
        return self.status != "UNRESOLVED"

    def report(self):
        return {**self.claim, "status": self.status, "estimate": self.estimate, "uncertainty_radius": self.radius,
                "shots": self.shots, "looks": self.looks,
                "interval": None if self.radius is None else [self.estimate - self.radius, self.estimate + self.radius]}


def run_policy(claims, groups, n, expected_probs, port, request):
    """Select and run measurements. Receives only a measurement port: no circuit, noise or state."""
    slot = alpha_slot(len(claims), request.max_looks, request.alpha_total)
    states = {c["claim_id"]: _State(c, n, expected_probs) for c in claims}
    looks = {g["group_id"]: 0 for g in groups}
    cap_shots = request.max_shots - request.batch_shots
    cap_evals = request.max_evaluations - 1
    rng = random.Random(request.seed ^ 0xA11CE)
    order = list(groups)
    if request.policy == "complementary_schedule":
        order.sort(key=lambda g: sum(c != "Z" for c in g["setting"]))
    ledger, stop = [], None
    while True:
        unresolved = [s for s in states.values() if not s.resolved]
        if not unresolved:
            stop = ("ALL_CLAIMS_RESOLVED", "Every declared claim is either violated or confirmed within tolerance at the corrected error level."); break
        open_groups = [g for g in order if looks[g["group_id"]] < request.max_looks]
        if request.policy == "adaptive":
            cover = {g["group_id"]: sum(not states[c].resolved for c in g["claims"]) for g in open_groups}
            open_groups = [g for g in open_groups if cover[g["group_id"]] > 0]
        if not open_groups:
            stop = ("LOOK_LIMIT_REACHED", "Every group that covers an unresolved claim has used its prespecified looks."); break
        if port.used_shots + request.batch_shots > cap_shots:
            stop = ("SHOT_BUDGET_EXHAUSTED", "Remaining shots (after the reserved control batch) cannot fund another batch; not scientific certainty."); break
        if port.used_evaluations + 1 > cap_evals:
            stop = ("EVALUATION_BUDGET_EXHAUSTED", "No circuit evaluation remains after the reserved control."); break
        if request.policy == "adaptive":
            pick = max(open_groups, key=lambda g: (cover[g["group_id"]], -g["basis_gates"], [-ord(c) for c in g["group_id"]]))
            reason = (f"Covers {cover[pick['group_id']]} unresolved claim(s): "
                      + ", ".join(c for c in pick["claims"] if not states[c].resolved)
                      + "; ties break toward fewer basis gates. Resolved claims are not re-measured.")
        elif request.policy == "random":
            pick = rng.choice(open_groups)
            reason = "Uniform random choice among groups with remaining looks, independent of evidence."
        else:
            pick = min(open_groups, key=lambda g: looks[g["group_id"]])
            reason = ("Predetermined round-robin in declared order." if request.policy == "fixed" else
                      "Predetermined round-robin, fewest non-Z basis letters first.") + " Independent of evidence."
        evidence = port.measure(pick["setting"], request.batch_shots, "claims:" + pick["group_id"])
        looks[pick["group_id"]] += 1
        for cid in pick["claims"]:
            states[cid].add(evidence["counts"], evidence["shots"], slot)
        ledger.append({"action_id": f"action{len(ledger)}", "execution_id": evidence["execution_id"],
                       "measurement_specification": {"group_id": pick["group_id"], "setting": pick["setting"],
                                                      "claims": pick["claims"], "look": looks[pick["group_id"]]},
                       "reason_selected": reason, "selection_policy": request.policy,
                       "shots_requested": request.batch_shots, "shots_executed": evidence["shots"],
                       "circuit_evaluations": 1, "basis_gates": pick["basis_gates"],
                       "execution_backend": evidence["backend"],
                       "observed_result": {c: {"status": states[c].status, "estimate": states[c].estimate} for c in pick["claims"]},
                       "uncertainty": {c: states[c].radius for c in pick["claims"]},
                       "remaining_budget": {"shots": request.max_shots - port.used_shots,
                                            "evaluations": request.max_evaluations - port.used_evaluations}})
    return states, ledger, stop, slot


class _Port:
    """Measurement capability. Holds the subject and environment privately; exposes only counts."""
    def __init__(self, subject, noise, budget, backend, seed, records):
        self._subject, self._noise, self._backend, self._seed = subject, noise, backend, seed
        self._budget, self._records = budget, records
        self._calls = 0

    @property
    def used_shots(self):
        return self._budget.shots

    @property
    def used_evaluations(self):
        return self._budget.evaluations

    def measure(self, setting, shots, label):
        circuit = Circuit(n_qubits=self._subject.n_qubits, gates=()) if setting is None else \
            measurement_circuit(self._subject, setting)
        self._budget.reserve(shots, label, resources(circuit))
        seed = (self._seed + 1000 + 7919 * self._calls) % 2 ** 32
        self._calls += 1
        record = execute(circuit, self._noise, shots, seed, backend=self._backend)
        record.update(measurement_setting=setting or "readout_control", lab_label=label)
        self._records.append(record)
        evidence = EvidenceCollector.collect(record, circuit.n_qubits)
        return {"counts": evidence.counts, "shots": evidence.shots, "execution_id": evidence.execution_id, "seed": seed,
                "backend": record["backend_name"]}


def _target_groups(contract, policy):
    cat = catalog(contract.amplitudes)
    _, groups = plan(cat["n"], contract)
    weight = dict(cat["terms"])
    for g in groups:
        g["coefficient_mass"] = sum(abs(weight[t]) for t in g["terms"])
    order = list(groups)
    if policy == "coefficient_weighted":
        order.sort(key=lambda g: -g["coefficient_mass"])
    elif policy == "complementary_schedule":
        order.sort(key=lambda g: sum(c != "Z" for c in g["setting"]))
    return cat, groups, order


def target_feasibility(contract, request):
    cat, groups, order = _target_groups(contract, "coefficient_weighted")
    slot = alpha_slot(len(cat["terms"]), request.max_looks, request.alpha_total)
    claim_shots = request.max_shots - request.batch_shots
    affordable = max(0, min(claim_shots // request.batch_shots, request.max_evaluations - 1))
    looks = {g["group_id"]: 0 for g in groups}
    for _ in range(affordable):  # best case: round robin, heaviest groups first, all estimates at target
        open_ = [g for g in order if looks[g["group_id"]] < request.max_looks]
        if not open_:
            break
        looks[min(open_, key=lambda g: looks[g["group_id"]])["group_id"]] += 1
    target = dict(cat["terms"])
    est, rad = {}, {}
    for g in groups:
        if looks[g["group_id"]]:
            for t in g["terms"]:
                est[t], rad[t] = target[t], hoeffding_radius(looks[g["group_id"]] * request.batch_shots, slot)
    L, U = bounds(cat, est, rad)
    ok = L >= contract.threshold
    return {"claims": [{"claim_id": "target:fidelity", "kind": "target_fidelity", "threshold": contract.threshold,
                        "tolerance": contract.fidelity_tolerance, "supported": True, "best_case_lower": L,
                        "best_case_radius": None, "confirmable_within_tolerance": ok,
                        "note": None if ok else "Even if every affordable witness matched the target exactly, the "
                        "measured lower bound could not reach the threshold; only violations are detectable."}],
            "groups": groups, "alpha_per_interval": slot, "alpha_total": request.alpha_total,
            "claim_shots_available": claim_shots, "reserved_control_shots": request.batch_shots,
            "catalog": {"version": CATALOG_VERSION, "terms": len(cat["terms"]), "groups": len(groups),
                        "stabilizer_target": cat["stabilizer"], "omitted_terms": cat["omitted_count"],
                        "omitted_abs_bound": cat["omitted_abs_bound"], "looks_affordable": affordable},
            "limitations": ["Measured witnesses bound fidelity; they do not certify the state unless the lower bound clears the threshold",
                            "Fidelity bounds require calibrated Pauli measurements of one common state and i.i.d. shots; basis-dependent noise need not define such a state",
                            "Violations do not identify a faulty gate or distinguish logic from noise",
                            "One declared input state only; not unitary equivalence"]}


class _FidelityClaim:
    def __init__(self, contract):
        self.claim = {"claim_id": "target:fidelity", "kind": "target_fidelity", "threshold": contract.threshold,
                      "tolerance": contract.fidelity_tolerance}
        self.status, self.lower, self.upper, self.shots, self.looks = "UNRESOLVED", 0., 1., 0, 0
        self.terms_measured, self.terms_total = 0, 0

    @property
    def resolved(self):
        return self.status != "UNRESOLVED"

    def report(self):
        return {**self.claim, "status": self.status, "estimate": None, "uncertainty_radius": None,
                "interval": [self.lower, self.upper], "lower": self.lower, "upper": self.upper,
                "shots": self.shots, "looks": self.looks, "terms_measured": self.terms_measured,
                "terms_total": self.terms_total, "evidence_label": "MEASUREMENT_DERIVED_WITNESS"}


def run_witness_policy(contract, contract_id, port, request):
    """Select witness groups for a target-state claim. Receives the target and a measurement port only."""
    from .target import point_estimate
    cat, groups, order = _target_groups(contract, request.policy)
    thr, b = contract.threshold, request.batch_shots
    slot = alpha_slot(len(cat["terms"]), request.max_looks, request.alpha_total)
    counts = {g["group_id"]: {} for g in groups}
    shots = {g["group_id"]: 0 for g in groups}
    looks = {g["group_id"]: 0 for g in groups}
    est, rad = {}, {}
    claim = _FidelityClaim(contract); claim.terms_total = len(cat["terms"])
    cap_shots, cap_evals = request.max_shots - b, request.max_evaluations - 1
    rng = random.Random(request.seed ^ 0xA11CE)
    ledger, stop = [], None
    while True:
        claim.lower, claim.upper = bounds(cat, est, rad)
        claim.status = decide(claim.lower, claim.upper, thr)
        if claim.resolved:
            stop = ("ALL_CLAIMS_RESOLVED", "The measured fidelity bound cleared or fell below the threshold at the corrected error level."); break
        open_groups = [g for g in order if looks[g["group_id"]] < request.max_looks]
        if not open_groups:
            stop = ("LOOK_LIMIT_REACHED", "Every witness group has used its prespecified looks."); break
        if port.used_shots + b > cap_shots:
            stop = ("SHOT_BUDGET_EXHAUSTED", "Remaining shots (after the reserved control batch) cannot fund another batch; not scientific certainty."); break
        if port.used_evaluations + 1 > cap_evals:
            stop = ("EVALUATION_BUDGET_EXHAUSTED", "No circuit evaluation remains after the reserved control."); break
        if request.policy == "adaptive_witness":
            radii = [hoeffding_radius(shots[g["group_id"]] + b, slot) for g in open_groups]
            gains, direction = marginal_gains(cat, est, rad, [g["terms"] for g in open_groups], radii, thr)
            scored = [((p, q, -g["basis_gates"], -i), g, p, q) for i, (g, (p, q)) in enumerate(zip(open_groups, gains))]
            key, pick, primary, secondary = max(scored, key=lambda s: s[0])
            if primary <= 1e-12 and secondary <= 1e-12:
                stop = ("NO_INFORMATIVE_ACTION", "No admissible witness is projected to tighten the decision-relevant bound."); break
            reason = (f"Plug-in fidelity {point_estimate(cat, est):.3f} vs threshold {thr:.3f}: aiming to {direction}. "
                      f"Projected bound improvement {primary:.4f} (other side {secondary:.4f}) over {len(open_groups)} open group(s); "
                      "heuristic proxy, not information gain.")
        elif request.policy == "random":
            pick = rng.choice(open_groups)
            reason = "Uniform random choice among groups with remaining looks, independent of evidence."
        else:
            pick = min(open_groups, key=lambda g: looks[g["group_id"]])
            reason = {"fixed": "Predetermined round-robin in catalog order.",
                      "coefficient_weighted": "Predetermined round-robin, largest target coefficient mass first.",
                      "complementary_schedule": "Predetermined round-robin, fewest non-Z basis letters first."}[request.policy] + " Independent of evidence."
        gid = pick["group_id"]
        ev = port.measure(pick["setting"], b, "witness:" + gid)
        looks[gid] += 1
        shots[gid] += ev["shots"]
        for k, v in ev["counts"].items():
            counts[gid][k] = counts[gid].get(k, 0) + v
        for t in pick["terms"]:
            est[t] = parity_expectation(counts[gid], shots[gid], t)
            rad[t] = hoeffding_radius(shots[gid], slot)
        claim.shots += ev["shots"]; claim.looks += 1; claim.terms_measured = len(est)
        L, U = bounds(cat, est, rad)
        target = dict(cat["terms"])
        ledger.append({"action_id": f"action{len(ledger)}", "execution_id": ev["execution_id"], "seed": ev["seed"],
                       "target_contract_id": contract_id,
                       "measurement_specification": {"group_id": gid, "setting": pick["setting"], "claims": ["target:fidelity"],
                                                      "pauli_terms": pick["terms"], "look": looks[gid]},
                       "reason_selected": reason, "selection_policy": request.policy, "policy_version": POLICY_VERSION,
                       "shots_requested": b, "shots_executed": ev["shots"], "circuit_evaluations": 1,
                       "basis_gates": pick["basis_gates"], "execution_backend": ev["backend"],
                       "derived_expectations": {t: {"estimate": est[t], "radius": rad[t], "target": target[t]} for t in pick["terms"]},
                       "observed_result": {"target:fidelity": {"status": decide(L, U, thr), "estimate": None, "bounds": [L, U]}},
                       "uncertainty": {"target:fidelity": (U - L) / 2},
                       "remaining_budget": {"shots": request.max_shots - port.used_shots,
                                            "evaluations": request.max_evaluations - port.used_evaluations}})
    discrepancies = [{"pauli": t, "estimate": est[t], "radius": rad[t], "target": a}
                     for t, a in cat["terms"] if t in est and abs(est[t] - a) - rad[t] > 0]
    evidence = {"label": "MEASUREMENT_DERIVED_WITNESS", "fidelity_bound": [claim.lower, claim.upper],
                "threshold": thr, "status": claim.status, "catalog_version": CATALOG_VERSION,
                "terms_measured": len(est), "terms_total": len(cat["terms"]), "stabilizer_target": cat["stabilizer"],
                "unmeasured_terms": [t for t, _ in cat["terms"] if t not in est][:64],
                "witness_discrepancies": discrepancies,
                "witness_discrepancy_note": "A measured Pauli term outside its interval departs from the ideal target; the "
                                            "fidelity tolerance may still permit it. Only the bound decides the contract.",
                "bound_method": "intersection of Pauli-expansion (|b|<=1 and purity Cauchy-Schwarz), stabilizer-projector "
                                "(stabilizer targets) and Fuchs-van de Graaf bounds; simultaneous on the union-bound coverage event"}
    return {"target:fidelity": claim}, ledger, stop, slot, evidence


def investigate_lab(request, truth=None):
    start = perf_counter()
    circuit, contract = request.circuit, request.contract
    n = circuit.n_qubits
    subject = circuit.subject()
    feas = feasibility(circuit, contract, request)
    claims, groups = plan(n, contract)
    expected = contract.expected_probabilities if isinstance(contract, DistributionContract) else None
    budget = ExecutionBudget(request.max_shots, request.max_evaluations)
    records = []
    port = _Port(subject, request.environment, budget, request.backend, request.seed, records)
    contract_id = "contract_" + digest(request.contract.model_dump(mode="json"))[:20]
    is_target = isinstance(contract, TargetStateContract)
    target_evidence = None
    policy_config = PolicyConfig.from_request(request)
    if is_target:
        states, ledger, stop, slot, target_evidence = run_witness_policy(contract, contract_id, port, policy_config)
        uncalibrated = bool(request.environment.readout or request.environment.depolarizing)
        target_evidence['model_validity'] = 'CALIBRATION_REQUIRED' if uncalibrated else 'IDEAL_MEASUREMENT_MODEL'
        target_evidence['measurement_assumption'] = 'Calibrated Pauli measurements of one common preanalysis state; sampling intervals do not cover systematic measurement-channel bias.'
        if uncalibrated:
            target_evidence['observed_witness_decision'] = target_evidence['status']
            target_evidence['conditional_witness_interval'] = target_evidence['fidelity_bound']
            target_evidence['fidelity_bound'] = [0., 1.]
            target_evidence['status'] = 'UNRESOLVED'
            target_evidence['bound_method'] = 'State fidelity is unestablished: declared readout or analysis-gate noise is not calibrated. Numerical witness bounds are conditional model calculations only'
            state = states['target:fidelity']
            state.status, state.lower, state.upper = 'UNRESOLVED', 0., 1.
            stop = ('MEASUREMENT_MODEL_UNCALIBRATED', 'Sampled witness means do not certify preanalysis state fidelity without a calibrated measurement model.')
            for action in ledger:
                action['interpretation'] = 'Conditional witness calculation; not a state-fidelity certificate under the declared measurement noise.'
                observed = action['observed_result']['target:fidelity']
                observed['conditional_witness_status'] = observed['status']
                observed['status'] = 'UNRESOLVED'
    else:
        states, ledger, stop, slot = run_policy(claims, groups, n, expected, port, policy_config)
    violated = [s for s in states.values() if s.status == "VIOLATED"]
    unresolved = [s for s in states.values() if not s.resolved]
    control = None
    if violated:
        ev = port.measure(None, request.batch_shots, "readout_control")
        zero = {format(i, f"0{n}b"): float(i == 0) for i in range(2 ** n)}
        tv = .5 * sum(abs(ev["counts"].get(k, 0) / ev["shots"] - zero[k]) for k in zero)
        radius = tv_radius(ev["shots"], 2 ** n, slot)
        control = {"execution_id": ev["execution_id"], "total_variation": tv, "uncertainty_radius": radius,
                   "tolerance": CONTROL_TOLERANCE, "significant_disagreement": tv - radius > CONTROL_TOLERANCE,
                   "method": "multinomial TV bound on |0...0> readout control; no gate noise is probed"}
    privileged, exact = [], None
    if request.diagnostic_mode == "simulator_assisted":
        budget.reserve(0, "privileged_exact_expectations", resources(subject))
        exact = exact_expectations(circuit, contract)
        privileged.append({"operation": "exact_expectations", "method": "Qiskit Statevector of the submitted circuit",
                           "note": "Simulator-only; not obtainable by sampling or on hardware"})
        if is_target:
            from .quantum import noisy_density
            rho = noisy_density(subject, Noise(depolarizing=request.environment.depolarizing))
            target_evidence["exact"] = {"label": "SIMULATOR_ASSISTED_EXACT_STATE",
                "ideal_fidelity": exact["target:fidelity"],
                "gate_noise_state_fidelity": fidelity(contract.vector(), rho),
                "note": "Privileged. Ideal = noiseless submitted circuit. Gate-noise state applies the configured "
                        "depolarizing channel per gate; readout error is not a state property and is excluded."}
    # --- assessment: detection, attribution, localization, recovery are separate verdicts
    if violated:
        category = "SIGNIFICANT_DISCREPANCY"
        reason = "At least one declared claim disagrees beyond tolerance at the corrected error level."
    elif unresolved:
        category = "INSUFFICIENT_EVIDENCE"
        reason = "Some declared claims are neither violated nor confirmed within tolerance: " + stop[1]
    else:
        category = "NO_SIGNIFICANT_DISCREPANCY"
        reason = "Declared claims were confirmed within tolerance. This does not establish circuit correctness."
    ideal_violation = None
    if exact is not None:
        ideal_violation = []
        for c in claims:
            v = exact[c["claim_id"]]
            if c["kind"] == "target_fidelity":
                if v < c["threshold"]:
                    ideal_violation.append(c["claim_id"])
                continue
            d = v if c["kind"] == "distribution" else abs(v - c["expected"])
            if d > c["tolerance"]:
                ideal_violation.append(c["claim_id"])
    noise_hint = bool(control and control["significant_disagreement"])
    if not violated:
        attribution = "NOT_APPLICABLE" if ideal_violation is None or not ideal_violation else "LOGICAL_DEFECT_SUPPORTED_BY_PRIVILEGED_STATE_NOT_SAMPLED"
    elif ideal_violation is None:
        attribution = "NOISE_CONSISTENT_NOT_UNIQUE" if noise_hint else "AMBIGUOUS_LOGICAL_VS_NOISE"
    elif ideal_violation and noise_hint:
        attribution = "MIXED"
    elif ideal_violation:
        attribution = "LOGICAL_DEFECT_SUPPORTED_FIXED_INPUT"
    else:
        attribution = "NOISE_CONSISTENT_FIXED_INPUT"
    eid = identifier("experiment")
    for r in records:
        r.update(experiment_id=eid, subject_circuit_id=circuit.circuit_id)
    diagnosis = {"category": category, "reason": reason, "capability_mode": request.diagnostic_mode,
                 "policy": request.policy,
                 "detection": {"status": category, "violated_claims": [s.claim["claim_id"] for s in violated],
                               "unresolved_claims": [s.claim["claim_id"] for s in unresolved]},
                 "attribution": {"status": attribution, "readout_control": control,
                                 "ideal_violation_claims": ideal_violation,
                                 "statement": "A violated expectation alone cannot separate a logical defect from gate or readout noise."},
                 "localization": {"status": "NOT_ESTABLISHED",
                                  "statement": "Violated claims do not identify a particular faulty gate."},
                 "stop": {"code": stop[0], "reason": stop[1]},
                 "confidence": None, "confidence_semantics": "No class probability claimed; intervals only",
                 "limitations": feas["limitations"]}
    recovery = {"status": "UNSUPPORTED",
                "reason": "No recovery class is validated for custom-circuit contracts (including target states); "
                          "repair selection from measurements is not implemented."}
    cost = {**budget.report(), "circuit_executions": len(records),
            "exact_state_evaluations": sum(a["shots"] == 0 for a in budget.actions),
            "basis_gates": sum(a["basis_gates"] for a in ledger), "runtime_seconds": perf_counter() - start}
    result = {"schema_version": 2, "investigation_kind": "custom_circuit", "experiment_id": eid,
              "created_at": timestamp(), "configuration": request.model_dump(mode="json"),
              "circuit": circuit.model_dump(mode="json"), "circuit_id": circuit.circuit_id,
              "executed_subject": subject.model_dump(mode="json"),
              "circuit_diagram": str(subject.native().draw(output="text")),
              "contract": {**request.contract.model_dump(mode="json"), "family": "custom", "contract_id": contract_id},
              "target_evidence": target_evidence,
              "feasibility": feas, "claims": [s.report() for s in states.values()],
              "action_ledger": ledger, "executions": records, "diagnosis": diagnosis, "recovery": recovery,
              "privileged_operations": privileged, "cost": cost,
              "statistical_design": {"method": ("Hoeffding intervals for every catalog Pauli term on a prespecified per-group shot grid "
                                     "{b,2b,...,Kb}; union bound over terms x looks plus one control; fidelity bounds are "
                                     "deterministic functions of those intervals" if is_target else
                                     "Hoeffding (Pauli) / Weissman TV (distribution) intervals on a prespecified "
                                     "per-group shot grid {b,2b,...,Kb}; union bound over claims x looks plus one control"),
                                     "alpha_total": request.alpha_total, "alpha_per_interval": slot,
                                     "looks_per_group": request.max_looks, "batch_shots": request.batch_shots,
                                     "validity": "Error rate for any false violation/confirmation <= alpha_total under i.i.d. shots and the stated measurement model. Target fidelity additionally requires calibrated common-state Pauli measurements; no certificate under uncalibrated noise. Not a class probability."},
              "replay": {"request": request.model_dump(mode="json"),
                         "note": "Same request and seed reproduce counts on the same backend and software versions"},
              "integrity": {"algorithm": "sha256", "canonicalization": "qfault-json-v1", "signing": "UNAVAILABLE"},
              "human_decisions": []}
    result["prediction_digest"] = digest({"diagnosis": diagnosis, "claims": result["claims"]})
    result["evaluation_truth"] = truth or {"kind": "user_supplied_circuit", "ground_truth": None,
        "note": "No evaluator truth exists for a user-supplied circuit; the simulated environment is requester-declared."}
    return result
