"""Controlled blind investigations over the existing execution/workflow engine."""
import json
import random
import re
import secrets
from pathlib import Path
from typing import Literal
from pydantic import Field,model_validator
from .quantum import Strict,benchmark,contract
from .workflow import RunRequest,observe,investigate
from .storage import ArtifactStore,verify_challenge_export
from .evidence import canonical,digest,identifier,timestamp

STEPS={'observed':'OBSERVED','diagnosed':'DIAGNOSED','freeze':'FROZEN','reveal':'REVEALED'}


class ChallengeRequest(Strict):
    family: Literal['bell','ghz','qft']='bell'
    n_qubits: int | None=Field(default=None,ge=2,le=5,strict=True)
    pool: Literal['core','extended']='core'
    diagnostic_mode: Literal['measurement_only','simulator_assisted']='measurement_only'
    measurement_plan: Literal['z_only','complementary']='complementary'
    shots: int=Field(default=2048,ge=1,le=10000,strict=True)
    max_shots: int=Field(default=12000,ge=2,le=100000,strict=True)
    max_evaluations: int=Field(default=384,ge=2,le=600,strict=True)
    backend: Literal['reference','aer']='aer'
    recover: bool=False
    seed: int | None=Field(default=None,ge=0,lt=2**32,strict=True)

    @model_validator(mode='after')
    def valid(self):
        RunRequest(**{k:v for k,v in self.model_dump().items() if k not in {'pool','seed'}},seed=self.seed or 0)
        return self


def eligible_pool(family,pool):
    values=['clean','remove','phase','readout','gate']
    if pool=='extended':values+=['replace','rewire','mixed']+(['angle'] if family=='qft' else [])
    return values


def measurement_view(record):
    return {key:record[key] for key in ('execution_id','backend_name','output_counts','executed_shots','execution_status') if key in record} | {
        'measurement_basis':record.get('measurement_basis','computational Z')}


def diagnosis_view(value):
    # Never project execution metadata, hidden circuit or evaluator fields.
    fields=('category','reason','policy','capability_mode','supported_discrepancy','discrepancy',
            'phase_probe','readout_probe','state_probe','state_infidelity','hypotheses',
            'evidence_references','confidence','confidence_semantics','limitations')
    return {key:value[key] for key in fields if key in value}


def recovery_view(value):
    if value is None:return None
    result={k:value[k] for k in ('status','edit','candidates_attempted','search_limit','reason','requires_human_review') if k in value}
    result['capability_mode']='privileged simulator candidate selection; not measurement-only recovery'
    if 'verification' in value:
        v=value['verification']
        result['verification']={k:v[k] for k in ('verified_status','validation_method','additional_shots',
            'additional_evaluations','state_fidelity','distribution_comparison','phase_distribution_comparison',
            'original_quality','candidate_quality','original_phase_quality','candidate_phase_quality','reason') if k in v}
    return result


class BlindChallenges:
    def __init__(self,root):
        self.root=Path(root)/'challenges';self.root.mkdir(exist_ok=True)
        # Deliberately outside ordinary experiment history/download namespace.
        self.private=ArtifactStore(self.root/'private-investigations')

    def folder(self,cid):
        if not re.fullmatch(r'challenge_[0-9a-f]{32}',cid):raise ValueError('invalid challenge identifier')
        folder=self.root/cid
        if not folder.is_dir():raise FileNotFoundError(cid)
        return folder

    def _write(self,folder,name,value):
        with (folder/(name+'.json')).open('xb') as stream:stream.write(canonical(value))

    def _public(self,folder,name,value):
        self._write(folder,name,value)
        path=folder/'manifest.json'
        manifest=json.loads(path.read_bytes()) if path.exists() else {'algorithm':'sha256','artifacts':{}}
        manifest['artifacts'][name]=digest(value)
        temporary=folder/(identifier('manifest')+'.tmp')
        with temporary.open('xb') as stream:stream.write(canonical(manifest))
        temporary.replace(path)

    def _bundle(self,cid):
        folder=self.folder(cid)
        manifest=json.loads((folder/'manifest.json').read_bytes())
        documents={name:json.loads((folder/(name+'.json')).read_bytes()) for name in STEPS if (folder/(name+'.json')).exists()}
        state=STEPS[next(reversed(documents))] if documents else 'INVALID'
        return {'kind':'blind_challenge','schema_version':1,'challenge_id':cid,'state':state,
                'documents':documents,'manifest':manifest}

    def _checked(self,cid):
        bundle=self._bundle(cid)
        if not verify_challenge_export(bundle)['valid']:raise ValueError('challenge integrity check failed')
        return bundle

    def get(self,cid):
        bundle=self._checked(cid);docs=bundle['documents']
        result={**docs['observed'],'state':bundle['state'],'diagnosis':None,'recovery':None}
        if 'diagnosed' in docs:
            result.update({k:docs['diagnosed'][k] for k in ('diagnosis','recovery','cost')})
        for key in ('freeze','reveal'):
            if key in docs:result[key]=docs[key]
        result['integrity']=verify_challenge_export(bundle)
        return result

    def start(self,request,replay_of=None):
        seed=request.seed if request.seed is not None else secrets.randbits(32)
        pool=eligible_pool(request.family,request.pool)
        chosen=random.Random(seed).choice(pool)
        run=RunRequest(**{k:v for k,v in request.model_dump().items() if k not in {'pool','seed'}},
                       seed=seed,scenario=chosen,policy='phase')
        records=observe(run)
        cid=identifier('challenge');folder=self.root/cid;folder.mkdir()
        self._write(folder,'setup-private',{'request':run.model_dump(),'challenge_request':request.model_dump(),
                    'selection_seed':seed,'eligible_pool':pool,'records':records,'replay_of':replay_of})
        public_config={k:v for k,v in request.model_dump().items() if k!='seed'}
        public_config['replay_of']=replay_of
        n=run.n_qubits or (2 if run.family=='bell' else 3)
        observed={'challenge_id':cid,'state':'OBSERVED','sequence':1,'created_at':timestamp(),
            'configuration':public_config,'contract':contract(run.family,n).describe(),
            'target_circuit':benchmark(run.family,n).model_dump(mode='json'),
            'target_label':'Declared target; hidden implementation is withheld',
            'measurements':[measurement_view(r) for r in records],
            'limitations':['Controlled local challenge; server administrators can inspect private records',
                'Behavior may suggest a fault, but injected labels/configuration are withheld until a persisted freeze',
                'Simulation only; deterministic selection from a declared eligible pool, not guaranteed success']}
        self._public(folder,'observed',observed)
        return self.get(cid)

    def diagnose(self,cid):
        if self._checked(cid)['state']!='OBSERVED':raise RuntimeError('Diagnosis already completed; prediction cannot be replaced')
        folder=self.folder(cid);setup=json.loads((folder/'setup-private.json').read_bytes())
        result=investigate(RunRequest.model_validate(setup['request']),initial_records=setup['records'])
        eid=self.private.save(result)
        self._write(folder,'completion-private',{'experiment_id':eid})
        cost={k:result['cost'][k] for k in ('shots','evaluations','max_shots','max_evaluations',
            'circuit_executions','exact_state_evaluations','runtime_seconds')}
        cost['actions']=[{k:a[k] for k in ('action','shots')} for a in result['cost']['actions']]
        self._public(folder,'diagnosed',{'challenge_id':cid,'state':'DIAGNOSED','sequence':2,'created_at':timestamp(),
            'observation_digest':digest(self._checked(cid)['documents']['observed']),
            'engine_prediction_digest':result['prediction_digest'],
            'diagnosis':diagnosis_view(result['diagnosis']),'recovery':recovery_view(result['recovery']),'cost':cost})
        return self.get(cid)

    def freeze(self,cid):
        bundle=self._checked(cid)
        if bundle['state'] in {'FROZEN','REVEALED'}:return self.get(cid)
        if bundle['state']!='DIAGNOSED':raise RuntimeError('Run diagnosis before freezing')
        self._public(self.folder(cid),'freeze',{'challenge_id':cid,'state':'FROZEN','sequence':3,
            'created_at':timestamp(),'prediction_digest':digest(bundle['documents']['diagnosed'])})
        return self.get(cid)

    def _private_result(self,cid):
        eid=json.loads((self.folder(cid)/'completion-private.json').read_bytes())['experiment_id']
        return self.private.export(eid)

    def reveal(self,cid):
        bundle=self._checked(cid)
        if bundle['state']=='REVEALED':return self.get(cid)
        if bundle['state']!='FROZEN':raise RuntimeError('Freeze the prediction before revealing evaluator truth')
        from .experiments import evaluator_truth
        exported=self._private_result(cid)
        if not exported['verification']['valid']:raise ValueError('private investigation integrity check failed')
        if exported['investigation']['prediction_digest']!=bundle['documents']['diagnosed']['engine_prediction_digest']:
            raise ValueError('private prediction does not match frozen participant record')
        internal={**exported['investigation'],'evaluation_truth':exported['evaluation']}
        actual,infidelity=evaluator_truth(internal)
        setup=json.loads((self.folder(cid)/'setup-private.json').read_bytes())
        prediction=bundle['documents']['diagnosed']['diagnosis']['category']
        self._public(self.folder(cid),'reveal',{'challenge_id':cid,'state':'REVEALED','sequence':4,'created_at':timestamp(),
            'prediction_digest':bundle['documents']['freeze']['prediction_digest'],
            'evaluation_truth':exported['evaluation'],'evaluator_category':actual,'evaluator_state_infidelity':infidelity,
            'comparison':{'frozen_prediction':prediction,'category_match':prediction==actual,
                'attribution_abstained':prediction in {'INSUFFICIENT_EVIDENCE','UNSUPPORTED'} or
                    (setup['request']['diagnostic_mode']=='measurement_only' and prediction=='MIXED_OR_AMBIGUOUS')},
            'replay':{'selection_seed':setup['selection_seed'],'request':setup['request'],'eligible_pool':setup['eligible_pool']},
            'actual_circuit':exported['investigation']['candidate']})
        return self.get(cid)

    def replay(self,cid):
        if self._checked(cid)['state']!='REVEALED':raise RuntimeError('Reveal before replaying the recorded configuration')
        setup=json.loads((self.folder(cid)/'setup-private.json').read_bytes())
        return self.start(ChallengeRequest.model_validate({**setup['challenge_request'],'seed':setup['selection_seed']}),replay_of=cid)

    def export(self,cid):
        bundle=self._checked(cid)
        if bundle['state']=='REVEALED':bundle['revealed_investigation']=self._private_result(cid)
        bundle['verification']=verify_challenge_export(bundle)
        return bundle

    def list(self):
        rows=[]
        for folder in sorted(self.root.glob('challenge_*'),key=lambda p:p.stat().st_mtime,reverse=True):
            r=self.get(folder.name)
            rows.append({'challenge_id':r['challenge_id'],'state':r['state'],'family':r['configuration']['family'],
                         'diagnostic_mode':r['configuration']['diagnostic_mode'],'created_at':r['created_at']})
        return rows
