"""Cross-instance immediate admission using one conditional private Blob object."""
import secrets,time

class Busy(Exception):pass

class Admission:
    def __init__(self,storage,namespace='global-admission-v1'):self.storage=storage;self.namespace=namespace

    def acquire(self,ceiling):
        from .hosting import empty_state,Conflict
        if type(ceiling) is not int or not 0<=ceiling<=250000:raise ValueError('Hosted per-request shot ceiling is250000')
        state,etag=self.storage.read(self.namespace);now=time.time();day=int(now//86400)
        slots={k:v for k,v in state.get('slots',{}).items() if v>now}
        if slots:raise Busy('Hosted execution is busy. No operation was admitted; retry after the running execution finishes.')
        if state.get('day')!=day:state={**state,'day':day,'reserved_shots':0,'admitted':0}
        if state.get('reserved_shots',0)+ceiling>5000000 or state.get('admitted',0)>=100:raise Busy('Hosted daily admission allowance reached. No new computation was admitted.')
        token=secrets.token_hex(16)
        state={**state,'slots':{token:now+330},'reserved_shots':state.get('reserved_shots',0)+ceiling,'admitted':state.get('admitted',0)+1}
        try:self.storage.write(self.namespace,state,etag)
        except Conflict:raise Busy('Another execution won admission. No computation was started.') from None
        return token

    def release(self,token):
        from .hosting import Conflict
        # Bounded safe CAS retries; no computation is ever resubmitted.
        for _ in range(3):
            state,etag=self.storage.read(self.namespace)
            if token not in state.get('slots',{}):return
            state={**state,'slots':{k:v for k,v in state['slots'].items() if k!=token}}
            try:self.storage.write(self.namespace,state,etag);return
            except Conflict:continue

def request_ceiling(path,body,files):
    """Use server schemas/saved request, never a client-provided cost estimate."""
    from .hosted_operations import validate_direct
    import json,re
    if path.startswith('/api/lab/') and path.endswith('/replay'):
        eid=path.split('/')[-2]
        if not re.fullmatch('experiment_[0-9a-f]{32}',eid):raise ValueError('Invalid replay identity')
        original=json.loads(files[eid+'/investigation.json']);request=original['replay']['request']
        direct='/api/lab/recoveries' if '/recoveries/' in path else '/api/lab/investigations'
        validate_direct(direct,request);return request_ceiling(direct,request,files)
    if path.startswith('/api/challenges/'):
        return 100000 if path.endswith(('/diagnose','/replay')) else 0
    if path in ('/api/lab/investigations','/api/lab/recoveries','/api/experiments','/api/challenges'):
        from .lab import LabRequest
        from .counterfactual import RecoveryRequest
        from .workflow import RunRequest
        from .challenge import ChallengeRequest
        schema={'/api/lab/investigations':LabRequest,'/api/lab/recoveries':RecoveryRequest,'/api/experiments':RunRequest,'/api/challenges':ChallengeRequest}[path]
        request=schema.model_validate(body)
        if request.max_shots>250000 or request.max_evaluations>(160 if path.startswith('/api/lab/') else 600) or getattr(request,'max_seconds',120)>120:raise ValueError('Hosted resource ceiling exceeded; use local mode for larger work')
        return request.max_shots
    return 0
