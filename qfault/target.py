"""Target-state contracts: Pauli witness catalog, rigorous fidelity bounds, adaptive witness selection.

Conventions: amplitude index i is the computational basis state format(i, f"0{n}b") in Qiskit order
(rightmost bit = qubit 0), identical to qiskit.quantum_info.Statevector. Pauli labels use the same order.

Two evidence paths are kept separate:
- SIMULATOR_ASSISTED_EXACT_STATE: privileged fidelity of the simulated candidate state.
- MEASUREMENT_DERIVED_WITNESS: bounds computed only from sampled Pauli expectations plus the
  user-declared target. The target's coefficients are not privileged; the candidate's state is.
"""
from functools import lru_cache
from math import sqrt
from typing import Annotated, Literal
import numpy as np
from pydantic import Field, model_validator
from qiskit.quantum_info import DensityMatrix, SparsePauliOp, Statevector
from .quantum import Strict

TARGET_NORM_TOLERANCE = 1e-6
STABILIZER_TOLERANCE = 1e-9
CATALOG_VERSION = "pauli-expansion-v1"
POLICY_VERSION = "witness-policy-v1"
TARGET_POLICIES = ("adaptive_witness", "coefficient_weighted", "fixed", "random", "complementary_schedule")


class TargetStateContract(Strict):
    kind: Literal["target_state"]
    environment: Literal["ideal"] = "ideal"
    # [real, imaginary] JSON numbers only; strings and expressions are rejected (strict).
    amplitudes: tuple[tuple[Annotated[float, Field(strict=True)], Annotated[float, Field(strict=True)]], ...] = Field(min_length=4, max_length=32)
    fidelity_tolerance: float = Field(gt=0, lt=1)
    provenance: str = Field(default="user-declared", min_length=1, max_length=200)

    @model_validator(mode="after")
    def valid(self):
        d = len(self.amplitudes)
        if d & (d - 1):
            raise ValueError("amplitude count must be 2**n_qubits (4-32)")
        norm2 = sum(r * r + i * i for r, i in self.amplitudes)
        if abs(norm2 - 1) > TARGET_NORM_TOLERANCE:
            raise ValueError(f"target must be normalized: |psi|^2={norm2:.9g}, allowed deviation {TARGET_NORM_TOLERANCE}")
        if not self.provenance.isprintable():
            raise ValueError("provenance must be printable text")
        return self

    @property
    def n_qubits(self):
        return len(self.amplitudes).bit_length() - 1

    @property
    def threshold(self):
        return 1 - self.fidelity_tolerance

    def vector(self):
        """Declared vector divided by its norm (a correction of at most ~5e-7, recorded as norm_squared)."""
        v = np.array([complex(r, i) for r, i in self.amplitudes])
        return v / np.linalg.norm(v)


def fidelity(target, state):
    """F = <psi_t|rho|psi_t> for a pure target; global-phase invariant by construction."""
    t = np.asarray(target, dtype=complex)
    if isinstance(state, DensityMatrix):
        return float(np.real(np.vdot(t, state.data @ t)))
    s = np.asarray(state.data if isinstance(state, Statevector) else state, dtype=complex)
    return float(abs(np.vdot(t, s)) ** 2)


@lru_cache(maxsize=64)
def catalog(amplitudes):
    """Deterministic target-only Pauli catalog.

    a_P = Tr(P rho_t) for every non-identity P with |a_P| above SparsePauliOp's internal cut-off.
    Terms it omits are accounted rigorously: their squared mass is d - 1 - sum(a_P^2) (purity), so
    their absolute sum is at most sqrt(count * mass) by Cauchy-Schwarz.
    """
    v = np.array([complex(r, i) for r, i in amplitudes]); v = v / np.linalg.norm(v)
    d = len(v); n = d.bit_length() - 1
    op = SparsePauliOp.from_operator(DensityMatrix(v))
    terms = []
    for label, c in zip(op.paulis.to_labels(), op.coeffs):
        if abs(c.imag) * d > 1e-9:
            raise ValueError("non-Hermitian Pauli coefficient")  # cannot happen for a valid density matrix
        if set(label) == {"I"}:
            continue
        terms.append((label, float(c.real) * d))
    terms.sort(key=lambda t: (-abs(t[1]), t[0]))
    mass = max(0.0, d - 1 - sum(a * a for _, a in terms))
    omitted = 4 ** n - 1 - len(terms)
    stabilizer = len(terms) == d - 1 and all(abs(abs(a) - 1) < STABILIZER_TOLERANCE for _, a in terms)
    return {"n": n, "terms": tuple(terms), "omitted_count": omitted, "omitted_mass": mass,
            "omitted_abs_bound": sqrt(omitted * mass), "stabilizer": stabilizer}


def _symplectic(label):
    return tuple(c in "XY" for c in label) + tuple(c in "ZY" for c in label)


def _independent(rows, row):
    """GF(2) independence of Pauli (x|z) vectors; phases ignored."""
    basis = [list(r) for r in rows]
    v = list(row)
    for b in basis:
        pivot = b.index(True)
        if v[pivot]:
            v = [x ^ y for x, y in zip(v, b)]
    return any(v)


def _reduced(rows):
    out = []
    for r in rows:
        v = list(r)
        for b in out:
            pivot = b.index(True)
            if v[pivot]:
                v = [x ^ y for x, y in zip(v, b)]
        if any(v):
            out.append(v)
    return out


def bounds(cat, est, rad):
    """Simultaneous [L, U] for F = Tr(rho_t rho) given intervals est+-rad on measured Pauli terms.

    Valid whenever every measured interval contains its true expectation. Combines:
    (1) Pauli expansion F = (1 + sum a_P b_P)/d, unmeasured terms bounded by both |b|<=1 and
        Cauchy-Schwarz with purity (sum of non-identity b^2 <= d-1);
    (2) stabilizer targets: F >= 1 - sum_i (1-<g_i>)/2 for any independent generating set
        (commuting projectors), using the greedy max-weight basis (optimal for a linear matroid),
        and F <= (1+<g>)/2 for every measured stabilizer element g;
    (3) Fuchs-van de Graaf: |b_P - a_P| <= 2D <= 2 sqrt(1-F)  =>  F <= 1 - (|b_P-a_P|/2)^2.
    """
    n, terms = cat["n"], cat["terms"]
    d = 2 ** n
    lo = hi = 1.0
    un_abs, un_sq = cat["omitted_abs_bound"], cat["omitted_mass"]
    upper = 1.0
    stab_lower_parts = []
    for label, a in terms:
        if label in est:
            b_lo, b_hi = max(-1., est[label] - rad[label]), min(1., est[label] + rad[label])
            lo += min(a * b_lo, a * b_hi); hi += max(a * b_lo, a * b_hi)
            dev = max(0., abs(est[label] - a) - rad[label])
            upper = min(upper, 1 - (dev / 2) ** 2)
            if cat["stabilizer"]:
                g_lo, g_hi = (b_lo, b_hi) if a > 0 else (-b_hi, -b_lo)
                upper = min(upper, (1 + g_hi) / 2)
                stab_lower_parts.append((g_lo, label))
        else:
            un_abs += abs(a); un_sq += a * a
    slack = min(un_abs, sqrt(un_sq * (d - 1)))
    L, U = max(0., (lo - slack) / d), min(1., (hi + slack) / d, upper)
    if cat["stabilizer"]:
        chosen = []
        for g_lo, label in sorted(stab_lower_parts, reverse=True):
            vec = _symplectic(label)
            if not chosen or _independent(_reduced([_symplectic(x) for _, x in chosen]), vec):
                chosen.append((g_lo, label))
            if len(chosen) == n:
                L = max(L, 1 - sum((1 - g) / 2 for g, _ in chosen))
                break
    return L, U  # L > U indicates incompatible intervals or a failed common-state measurement model.


def decide(L, U, threshold):
    if L > U:
        return "UNRESOLVED"
    if U < threshold:
        return "VIOLATED"
    if L >= threshold:
        return "SATISFIED_WITHIN_TOLERANCE"
    return "UNRESOLVED"


def point_estimate(cat, est):
    """Plug-in fidelity: measured terms at their estimates, all others at their target values. Not a bound."""
    d = 2 ** cat["n"]
    return (1 + sum(a * est.get(label, a) for label, a in cat["terms"]) + cat["omitted_mass"]) / d


def _project(cat, est, rad, groups, radii):
    target = dict(cat["terms"])
    e2, r2 = dict(est), dict(rad)
    for terms, r in zip(groups, radii):
        for label in terms:
            e2[label] = est.get(label, target[label])
            r2[label] = r
    return bounds(cat, e2, r2)


def marginal_gains(cat, est, rad, groups, radii, threshold):
    """Plug-in marginal value of one more look at each open group.

    Heuristic proxy, NOT expected information gain. Projection: measured terms keep their current
    estimates, unmeasured terms sit at their target values, radii shrink to the next grid point.
    Value of group g = bound(project all open groups) - bound(project all open groups except g), so a
    group that only helps jointly with others (e.g. stabilizer generators) is still credited.
    Falls back to one-step gains when every marginal value is zero.
    Direction: confirmation (raise L) while the plug-in fidelity is at/above threshold, violation
    (lower U) otherwise; the observed estimates steer this choice.
    Returns ([(primary, secondary)], direction).
    """
    direction = "confirm" if point_estimate(cat, est) >= threshold else "violate"
    L_all, U_all = _project(cat, est, rad, groups, radii)
    out = []
    for i in range(len(groups)):
        Lw, Uw = _project(cat, est, rad, groups[:i] + groups[i + 1:], radii[:i] + radii[i + 1:])
        out.append((max(0., L_all - Lw), max(0., Uw - U_all)))
    if not any(c > 1e-12 or v > 1e-12 for c, v in out):
        L0, U0 = bounds(cat, est, rad)
        out = []
        for terms, r in zip(groups, radii):
            L1, U1 = _project(cat, est, rad, [terms], [r])
            out.append((max(0., L1 - L0), max(0., U0 - U1)))
    return [(c, v) if direction == "confirm" else (v, c) for c, v in out], direction
