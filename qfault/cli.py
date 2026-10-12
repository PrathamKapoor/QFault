"""Reproducible local CLI; no arbitrary Python or OpenQASM execution."""
import argparse
import json
import sys
from pathlib import Path
from .quantum import benchmark,contract,Circuit,Noise
from .workflow import investigate,RunRequest
from .storage import ArtifactStore
from .evidence import canonical,identifier


def emit(value): print(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))


def demo(store):
    investigations=[]
    for family,scenario,policy in [("bell","clean","evidence"),("bell","remove","evidence"),
             ("bell","readout","evidence"),("ghz","mixed","evidence"),("qft","clean","fixed"),("bell","phase","fixed")]:
        result=investigate(RunRequest(family=family,scenario=scenario,policy=policy,seed=42))
        eid=store.save(result)
        investigations.append({"experiment_id":eid,"family":family,"scenario":scenario,
                               "diagnosis":result["diagnosis"]["category"],
                               "recovery_status":result["recovery"]["status"] if result["recovery"] else None,
                               "shots":result["cost"]["shots"],"evaluations":result["cost"]["evaluations"]})
    scratch=investigate(RunRequest(seed=99,recover=False))
    eid=store.save(scratch)
    path=store.folder(eid)/"investigation.json"
    before=path.read_bytes()
    original=store.verify(eid)["valid"]
    try:
        altered=json.loads(before)
        first=altered["executions"][0]["output_counts"]
        first[next(iter(first))]+=1
        path.write_bytes(canonical(altered))
        tampered=store.verify(eid)["valid"]
    finally: path.write_bytes(before)
    restored=store.verify(eid)["valid"]
    return {"investigations":investigations,"integrity_demonstration":{"original":original,"tampered":tampered,"restored":restored},
            "integrity_throwaway_experiment":eid,"backend_mode":"Qiskit reference backend; optional Aer is selected separately"}


def main(argv=None):
    parser=argparse.ArgumentParser(prog="qfault")
    parser.add_argument("--store",default="artifacts/investigations")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("circuits")
    p=sub.add_parser("contract");p.add_argument("family",choices=["bell","ghz","qft"]);p.add_argument("--qubits",type=int)
    p=sub.add_parser("run")
    p.add_argument("--family",default="bell",choices=["bell","ghz","qft"])
    p.add_argument("--scenario",default="clean",choices=["clean","readout","gate","remove","replace","angle","rewire","mixed","phase"])
    p.add_argument("--policy",default="fixed",choices=["evidence","fixed","random","threshold","phase"])
    p.add_argument("--qubits",type=int);p.add_argument("--shots",type=int,default=2048);p.add_argument("--seed",type=int,default=42)
    p.add_argument("--max-shots",type=int,default=12000);p.add_argument("--max-evaluations",type=int,default=384)
    p.add_argument("--backend",choices=["reference","aer"],default="reference")
    p.add_argument("--no-recovery",action="store_true")
    p.add_argument('--diagnostic-mode',choices=['simulator_assisted','measurement_only'],default='simulator_assisted')
    p.add_argument('--measurement-plan',choices=['z_only','complementary'],default='complementary')
    for name in ["inspect","analyze","recovery","verify"]:
        p=sub.add_parser(name);p.add_argument("experiment_id")
    p=sub.add_parser("export");p.add_argument("experiment_id");p.add_argument("destination")
    p=sub.add_parser("review");p.add_argument("experiment_id");p.add_argument("--reviewer",required=True);p.add_argument("--reason",required=True);p.add_argument("--action",default="acknowledge",choices=["acknowledge","reject","request_evidence"])
    p=sub.add_parser("verify-repair");p.add_argument("circuit_json");p.add_argument("--family",required=True,choices=["bell","ghz","qft"]);p.add_argument("--shots",type=int,default=2048);p.add_argument("--seed",type=int,default=10007)
    sub.add_parser("demo")
    p=sub.add_parser("benchmark");p.add_argument("--out",required=True)
    p=sub.add_parser("evaluate");p.add_argument("--out",required=True);p.add_argument("--split",choices=["development","final","low_shot_control"],required=True);p.add_argument("--config",default="configs/diagnostic-evaluation.json")
    p=sub.add_parser("verify-report");p.add_argument("report_json")
    sub.add_parser("serve")
    args=parser.parse_args(argv)
    try:
        if args.command=="circuits":
            emit([{"family":f,"qubits":n,"contract_id":contract(f,n).contract_id,"circuit_id":benchmark(f,n).circuit_id} for f,n in [("bell",2),("ghz",3),("qft",3)]])
        elif args.command=="contract": emit(contract(args.family,args.qubits or (2 if args.family=="bell" else 3)).describe())
        elif args.command=="verify-report":
            from .storage import verify_export
            result=verify_export(json.loads(Path(args.report_json).read_bytes()))
            emit(result)
            return 0 if result["valid"] else 1
        elif args.command=="serve":
            from .api import main as serve
            serve()
        elif args.command=="evaluate":
            from .experiments import compare_policies
            result=compare_policies(json.loads(Path(args.config).read_bytes()),args.out,args.split)
            emit({"destination":args.out,"split":args.split,"policies":result["policies"]})
        elif args.command=="benchmark":
            from .experiments import benchmark_run
            result=benchmark_run(args.out)
            emit({"destination":args.out,"policies":result["policies"],"recovery":result["recovery"]})
        elif args.command=="verify-repair":
            from .recovery import IndependentVerifier
            from .diagnostics import ExecutionBudget
            c=Circuit.model_validate_json(Path(args.circuit_json).read_bytes())
            result=IndependentVerifier().verify(c,contract(args.family,c.n_qubits),Noise(),args.shots,args.seed,ExecutionBudget(args.shots,2))
            emit(result)
            return 0 if result["verified_status"]=="VERIFIED" else 1
        else:
            store=ArtifactStore(args.store)
            if args.command=="run":
                result=investigate(RunRequest(family=args.family,n_qubits=args.qubits,scenario=args.scenario,policy=args.policy,
                      shots=args.shots,seed=args.seed,max_shots=args.max_shots,max_evaluations=args.max_evaluations,recover=not args.no_recovery,backend=args.backend,
                      diagnostic_mode=args.diagnostic_mode,measurement_plan=args.measurement_plan))
                eid=store.save(result);emit(store.load(eid))
            elif args.command=="demo": emit(demo(store))
            elif args.command=="inspect": emit(store.load(args.experiment_id))
            elif args.command=="analyze": emit(store.load(args.experiment_id)["diagnosis"])
            elif args.command=="recovery": emit(store.load(args.experiment_id)["recovery"])
            elif args.command=="verify":
                result=store.verify(args.experiment_id);emit(result)
                return 0 if result["valid"] else 1
            elif args.command=="review": emit(store.review(args.experiment_id,args.reviewer,args.action,args.reason))
            elif args.command=="export":
                with Path(args.destination).open("xb") as stream: stream.write(canonical(store.export(args.experiment_id)))
                emit({"exported":args.destination})
        return 0
    except (ValueError,OSError,RuntimeError,ImportError) as exc:
        print(json.dumps({"status":"FAILED","error":str(exc)}),file=sys.stderr)
        return 1


if __name__=="__main__": sys.exit(main())
