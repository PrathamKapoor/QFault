"""Localhost API; all science runs through the same CLI-tested workflow."""
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


class ReviewRequest(Strict):
    reviewer: str = Field(min_length=1,max_length=100)
    action: str = Field(pattern="^(acknowledge|reject|request_evidence)$")
    reason: str = Field(min_length=1,max_length=2000)


def create_app(root=None):
    app=FastAPI(title="QFAULT",version="0.1.0")
    store=ArtifactStore(root or os.environ.get("QFAULT_ARTIFACTS","artifacts/investigations"))
    lock=threading.Lock()
    from .challenge import BlindChallenges,ChallengeRequest
    challenges=BlindChallenges(store.root)

    def challenge_action(action,*args,wait=False):
        if not lock.acquire(blocking=wait):raise HTTPException(409,'An investigation is already running')
        try:return action(*args)
        except FileNotFoundError:raise HTTPException(404,'Challenge not found')
        except RuntimeError as exc:raise HTTPException(409,str(exc))
        except (ValueError,KeyError,OSError,ImportError):raise HTTPException(422,'Invalid, unavailable or corrupt challenge; no truth was disclosed')
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


def main():
    import uvicorn
    uvicorn.run("qfault.api:app",host="127.0.0.1",port=8000)


if __name__=="__main__": main()
