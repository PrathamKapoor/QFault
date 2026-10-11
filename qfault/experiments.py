"""Frozen corpus evaluation. Truth is consulted only after predictions exist."""
import json
import math
from pathlib import Path
from statistics import NormalDist
from qiskit.quantum_info import DensityMatrix
from .quantum import Circuit,contract
from .workflow import RunRequest,investigate
from .storage import ArtifactStore
from .evidence import canonical,digest,timestamp


def event_rate(k,n):
    if not 0<=k<=n: raise ValueError("invalid event counts")
    if n==0: return {"successes":k,"n":n,"rate":None,"low":None,"high":None,"method":"Wilson 95%"}
    z=NormalDist().inv_cdf(.975)
    p=k/n
    denominator=1+z*z/n
    center=(p+z*z/(2*n))/denominator
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return {"successes":k,"n":n,"rate":p,"low":max(0.,center-half),"high":min(1.,center+half),"method":"Wilson 95%"}


def summarize(rows):
    abstain={"INSUFFICIENT_EVIDENCE","UNSUPPORTED"}
    selected=[r for r in rows if r["prediction"] not in abstain]
    clean=[r for r in rows if r["truth"]=="NO_SIGNIFICANT_FAILURE_DETECTED"]
    logical=[r for r in rows if r["truth"]=="LOGICAL_CIRCUIT_DEFECT"]
    confusion={}
    for r in rows:
        confusion.setdefault(r["truth"],{})[r["prediction"]]=confusion.setdefault(r["truth"],{}).get(r["prediction"],0)+1
    return {"accuracy":event_rate(sum(r["prediction"]==r["truth"] for r in rows),len(rows)),
            "abstention":event_rate(sum(r["prediction"] in abstain for r in rows),len(rows)),
            "selective_accuracy":event_rate(sum(r["prediction"]==r["truth"] for r in selected),len(selected)),
            "clean_false_diagnosis":event_rate(sum(r["prediction"]!="NO_SIGNIFICANT_FAILURE_DETECTED" and r["prediction"] not in abstain for r in clean),len(clean)),
            "logical_defect_recall":event_rate(sum(r["prediction"]=="LOGICAL_CIRCUIT_DEFECT" for r in logical),len(logical)),
            "per_class_recall":{truth:event_rate(confusion[truth].get(truth,0),sum(confusion[truth].values())) for truth in confusion},
            "confusion_matrix":confusion,"shots":sum(r["shots"] for r in rows),
            "evaluations":sum(r["evaluations"] for r in rows),"cases":len(rows)}


def evaluator_truth(result):
    candidate=Circuit.model_validate(result["candidate"])
    spec=contract(result["contract"]["family"],candidate.n_qubits)
    rho=DensityMatrix.from_label("0"*candidate.n_qubits).evolve(candidate.native())
    state=spec.state()
    infidelity=max(0.,1-float((state.conj()@rho.data@state).real))
    defective=infidelity>spec.state_infidelity_tolerance
    noise=result["evaluation_truth"]["noise"]
    noisy=any(v>0 for v in noise.values())
    truth="MIXED_OR_AMBIGUOUS" if defective and noisy else "LOGICAL_CIRCUIT_DEFECT" if defective else "NOISE_CONSISTENT_DEGRADATION" if noisy else "NO_SIGNIFICANT_FAILURE_DETECTED"
    return truth,infidelity


def benchmark_run(destination):
    out=Path(destination)
    out.mkdir(parents=True,exist_ok=False)
    store=ArtifactStore(out/"investigations")
    config={"protocol":"docs/benchmark-protocol.md","seeds":[11,29,47],"shots":2048,
            "max_shots":6144,"max_evaluations":4,"policies":["evidence","fixed","random","threshold"],
            "families":["bell","ghz","qft"],"scenarios":["clean","readout","gate","remove","replace","rewire","mixed","phase"]}
    (out/"configuration.json").write_bytes(canonical(config))
    rows=[]
    for policy in config["policies"]:
        for family in config["families"]:
            scenarios=config["scenarios"]+(["angle"] if family=="qft" else [])
            for scenario in scenarios:
                for seed in config["seeds"]:
                    result=investigate(RunRequest(family=family,scenario=scenario,seed=seed,policy=policy,recover=False,
                         shots=config["shots"],max_shots=config["max_shots"],max_evaluations=config["max_evaluations"]))
                    # Freeze proof before evaluator reads truth.
                    assert result["prediction_digest"]==digest({"diagnosis":result["diagnosis"],"recovery":result["recovery"]})
                    truth,infidelity=evaluator_truth(result)
                    eid=store.save(result)
                    rows.append({"policy":policy,"family":family,"scenario":scenario,"seed":seed,
                        "truth":truth,"prediction":result["diagnosis"]["category"],"evaluator_state_infidelity":infidelity,
                        "shots":result["cost"]["shots"],"evaluations":result["cost"]["evaluations"],
                        "runtime_seconds":result["cost"]["runtime_seconds"],"experiment_id":eid,
                        "manifest_digest":digest(store.export(eid)["manifest"]),"artifact_path":str(out/"investigations"/eid)})
    recovery=[]
    for family in ["bell","ghz"]:
        for seed in config["seeds"]:
            result=investigate(RunRequest(family=family,scenario="remove",seed=seed))
            eid=store.save(result)
            proposal=result["recovery"]
            recovery.append({"family":family,"seed":seed,"experiment_id":eid,
               "proposed":bool(proposal and "verification" in proposal),
               "verified":bool(proposal and proposal.get("verification",{}).get("verified_status")=="VERIFIED"),
               "status":proposal["status"] if proposal else "NO_PROPOSAL","shots":result["cost"]["shots"],
               "evaluations":result["cost"]["evaluations"],"original_quality":None if not proposal else proposal.get("verification",{}).get("original_quality"),
               "candidate_quality":None if not proposal else proposal.get("verification",{}).get("candidate_quality")})
    summary={"created_at":timestamp(),"configuration":config,"configuration_digest":digest(config),
             "policies":{p:summarize([r for r in rows if r["policy"]==p]) for p in config["policies"]},
             "recovery":{"verified_all_faulty":event_rate(sum(r["verified"] for r in recovery),len(recovery)),
                         "verified_proposals":event_rate(sum(r["verified"] for r in recovery),sum(r["proposed"] for r in recovery)),
                         "rows":recovery},
             "limitations":["Small fixed corpus with repeated sampling seeds; Wilson intervals are descriptive, not circuit-population guarantees",
                 "Exact simulator diagnostics are privileged and costed in evaluations, not shots",
                 "Configured noise may be unobservable for a given measurement contract",
                 "No tuning or hardware experiments; no scientific superiority claim"],"rows":rows}
    (out/"summary.json").write_bytes(canonical(summary))
    (out/"summary.sha256").write_text(digest(summary),encoding="ascii")
    return summary


def compare_policies(config,destination,split):
    """Execute a prespecified split; evaluator labels are consulted after freeze."""
    out=Path(destination)
    out.mkdir(parents=True,exist_ok=False)
    store=ArtifactStore(out/'investigations')
    settings=config[split]
    shots=settings.get('shots',config['shots'])
    rows=[]
    for policy in config['policies']:
        for family,n in settings['circuits']:
            scenarios=settings.get('scenarios',config['scenarios'])+(config.get('qft_extra',[]) if family=='qft' else [])
            for scenario in scenarios:
                for seed in settings['seeds']:
                    request=RunRequest(family=family,n_qubits=n,scenario=scenario,policy=policy,seed=seed,
                        shots=shots,max_shots=config['max_shots'],max_evaluations=config['max_evaluations'],recover=False)
                    result=investigate(request)
                    assert result['prediction_digest']==digest({'diagnosis':result['diagnosis'],'recovery':result['recovery']})
                    truth,infidelity=evaluator_truth(result)
                    eid=store.save(result)
                    rows.append({'case_id':f'{family}-{n}-{scenario}-{seed}','policy':policy,'family':family,'n_qubits':n,
                        'scenario':scenario,'seed':seed,'truth':truth,'prediction':result['diagnosis']['category'],
                        'evaluator_state_infidelity':infidelity,'shots':result['cost']['shots'],
                        'evaluations':result['cost']['evaluations'],'executions':result['cost']['circuit_executions'],
                        'runtime_seconds':result['cost']['runtime_seconds'],'experiment_id':eid,
                        'actions':result['cost']['actions'],'artifact_path':str(out/'investigations'/eid),
                        'manifest_digest':digest(store.export(eid)['manifest'])})
    policies={p:summarize([r for r in rows if r['policy']==p]) for p in config['policies']}
    for p,metrics in policies.items():
        metrics.update(executions=sum(r['executions'] for r in rows if r['policy']==p),
                       runtime_seconds=sum(r['runtime_seconds'] for r in rows if r['policy']==p))
    result={'configuration':config,'configuration_digest':digest(config),'split':split,'created_at':timestamp(),
            'implementation_digest':digest({p.name:p.read_text(encoding='utf8') for p in Path(__file__).parent.glob('*.py')}),
            'policies':policies,'rows':rows,
            'limitations':['Configured noise may be invisible in task measurements; category accuracy is not detection power',
                'Fixed circuits and few seeds; intervals are descriptive, not unseen-algorithm generalization',
                'Phase policy still uses privileged exact ideal simulation for logical/noise attribution',
                'All policies have equal ceilings; actual resources differ; recovery evaluated separately']}
    (out/'configuration.json').write_bytes(canonical(config))
    (out/'summary.json').write_bytes(canonical(result))
    (out/'summary.sha256').write_text(digest(result),encoding='ascii')
    return result
