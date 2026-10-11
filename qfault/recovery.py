"""One-edit repair search and separately implemented independent verification."""
from itertools import permutations
from math import pi
import numpy as np
from qiskit.quantum_info import DensityMatrix
from .quantum import Circuit,Gate,ideal_state,execute,resources,probabilities,measured_circuit,measurement_probabilities
from .diagnostics import EvidenceCollector,comparison


def edit_candidates(circuit,limit=256):
    palette=[Gate(name=name,qubits=(q,)) for name in ["h","x","z"] for q in range(circuit.n_qubits)]
    palette += [Gate(name="cx",qubits=pair) for pair in permutations(range(circuit.n_qubits),2)]
    seen={circuit.circuit_id}
    produced=0
    gates=list(circuit.gates)
    edits=[]
    for i,gate in enumerate(gates):
        edits.append((gates[:i]+gates[i+1:],{"operator":"remove","index":i}))
        for replacement in palette:
            edits.append((gates[:i]+[replacement]+gates[i+1:],{"operator":"replace","index":i,"gate":replacement.model_dump(mode="json")}))
        if gate.angle is not None:
            for delta in [-pi/4,pi/4,-pi/2,pi/2]:
                if abs(gate.angle+delta)>8*pi: continue
                replacement=Gate(name=gate.name,qubits=gate.qubits,angle=gate.angle+delta)
                edits.append((gates[:i]+[replacement]+gates[i+1:],{"operator":"angle","index":i,"delta":delta}))
        for pair in permutations(range(circuit.n_qubits),len(gate.qubits)):
            replacement=Gate(name=gate.name,qubits=pair,angle=gate.angle)
            edits.append((gates[:i]+[replacement]+gates[i+1:],{"operator":"rewire","index":i,"qubits":list(pair)}))
    for i in range(len(gates)+1):
        for insertion in palette:
            edits.append((gates[:i]+[insertion]+gates[i:],{"operator":"insert","index":i,"gate":insertion.model_dump(mode="json")}))
    for changed,edit in edits:
        if len(changed)>32: continue
        candidate=Circuit(n_qubits=circuit.n_qubits,gates=tuple(changed))
        if candidate.circuit_id in seen: continue
        seen.add(candidate.circuit_id)
        yield candidate,{**edit,"edit_count":1}
        produced+=1
        if produced>=limit: return


class RecoveryPlanner:
    def propose(self,candidate,contract,budget,reserved_validation_shots=0,reserved_validation_evaluations=0):
        attempted=0
        for changed,edit in edit_candidates(candidate):
            if not budget.can(reserved_validation_shots,1+reserved_validation_evaluations): break
            budget.reserve(0,"repair_candidate_state",resources(changed))
            attempted+=1
            infidelity=float(max(0.,1-abs(np.vdot(contract.state(),ideal_state(changed)))**2))
            if infidelity<=contract.state_infidelity_tolerance:
                return {"candidate":changed.model_dump(mode="json"),"edit":edit,"selection_infidelity":infidelity,
                        "candidates_attempted":attempted,"search_limit":256,
                        "status":"PROPOSED","requires_human_review":True}
        return {"status":"NO_VERIFIED_CANDIDATE","candidates_attempted":attempted,"search_limit":256,
                "reason":"No satisfying one-edit candidate found within search and execution budget"}


class IndependentVerifier:
    def verify(self,candidate,contract,noise,shots,seed,budget,phase_validate=False,backend="reference"):
        if not budget.can(shots*(2 if phase_validate else 1),3 if phase_validate else 2):
            return {"verified_status":"INCONCLUSIVE","contract_satisfied":False,"reason":"Validation budget exhausted"}
        budget.reserve(0,"independent_density_state",resources(candidate))
        # Different evolution implementation from planner's Statevector; analytic expected state.
        density=DensityMatrix.from_label("0"*candidate.n_qubits).evolve(candidate.native())
        target=contract.state()
        fidelity=float(np.real(np.vdot(target,density.data@target)))
        budget.reserve(shots,"independent_recovery_measurement",resources(candidate))
        record=execute(candidate,noise,shots,seed,contract_id=contract.contract_id,backend=backend)
        measured=EvidenceCollector.collect(record,candidate.n_qubits)
        result=comparison(measured,probabilities(target),contract.distribution_tolerance)
        state_ok=1-fidelity<=contract.state_infidelity_tolerance
        sampled_ok=result["upper"]<=contract.distribution_tolerance
        phase_record=None
        phase_comparison=None
        if phase_validate:
            rotated=measured_circuit(candidate,contract)
            budget.reserve(shots,"independent_phase_measurement",resources(rotated))
            phase_record=execute(rotated,noise,shots,(seed+17)%2**32,contract_id=contract.contract_id,backend=backend)
            phase_record.update(measurement_basis="contract phase basis",subject_circuit_id=candidate.circuit_id)
            phase_comparison=comparison(EvidenceCollector.collect(phase_record,candidate.n_qubits),measurement_probabilities(contract),contract.distribution_tolerance)
            sampled_ok=sampled_ok and phase_comparison["upper"]<=contract.distribution_tolerance
        rejected=(not state_ok) or result["significant_disagreement"] or bool(phase_comparison and phase_comparison["significant_disagreement"])
        status="VERIFIED" if state_ok and sampled_ok else "REJECTED" if rejected else "INCONCLUSIVE"
        answer={"verified_status":status,"contract_satisfied":status=="VERIFIED",
                "validation_method":"Independent Qiskit DensityMatrix fixed-input fidelity plus fresh sampled counts",
                "validation_seed":seed,"additional_shots":shots*(2 if phase_validate else 1),"additional_evaluations":3 if phase_validate else 2,
                "state_fidelity":fidelity,"distribution_comparison":result,"execution":record,
                "candidate_quality":1-result["total_variation"],"uncertainty":result["uncertainty_radius"],
                "unitary_equivalence":"NOT_CHECKED","hardware_performance":"NOT_MEASURED"}

        if phase_validate:
            answer.update(phase_execution=phase_record,phase_distribution_comparison=phase_comparison)
        return answer
