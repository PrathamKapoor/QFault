"""HTTP operation bookkeeping, separate from all scientific decisions."""
import hashlib
import json
import re
import time
from .evidence import canonical

OPERATION=re.compile(r'operation_[0-9a-f]{32}')

def fingerprint(method,path,body):
    return hashlib.sha256(canonical({'method':method,'path':path,'body':body})).hexdigest()

def operation_view(oid,value):
    state=value['state']
    if state in ('ADMITTED','RUNNING') and value.get('lease_until',0)<time.time():state='UNKNOWN'
    return {'operation_id':oid,'state':state,'result_id':value.get('result_id'),
            'result_path':value.get('result_path'),'detail':value.get('detail'),
            'created_at':value['created_at'],'status_code':value.get('status_code')}

def validate_direct(path,body):
    """Admission schema validation only; the original route still validates/executes."""
    from .lab import LabRequest
    from .counterfactual import RecoveryRequest
    from .workflow import RunRequest
    from .challenge import ChallengeRequest
    from .api import ReplayOptions,ReviewRequest
    schema={'/api/lab/investigations':LabRequest,'/api/lab/recoveries':RecoveryRequest,
            '/api/experiments':RunRequest,'/api/challenges':ChallengeRequest}.get(path)
    if path.endswith('/replay') and path.startswith('/api/lab/'):schema=ReplayOptions
    if path.endswith('/review'):schema=ReviewRequest
    if schema:schema.model_validate(body)
    if not isinstance(body,dict):raise ValueError('JSON object required')

async def read_body(receive):
    raw=b''
    while True:
        message=await receive()
        if message['type']=='http.disconnect':raise OSError('Connection closed before admission')
        raw+=message.get('body',b'')
        if len(raw)>65536:raise ValueError('Request exceeds byte limit')
        if not message.get('more_body',False):break
    body=json.loads(raw or b'{}',parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    async def replay():return {'type':'http.request','body':raw,'more_body':False}
    return body,replay
