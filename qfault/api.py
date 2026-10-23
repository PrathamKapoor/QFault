"""Localhost API; all science runs through the same CLI-tested workflow."""
import json
import math
import os
import threading
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from .quantum import Strict,contract
from .workflow import RunRequest,investigate
from .storage import ArtifactStore
from .evidence import canonical,identifier,timestamp


class LocalRequestBoundary:
    """Enforce loopback host/same-origin mutation semantics, without proxy trust."""
    def __init__(self,app,testing=False):
        self.app=app
        self.allowed={'localhost','127.0.0.1','::1'} | ({'testserver'} if testing else set())

    async def __call__(self,scope,receive,send):
        if scope['type']!='http': return await self.app(scope,receive,send)
        from urllib.parse import urlsplit
        hosts=[v for k,v in scope.get('headers',[]) if k.lower()==b'host']
        try:
            if len(hosts)!=1: raise ValueError('Host required')
            host=hosts[0].decode('ascii').lower()
            parsed=urlsplit('http://'+host)
            if parsed.hostname not in self.allowed or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
                raise ValueError('Invalid local host')
            if parsed.port is not None and not 1<=parsed.port<=65535: raise ValueError('Invalid port')
        except (ValueError,UnicodeError):
            return await JSONResponse({'detail':'Local host required'},status_code=400)(scope,receive,send)
        if scope.get('method') not in ('GET','HEAD','OPTIONS'):
            origins=[v for k,v in scope.get('headers',[]) if k.lower()==b'origin']
            expected=(scope.get('scheme','http')+'://'+host).encode('ascii')
            if origins and (len(origins)!=1 or origins[0]!=expected):
                return await JSONResponse({'detail':'Same-origin local request required'},status_code=403)(scope,receive,send)
        await self.app(scope,receive,send)


class RequestBodyLimit:
    """Bound actual API bytes before JSON parsing, including chunked requests."""
    def __init__(self, app, limit=65536):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or not scope.get('path', '').startswith('/api/'):
            return await self.app(scope, receive, send)
        headers = dict(scope.get('headers', []))
        lengths = [value for key, value in scope.get('headers', []) if key.lower() == b'content-length']
        if any(not value.isdigit() or len(value) > 20 for value in lengths):
            return await JSONResponse({'detail': 'Invalid Content-Length'}, status_code=400)(scope, receive, send)
        if len({int(value) for value in lengths}) > 1:
            return await JSONResponse({'detail': 'Conflicting Content-Length'}, status_code=400)(scope, receive, send)
        if any(int(value) > self.limit for value in lengths):
            return await JSONResponse({'detail': 'Request body exceeds 64 KiB'}, status_code=413)(scope, receive, send)
        messages, size = [], 0
        while True:
            message = await receive()
            size += len(message.get('body', b''))
            if size > self.limit:
                return await JSONResponse({'detail': 'Request body exceeds 64 KiB'}, status_code=413)(scope, receive, send)
            messages.append(message)
            if message['type'] == 'http.disconnect' or not message.get('more_body', False):
                break
        body = b''.join(message.get('body', b'') for message in messages)
        content_type = headers.get(b'content-type', b'application/json').split(b';', 1)[0].strip().lower()
        if body and messages[-1]['type'] != 'http.disconnect':
            if content_type != b'application/json' and not (content_type.startswith(b'application/') and content_type.endswith(b'+json')):
                return await JSONResponse({'detail': 'API requests require JSON'}, status_code=422)(scope, receive, send)
            def reject_constant(value):
                raise ValueError('Non-finite JSON number')
            def finite_float(value):
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError('Non-finite JSON number')
                return number
            try:
                parsed = json.loads(body, parse_constant=reject_constant, parse_float=finite_float)
                pending_values = [(parsed, 0)]
                while pending_values:
                    value, depth = pending_values.pop()
                    if depth > 64:
                        raise ValueError('JSON nesting exceeds 64 levels')
                    if isinstance(value, dict):
                        for key in value:
                            key.encode('utf-8')
                        pending_values.extend((child, depth + 1) for child in value.values())
                    elif isinstance(value, list):
                        pending_values.extend((child, depth + 1) for child in value)
                    elif isinstance(value, str):
                        value.encode('utf-8')
            except (ValueError, UnicodeError, RecursionError):
                return await JSONResponse({'detail': 'Invalid JSON body'}, status_code=422)(scope, receive, send)
        pending = iter(messages)

        async def replay():
            return next(pending, None) or await receive()

        await self.app(scope, replay, send)


class ReviewRequest(Strict):
    reviewer: str = Field(min_length=1,max_length=100)
    action: str = Field(pattern="^(acknowledge|reject|request_evidence)$")
    reason: str = Field(min_length=1,max_length=2000)


class ReplayOptions(Strict):
    seed: int | None = Field(default=None, ge=0, lt=2**32, strict=True)


def create_app(root=None):
    app=FastAPI(title="QFAULT",version="0.1.0")
    app.add_middleware(RequestBodyLimit)
    app.add_middleware(LocalRequestBoundary,testing=root is not None)
    store=ArtifactStore(root or os.environ.get("QFAULT_ARTIFACTS","artifacts/investigations"))
    lock=threading.Lock()
    from .challenge import BlindChallenges,ChallengeRequest,ChallengeConflict
    challenges=BlindChallenges(store.root)

    def challenge_action(action,*args,wait=False):
        # Reads (history/report) hold the lock briefly; mutations wait for them rather than racing to 409.
        if not lock.acquire(timeout=-1 if wait else 30):raise HTTPException(409,'An investigation is already running')
        try:return action(*args)
        except FileNotFoundError:raise HTTPException(404,'Challenge not found')
        except ChallengeConflict as exc:raise HTTPException(409,str(exc))
        except (RuntimeError,ValueError,KeyError,OSError,ImportError):raise HTTPException(422,'Invalid, unavailable or corrupt challenge; no truth was disclosed')
        finally:lock.release()

    @app.post('/api/challenges',status_code=201)
    def start_challenge(request:ChallengeRequest):return challenge_action(challenges.start,request)

    @app.get('/api/challenges')
    def challenge_history():return challenge_action(challenges.list,wait=True)

    @app.get('/api/challenges/{cid}')
    def get_challenge(cid:str):return challenge_action(challenges.get,cid,wait=True)

    @app.post('/api/challenges/{cid}/diagnose')
    def diagnose_challenge(cid:str):return challenge_action(challenges.diagnose,cid)

    @app.post('/api/challenges/{cid}/freeze')
    def freeze_challenge(cid:str):return challenge_action(challenges.freeze,cid)

    @app.post('/api/challenges/{cid}/reveal')
    def reveal_challenge(cid:str):return challenge_action(challenges.reveal,cid)

    @app.post('/api/challenges/{cid}/replay',status_code=201)
    def replay_challenge(cid:str):return challenge_action(challenges.replay,cid)

    @app.get('/api/challenges/{cid}/report')
    def challenge_report(cid:str):
        return JSONResponse(challenge_action(challenges.export,cid,wait=True),headers={'Content-Disposition':f'attachment; filename="{cid}.json"'})

    @app.get('/api/challenges/{cid}/verification')
    def challenge_verification(cid:str):return challenge_action(challenges.export,cid,wait=True)['verification']

    def existing(eid):
        try: return store.load(eid)
        except FileNotFoundError: raise HTTPException(404,"Investigation not found")
        except (ValueError,KeyError): raise HTTPException(422,"Invalid or corrupt investigation")

    @app.get("/api/health")
    def health():
        try:
            import qiskit_aer
            aer={"version":qiskit_aer.__version__,"status":"importable; select backend=aer to execute"}
        except (ImportError,OSError) as exc:
            aer={"status":"unavailable","error":str(exc)}
        return {"status":"ok","mode":"local simulation","qiskit":__import__("qiskit").__version__,
                "aer":aer,"default_backend":"reference","supported_backends":["reference","aer"],"signing":"unavailable"}

    @app.get("/api/circuits")
    def circuits():
        return [{"family":f,"default_qubits":n,"supported_qubits":[2] if f=="bell" else [2,3,4,5],
                 "contract":contract(f,n).describe()} for f,n in [("bell",2),("ghz",3),("qft",3)]]

    @app.get("/api/contracts/{family}/{n}")
    def get_contract(family:str,n:int):
        try: return contract(family,n).describe()
        except ValueError: raise HTTPException(422,"Unsupported circuit contract")

    @app.get("/api/benchmark")
    def benchmark_summary():
        import json
        path=Path(__file__).resolve().parents[1]/"benchmarks"/"results.json"
        if not path.exists(): raise HTTPException(404,"No recorded benchmark exists")
        data=json.loads(path.read_bytes())
        return {k:v for k,v in data.items() if k!="rows"}

    @app.get('/api/research')
    def current_research():
        import hashlib
        root=Path(__file__).resolve().parents[1]
        path=root/'benchmarks/external-holdout-v1/summary.json'
        if not path.is_file(): raise HTTPException(404,'Current research summary is unavailable')
        data=json.loads(path.read_bytes())
        recovery={}
        for policy in ('conservative','point_discrepancy'):
            row=data['recovery_summaries'][policy]
            recovery[policy]={'runs':row['runs'],'eligible':row['eligible'],
                'verified':row['outcomes'].get('VERIFIED_UNDER_DECLARED_CONTRACT',0),
                'rejected':row['outcomes'].get('REJECTED',0),'shots':row['shots'],
                'executions':row['executions'],'noise_only_proposals':row['noise_only_proposals']}
        reports=root/'benchmarks/external-holdout-v1/reports.jsonl.gz'
        conservative,point=recovery['conservative'],recovery['point_discrepancy']
        return {'protocol':data['protocol']['name'],'source_commit':data['execution_revision'],
            'summary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'architectures':data['architecture_count'],'recovery':recovery,
            'comparison':{'equal_verified_yield':conservative['verified']==point['verified'],
                'relative_shot_reduction':(point['shots']-conservative['shots'])/point['shots'] if point['shots'] else None},
            'evidence':{'available':reports.is_file(),'scope':'Current external study; availability is not a fresh integrity audit',
                'verification_command':'python -m scripts.verify_external_results benchmarks/external-holdout-v1/summary.json'},
            'limitations':['Controlled local simulation; repeated seeds are not independent circuit families',
                'One declared input/contract; a verified intervention does not identify the causal origin',
                'Historical template/lab/target studies have separate evidence-availability records']}

    @app.get('/api/guided-demo')
    def guided_demo_inputs():
        from .demo import demo_catalog
        try:return demo_catalog()
        except (OSError,ValueError,KeyError,TypeError):
            raise HTTPException(503,'Guided demonstration inputs are unavailable or inconsistent; no execution occurred')

    @app.get("/api/benchmark/report")
    def benchmark_report():
        path=Path(__file__).resolve().parents[1]/"benchmarks"/"results.json"
        if not path.exists(): raise HTTPException(404,"No recorded benchmark exists")
        return FileResponse(path,media_type="application/json",filename="qfault-benchmark.json")

    @app.get("/api/evaluation")
    def final_evaluation():
        import json
        path=Path(__file__).resolve().parents[1]/"benchmarks"/"diagnostic-final.json"
        if not path.exists(): raise HTTPException(404,"No frozen final evaluation exists")
        data=json.loads(path.read_bytes())
        return {k:v for k,v in data.items() if k!="rows"}

    @app.get("/api/evaluation/report")
    def final_evaluation_report():
        path=Path(__file__).resolve().parents[1]/"benchmarks"/"diagnostic-final.json"
        if not path.exists(): raise HTTPException(404,"No frozen final evaluation exists")
        return FileResponse(path,media_type="application/json",filename="qfault-frozen-evaluation.json")

    from .lab import LabRequest,investigate_lab,feasibility
    from .lab_corpus import cases as lab_cases

    @app.get("/api/lab/examples")
    def lab_examples():
        picks={}
        for c in lab_cases("development"):
            if c["environment"]=="ideal" and c["modification"] in {"clean","remove_last"} and c["seed"]==101:
                picks[c["family"]+"-"+c["modification"]]=c
        return [{"id":k,"title":v["circuit"]["name"],"circuit":v["circuit"],"contract":v["contract"],
                 "provenance":"Contract declared from the reference design by exact Qiskit evaluation, not from this candidate"}
                for k,v in picks.items()]

    @app.post("/api/lab/validate")
    def lab_validate(request:LabRequest):
        return {"valid":True,"circuit_id":request.circuit.circuit_id,"executed_subject":request.circuit.subject().model_dump(mode="json"),
                "circuit_diagram":str(request.circuit.subject().native().draw(output="text")),
                "feasibility":feasibility(request.circuit,request.contract,request),
                "conventions":"Bitstrings/Pauli strings use Qiskit order: leftmost character = highest qubit"}

    def run_lab(request, replay_of=None, semantics=None):
        if not lock.acquire(blocking=False): raise HTTPException(409,"An investigation is already running")
        try:
            result=investigate_lab(request)
            if replay_of:
                result['replay'].update(source_experiment_id=replay_of,semantics=semantics)
            return store.load(store.save(result))
        except (ValueError,RuntimeError,ImportError,OSError) as exc:
            failure={"failure_id":identifier("failure"),"created_at":timestamp(),"configuration":request.model_dump(mode="json"),
                     "execution_status":"FAILED","failure_reason":str(exc)}
            failures=store.root/"failures";failures.mkdir(exist_ok=True)
            (failures/(failure["failure_id"]+".json")).write_bytes(canonical(failure))
            raise HTTPException(422,"Investigation failed; error preserved in local failure artifact")
        finally: lock.release()

    @app.post("/api/lab/investigations",status_code=201)
    def lab_investigate(request:LabRequest): return run_lab(request)

    from .counterfactual import RecoveryRequest,recover

    def run_recovery(request, replay_of=None, semantics=None):
        if not lock.acquire(blocking=False): raise HTTPException(409,"An investigation is already running")
        try:
            result=recover(request)
            if replay_of:
                result['replay'].update(source_experiment_id=replay_of,semantics=semantics)
            return store.load(store.save(result))
        except (ValueError,RuntimeError,ImportError,OSError) as exc:
            failure={"failure_id":identifier("failure"),"created_at":timestamp(),
                     "configuration":request.model_dump(mode="json"),"execution_status":"FAILED",
                     "failure_reason":str(exc),"investigation_kind":"counterfactual_recovery"}
            failures=store.root/'failures';failures.mkdir(exist_ok=True)
            (failures/(failure['failure_id']+'.json')).write_bytes(canonical(failure))
            raise HTTPException(422,"Recovery execution failed; failure recorded, no verified repair claimed") from exc
        finally: lock.release()

    @app.post('/api/lab/recoveries',status_code=201)
    def measured_recovery(request:RecoveryRequest): return run_recovery(request)

    @app.post('/api/lab/recoveries/{eid}/replay',status_code=201)
    def replay_recovery(eid:str, options:ReplayOptions=ReplayOptions()):
        original=existing(eid)
        if original.get('investigation_kind')!='counterfactual_recovery': raise HTTPException(422,'Not a measured recovery')
        try: request=RecoveryRequest.model_validate(original['replay']['request'])
        except (ValueError,KeyError,TypeError): raise HTTPException(422,'Saved replay request is invalid')
        semantics='new_seed_rerun' if options.seed is not None and options.seed!=request.seed else 'deterministic_replay'
        if options.seed is not None: request=request.model_copy(update={'seed':options.seed})
        return run_recovery(request,replay_of=eid,semantics=semantics)

    @app.post("/api/lab/investigations/{eid}/replay",status_code=201)
    def lab_replay(eid:str, options:ReplayOptions=ReplayOptions()):
        original=existing(eid)
        if original.get("investigation_kind")!="custom_circuit": raise HTTPException(422,"Not a custom-circuit investigation")
        try: request=LabRequest.model_validate(original['replay']['request'])
        except (ValueError,KeyError,TypeError): raise HTTPException(422,'Saved replay request is invalid')
        semantics='new_seed_rerun' if options.seed is not None and options.seed!=request.seed else 'deterministic_replay'
        if options.seed is not None: request=request.model_copy(update={'seed':options.seed})
        return run_lab(request,replay_of=eid,semantics=semantics)

    @app.get("/api/experiments")
    def list_experiments(): return store.list()

    @app.post("/api/experiments",status_code=201)
    def run_experiment(request:RunRequest):
        if not lock.acquire(blocking=False): raise HTTPException(409,"An investigation is already running")
        try:
            result=investigate(request)
            eid=store.save(result)
            return store.load(eid)
        except (ValueError,RuntimeError,ImportError,OSError) as exc:
            failure={"failure_id":identifier("failure"),"created_at":timestamp(),"configuration":request.model_dump(),
                     "execution_status":"FAILED","failure_reason":str(exc)}
            failures=store.root/"failures"
            failures.mkdir(exist_ok=True)
            (failures/(failure["failure_id"]+".json")).write_bytes(canonical(failure))
            raise HTTPException(422,"Investigation failed; error preserved in local failure artifact")
        finally: lock.release()

    @app.get("/api/experiments/{eid}")
    def get_experiment(eid:str): return existing(eid)

    @app.get("/api/experiments/{eid}/verification")
    def verify(eid:str):
        try: folder=store.folder(eid)
        except ValueError: raise HTTPException(422,"Invalid experiment identifier")
        if not folder.is_dir(): raise HTTPException(404,"Investigation not found")
        return store.verify(eid)

    @app.get("/api/experiments/{eid}/report")
    def report(eid:str):
        existing(eid)
        return JSONResponse(store.export(eid),headers={"Content-Disposition":f'attachment; filename="{eid}.json"'})

    @app.post("/api/experiments/{eid}/review",status_code=201)
    def review(eid:str,request:ReviewRequest):
        existing(eid)
        try:
            with lock: return store.review(eid,request.reviewer,request.action,request.reason)
        except ValueError as exc: raise HTTPException(409,str(exc))

    web=Path(__file__).resolve().parents[1]/"web"/"dist"
    if web.is_dir(): app.mount("/",StaticFiles(directory=web,html=True),name="web")
    else:
        @app.get("/")
        def missing_web(): raise HTTPException(503,"Build the web interface with npm --prefix web run build")
    return app


app=create_app()


def main(port=8000):
    """Serve on localhost only. Fails fast with a clear message if the port is already taken."""
    import socket,sys,uvicorn
    probe=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try: probe.bind(("127.0.0.1",port))
    except OSError:
        print(f"QFAULT cannot start: 127.0.0.1:{port} is already in use. Stop the other server or pass --port.",file=sys.stderr)
        raise SystemExit(2)
    finally: probe.close()
    print(f"QFAULT serving http://127.0.0.1:{port}/ (pid {__import__('os').getpid()}); Ctrl+C stops it.",flush=True)
    uvicorn.run("qfault.api:app",host="127.0.0.1",port=port)


if __name__=="__main__": main()
