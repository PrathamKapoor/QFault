"""Deterministic investigation supervisor and evaluator-side scenario construction."""
from time import perf_counter
from typing import Literal
from pydantic import Field,model_validator
from .quantum import Strict,Noise,Circuit,Gate,benchmark,contract,mutate,execute,resources
from .diagnostics import EvidenceCollector,DiagnosticAnalyst,DiagnosticAccess,ExecutionBudget
from .recovery import RecoveryPlanner,IndependentVerifier
from .evidence import identifier,timestamp,digest


class RunRequest(Strict):
    family: Literal["bell","ghz","qft"] = "bell"
    n_qubits: int | None = Field(default=None,ge=2,le=5)
    scenario: Literal["clean","readout","gate","remove","replace","angle","rewire","mixed","phase"] = "clean"
    shots: int = Field(default=2048,ge=1,le=10000,strict=True)
    seed: int = Field(default=42,ge=0,lt=2**32,strict=True)
    policy: Literal["evidence","fixed","random","threshold","phase"] = "fixed"
    max_shots: int = Field(default=12000,ge=2,le=100000,strict=True)
    max_evaluations: int = Field(default=384,ge=2,le=600,strict=True)
    recover: bool = True

    @model_validator(mode="after")
    def valid(self):
        contract(self.family,self.n_qubits or (2 if self.family=="bell" else 3))
        if self.max_shots<2*self.shots: raise ValueError("budget must fund baseline and observation")
        if self.scenario=="angle" and self.family!="qft": raise ValueError("angle scenario requires QFT")
        return self


class Supervisor:
    allowed={"REGISTERED":{"BASELINED"},"BASELINED":{"OBSERVED"},"OBSERVED":{"DIAGNOSED"},
             "DIAGNOSED":{"RECOVERY_PROPOSED","AWAITING_HUMAN_REVIEW"},
             "RECOVERY_PROPOSED":{"VERIFICATION_COMPLETED"},"VERIFICATION_COMPLETED":{"AWAITING_HUMAN_REVIEW"},
             "AWAITING_HUMAN_REVIEW":{"REVIEWED"},"REVIEWED":set()}
    def __init__(self):
        self.state="REGISTERED"
        self.history=[{"state":self.state,"at":timestamp()}]
    def transition(self,state):
        if state not in self.allowed[self.state]: raise ValueError(f"invalid transition {self.state} -> {state}")
        self.state=state
        self.history.append({"state":state,"at":timestamp()})


def scenario(request):
    n=request.n_qubits or (2 if request.family=="bell" else 3)
    original=benchmark(request.family,n)
    candidate=original
    noise=Noise(readout=.18 if request.scenario in {"readout","mixed"} else 0,
                depolarizing=.20 if request.scenario=="gate" else 0)
    truth={"scenario":request.scenario,"mutation":None,"noise":noise.model_dump()}
    if request.scenario in {"remove","replace","rewire","mixed","angle"}:
        operator="remove" if request.scenario=="mixed" else request.scenario
        eligible=[i for i,g in enumerate(original.gates) if g.angle is not None] if operator=="angle" else list(range(len(original.gates)))
        index=eligible[-1] if request.family!="qft" else eligible[0]
        candidate,mutation=mutate(original,operator,index,request.seed)
        truth["mutation"]=mutation
    if request.scenario=="phase":
        candidate=Circuit(n_qubits=n,gates=original.gates+(Gate(name="z",qubits=(0,)),))
        truth["mutation"]={"operator":"insert_phase","index":len(original.gates)}
    return original,candidate,noise,truth


def investigate(request):
    start=perf_counter()
    original,candidate,noise,truth=scenario(request)
    spec=contract(request.family,candidate.n_qubits)
    experiment_id=identifier("experiment")
    supervisor=Supervisor()
    budget=ExecutionBudget(request.max_shots,request.max_evaluations)
    records=[]
    budget.reserve(request.shots,"baseline",resources(original))
    records.append(execute(original,Noise(),request.shots,request.seed,experiment_id,spec.contract_id))
    supervisor.transition("BASELINED")
    budget.reserve(request.shots,"observation",resources(candidate))
    records.append(execute(candidate,noise,request.shots,request.seed,experiment_id,spec.contract_id))
    supervisor.transition("OBSERVED")
    measured=EvidenceCollector.collect(records[-1],candidate.n_qubits)
    access=DiagnosticAccess(candidate,noise,budget,request.seed)
    diagnosis=DiagnosticAnalyst().analyze(candidate,spec,measured,access,request.policy)
    for record in access.records:
        record.update(experiment_id=experiment_id,contract_id=spec.contract_id)
    records.extend(access.records)
    supervisor.transition("DIAGNOSED")
    recovery=None
    if request.recover and diagnosis["category"]=="LOGICAL_CIRCUIT_DEFECT":
        recovery=RecoveryPlanner().propose(candidate,spec,budget,
                    reserved_validation_shots=2*request.shots if request.policy=="phase" else 0,
                    reserved_validation_evaluations=3 if request.policy=="phase" else 0)
        if recovery["status"]=="PROPOSED":
            supervisor.transition("RECOVERY_PROPOSED")
            verification=IndependentVerifier().verify(Circuit.model_validate(recovery["candidate"]),spec,noise,
                         request.shots,(request.seed+10007)%2**32,budget,phase_validate=request.policy=="phase")
            verification["original_quality"]=1-diagnosis["discrepancy"]["total_variation"]
            if diagnosis.get("phase_probe") and verification.get("phase_distribution_comparison"):
                verification["original_phase_quality"]=1-diagnosis["phase_probe"]["comparison"]["total_variation"]
                verification["candidate_phase_quality"]=1-verification["phase_distribution_comparison"]["total_variation"]
            recovery["verification"]=verification
            recovery["status"]=verification["verified_status"]
            if "execution" in verification:
                verification["execution"].update(experiment_id=experiment_id,contract_id=spec.contract_id)
                records.append(verification["execution"])
            if "phase_execution" in verification:
                verification["phase_execution"].update(experiment_id=experiment_id,contract_id=spec.contract_id)
                records.append(verification["phase_execution"])
            supervisor.transition("VERIFICATION_COMPLETED")
    supervisor.transition("AWAITING_HUMAN_REVIEW")
    result={"schema_version":1,"experiment_id":experiment_id,"created_at":timestamp(),
            "configuration":request.model_dump(),"contract":spec.describe(),"candidate":candidate.model_dump(mode="json"),
            "circuit_id":candidate.circuit_id,"circuit_diagram":str(candidate.native().draw(output="text")),
            "executions":records,"measured_evidence":measured.model_dump(),"diagnosis":diagnosis,"recovery":recovery,
            "cost":{**budget.report(),"circuit_executions":len(records),"exact_state_evaluations":sum(a["shots"]==0 for a in budget.actions),"runtime_seconds":perf_counter()-start},
            "supervisor":{"state":supervisor.state,"history":supervisor.history},"human_decisions":[],
            "integrity":{"algorithm":"sha256","canonicalization":"qfault-json-v1","signing":"UNAVAILABLE"}}
    result["observations"]=[{
        "observation_id":identifier("observation"),"experiment_id":experiment_id,"subject_id":r["circuit_id"],
        "kind":"measured","observation_type":"quantum_counts","severity":"informational",
        "evidence_references":[r["execution_id"]],"measured_values":r["output_counts"],"comparison_values":None,
        "uncertainty":{"shots":r["executed_shots"]},"measurement_basis":r.get("measurement_basis","computational Z"),"method":r["backend_name"],"method_version":"1",
        "limitations":["Simulated finite-shot measurements"],"created_at":timestamp()} for r in records]
    result["observations"].append({
        "observation_id":identifier("observation"),"experiment_id":experiment_id,"subject_id":candidate.circuit_id,
        "kind":"derived","observation_type":"contract_comparison","severity":"warning" if diagnosis["discrepancy"]["significant_disagreement"] else "informational",
        "evidence_references":[measured.execution_id],"measured_values":diagnosis["discrepancy"],
        "comparison_values":spec.describe()["expected_probabilities"],"uncertainty":diagnosis["discrepancy"]["uncertainty_radius"],
        "method":"total variation with multinomial concentration bound","method_version":"1",
        "limitations":diagnosis["limitations"],"created_at":timestamp()})
    # Predictions are complete before the evaluator attaches truth. Analyst never receives this object.
    result["prediction_digest"]=digest({"diagnosis":diagnosis,"recovery":recovery})
    result["evaluation_truth"]=truth
    return result
