"""Diagnosis consumes measured projections and bounded diagnostic operations only."""
from math import log, sqrt
from dataclasses import dataclass, field
import numpy as np
from pydantic import Field
from .quantum import Strict, Circuit, Noise, ideal_state, probabilities, execute, resources


class MeasuredEvidence(Strict):
    execution_id: str
    shots: int = Field(ge=1)
    counts: dict[str,int]


class EvidenceCollector:
    @staticmethod
    def collect(record,n):
        if record["execution_status"]!="SUCCEEDED": raise ValueError("execution failed")
        counts=record["output_counts"]
        shots=record["executed_shots"]
        if not counts or any(len(k)!=n or set(k)-{"0","1"} or type(v) is not int or v<0 for k,v in counts.items()):
            raise ValueError("invalid measured counts")
        if type(shots) is not int or shots<1 or sum(counts.values())!=shots:
            raise ValueError("counts do not match executed shots")
        # Explicit allowlist: backend scenario metadata and evaluator truth never cross this boundary.
        return MeasuredEvidence(execution_id=record["execution_id"],shots=shots,counts=dict(counts))


def total_variation(counts,shots,expected):
    if shots<=0 or sum(counts.values())!=shots: raise ValueError("invalid shot accounting")
    if any(not np.isfinite(v) or v<0 for v in expected.values()) or abs(sum(expected.values())-1)>1e-8:
        raise ValueError("invalid probability distribution")
    return .5*sum(abs(counts.get(k,0)/shots-expected.get(k,0)) for k in set(counts)|set(expected))


def tv_radius(shots,outcomes,alpha=.001):
    """Weissman multinomial L1 bound / 2; alpha per comparison, <=10 comparisons/run."""
    return min(1.,sqrt(log((2.**outcomes-2)/alpha)/(2*shots)))


def comparison(measured,expected,tolerance):
    tv=total_variation(measured.counts,measured.shots,expected)
    radius=tv_radius(measured.shots,len(expected))
    return {"total_variation":tv,"uncertainty_radius":radius,"lower":max(0.,tv-radius),
            "upper":min(1.,tv+radius),"tolerance":tolerance,
            "significant_disagreement":tv-radius>tolerance,
            "method":"multinomial TV concentration bound; per-comparison alpha=0.001"}


@dataclass
class ExecutionBudget:
    max_shots: int
    max_evaluations: int
    shots: int = 0
    evaluations: int = 0
    actions: list = field(default_factory=list)

    def can(self,shots=0,evaluations=1):
        return self.shots+shots<=self.max_shots and self.evaluations+evaluations<=self.max_evaluations

    def reserve(self,shots,label,resource=None):
        if type(shots) is not int or shots<0 or not self.can(shots): raise ValueError("execution budget exhausted")
        self.shots+=shots
        self.evaluations+=1
        self.actions.append({"action":label,"shots":shots,"resources":resource or {}})

    def report(self):
        return {"shots":self.shots,"evaluations":self.evaluations,"max_shots":self.max_shots,
                "max_evaluations":self.max_evaluations,"actions":self.actions,
                "depth_sum":sum(a["resources"].get("depth",0) for a in self.actions),
                "two_qubit_gate_sum":sum(a["resources"].get("two_qubit_gates",0) for a in self.actions),
                "cost_units":"shots and local circuit evaluations; no currency conversion"}


class DiagnosticAccess:
    """Simulator oracle. No mutation label, original circuit or scenario is retained.

    Noise configuration remains in the executor. This is a software API boundary,
    not a security sandbox against adversarial Python introspection.
    """
    def __init__(self,candidate,noise,budget,seed):
        self._candidate=candidate
        self._noise=noise
        self.budget=budget
        self._seed=seed
        self.records=[]

    def state_probe(self,contract):
        self.budget.reserve(0,"diagnostic_ideal_state",resources(self._candidate))
        state=ideal_state(self._candidate)
        return {"infidelity":float(max(0.,1-abs(np.vdot(contract.state(),state))**2)),
                "probabilities":probabilities(state),"method":"Qiskit Statevector exact local calculation",
                "limitation":"Privileged simulator operation; unavailable as a direct hardware measurement"}

    def readout_probe(self):
        shots=1024
        self.budget.reserve(shots,"diagnostic_readout_zero")
        c=Circuit(n_qubits=self._candidate.n_qubits,gates=())
        r=execute(c,self._noise,shots,(self._seed+101)%2**32)
        self.records.append(r)
        m=EvidenceCollector.collect(r,c.n_qubits)
        expected={format(i,f"0{c.n_qubits}b"):float(i==0) for i in range(2**c.n_qubits)}
        return comparison(m,expected,.10)


class DiagnosticAnalyst:
    def analyze(self,candidate,contract,measured,access,policy="evidence"):
        expected=probabilities(contract.state())
        discrepancy=comparison(measured,expected,contract.distribution_tolerance)
        significant=discrepancy["significant_disagreement"]
        state=None
        calibration=None
        residual=None
        if policy not in {"evidence","fixed","random","threshold"}: raise ValueError("unsupported policy")
        state_needed=(policy=="fixed" or significant or (policy=="threshold" and discrepancy["total_variation"]>.10))
        random_calibration=(policy=="random" and np.random.default_rng(access._seed).integers(2)==0)
        if random_calibration: state_needed=False
        if state_needed and access.budget.can():
            state=access.state_probe(contract)
            residual=comparison(measured,state["probabilities"],contract.distribution_tolerance)
        if (policy=="fixed" or significant) and policy!="threshold" and access.budget.can(1024):
            calibration=access.readout_probe()
        logical=state is not None and state["infidelity"]>contract.state_infidelity_tolerance
        noise=(residual is not None and residual["significant_disagreement"]) or (calibration is not None and calibration["significant_disagreement"])
        if significant and state is None:
            category="INSUFFICIENT_EVIDENCE"
            reason="Measurement failure detected; budget or policy did not resolve logical versus noise explanations."
        elif logical and noise:
            category="MIXED_OR_AMBIGUOUS"
            reason="Ideal state violates the contract and independent noise-sensitive measurements also disagree."
        elif logical:
            category="LOGICAL_CIRCUIT_DEFECT"
            reason="Ideal fixed-input state violates the contract; observed counts alone are not the proof."
        elif significant and state is not None:
            category="NOISE_CONSISTENT_DEGRADATION"
            reason="Ideal state satisfies the contract while sampled execution disagrees; consistent with execution noise."
        elif measured.shots<128:
            category="INSUFFICIENT_EVIDENCE"
            reason="Too few shots for the supported investigation policy."
        else:
            category="NO_SIGNIFICANT_FAILURE_DETECTED"
            reason="No supported disagreement detected; this does not establish circuit correctness."
        hypotheses=[{"hypothesis":"logical fixed-input defect","support":"supported" if logical else "not established"},
                    {"hypothesis":"noise-related degradation","support":"supported" if noise or category=="NOISE_CONSISTENT_DEGRADATION" else "not established"},
                    {"hypothesis":"finite-shot variation","support":"not excluded" if not significant else "insufficient to explain measured effect under the declared bound"}]
        return {"category":category,"reason":reason,"policy":policy,"discrepancy":discrepancy,
                "state_infidelity":None if state is None else state["infidelity"],"state_probe":state,
                "readout_probe":calibration,"candidate_distribution_comparison":residual,
                "hypotheses":hypotheses,"evidence_references":[measured.execution_id],
                "confidence":None,"confidence_semantics":"No calibrated class probability is claimed",
                "limitations":["Only tested noise channels are supported; noise attribution is consistency, not causal proof",
                    "State diagnostics cover one declared input, not full unitary equivalence",
                    "Measurement-triggered plans can miss phase-only faults",
                    "At most ten TV comparisons; union bound failure probability <=0.01 per investigation"]}
