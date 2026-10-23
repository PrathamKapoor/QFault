"""Opt-in Vercel boundary; the local API and scientific engine remain unchanged."""
import asyncio
import hashlib
import hmac
from http.cookies import SimpleCookie,CookieError
import json
import os
from pathlib import Path,PurePosixPath
import re
import secrets
import tempfile
import time
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler

from fastapi.responses import JSONResponse
from .api import create_app
from .evidence import canonical
from .hosted_operations import OPERATION,fingerprint,operation_view,validate_direct,read_body

MAX_STATE=32*1024*1024
MAX_RESPONSE=4*1024*1024
COOKIE='__Host-qfault-session'
AGE=30*86400


class Conflict(Exception):pass


def empty_state():
    return {'schema_version':1,'operations':0,'lease_until':0,'files':{}}


def member(name):
    parts=PurePosixPath(name).parts
    return (bool(parts) and len(name)<240 and not name.startswith('/')
            and all(re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*',p) and p not in ('.','..') for p in parts)
            and '\\' not in name and name.endswith('.json'))


def restore(root,files):
    if not isinstance(files,dict) or len(files)>1000:raise ValueError('Invalid snapshot membership')
    total=0
    for name,body in files.items():
        if not isinstance(name,str) or not member(name) or not isinstance(body,str):raise ValueError('Unsafe snapshot member')
        raw=body.encode('utf8');total+=len(raw)
        if total>MAX_STATE:raise ValueError('Snapshot exceeds limit')
        json.loads(raw)
        path=root/name
        if not path.resolve().is_relative_to(root.resolve()):raise ValueError('Snapshot path escaped root')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)


def snapshot(root):
    files={};total=0
    for path in root.rglob('*'):
        if path.is_symlink():raise ValueError('Linked artifact rejected')
        if not path.is_file():continue
        name=path.relative_to(root).as_posix()
        if not member(name):raise ValueError('Unexpected artifact')
        if path.stat().st_size>MAX_STATE:raise ValueError('Artifact exceeds limit')
        raw=path.read_bytes();total+=len(raw)
        if total>MAX_STATE or len(files)>=1000:raise ValueError('Snapshot exceeds limit')
        files[name]=raw.decode('utf8')
    return files


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


class BlobState:
    """Small Blob HTTP v12 client; no credentials in URLs, logs or responses."""
    def __init__(self,token=None,request=None):
        self.token=token or os.environ.get('BLOB_READ_WRITE_TOKEN','')
        self.request=request or self._request

    def _request(self,method,url,body=None,headers=None,limit=MAX_STATE):
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.username or not (parsed.hostname=='blob.vercel-storage.com' or (parsed.hostname or '').endswith('.private.blob.vercel-storage.com')):
            raise OSError('Invalid storage endpoint')
        if not self.token:raise OSError('Private storage is not configured')
        request=Request(url,data=body,headers={'Authorization':'Bearer '+self.token,'x-api-version':'12',**(headers or {})},method=method)
        try:
            with build_opener(NoRedirect()).open(request,timeout=25) as response:
                raw=response.read(limit+1);meta={k.lower():v for k,v in response.headers.items()}
        except HTTPError as exc:
            if exc.code in (409,412):raise Conflict() from None
            if exc.code==404:return None,{}
            raise OSError('Private storage request failed') from None
        except (URLError,TimeoutError):raise OSError('Private storage unavailable') from None
        if len(raw)>limit:raise OSError('Private storage exceeds limit')
        return raw,meta

    def read(self,sid):
        name='sessions/'+sid+'.json'
        raw,_=self.request('GET','https://blob.vercel-storage.com?'+urlencode({'url':name}),limit=8192)
        if raw is None:return empty_state(),None
        meta=json.loads(raw);url=meta['url'];etag=meta['etag']
        if not urlsplit(url).hostname.endswith('.private.blob.vercel-storage.com'):raise OSError('Invalid private snapshot URL')
        for _ in range(3):
            body,headers=self.request('GET',url+'?'+urlencode({'cache':'0','qfault_revision':secrets.token_hex(12)}),headers={'Cache-Control':'no-cache'})
            if body is not None and headers.get('etag')==etag:
                state=json.loads(body)
                if (type(state.get('schema_version')) is not int or state['schema_version']!=1
                    or type(state.get('operations')) is not int or not 0<=state['operations']<=64
                    or not isinstance(state.get('lease_until'),(int,float)) or not isinstance(state.get('files'),dict)):
                    raise OSError('Invalid stored session')
                return state,etag
        raise OSError('Current private snapshot not available')

    def write(self,sid,state,etag):
        raw=canonical(state)
        if len(raw)>MAX_STATE:raise ValueError('Session storage limit reached')
        headers={'content-type':'application/json','x-content-type':'application/json',
                 'x-vercel-blob-access':'private','x-add-random-suffix':'0',
                 'x-allow-overwrite':'1' if etag else '0','x-cache-control-max-age':'60'}
        if etag:headers['x-if-match']=etag
        body,_=self.request('PUT','https://blob.vercel-storage.com?'+urlencode({'pathname':'sessions/'+sid+'.json'}),body=raw,headers=headers,limit=8192)
        if body is None:raise OSError('Private storage save unavailable')
        result=json.loads(body)
        if not result.get('etag'):raise OSError('Missing storage revision')
        return result['etag']


class HostedApp:
    def __init__(self,storage=None,secret=None,hosts=None):
        self.storage=storage or BlobState()
        self.secret=secret or os.environ.get('QFAULT_SESSION_KEY','')
        self.hosts=hosts or {v.lower() for v in [os.environ.get(k,'') for k in ('VERCEL_URL','VERCEL_BRANCH_URL','VERCEL_PROJECT_PRODUCTION_URL')]+os.environ.get('QFAULT_PUBLIC_HOSTS','').split(',') if v}

    def session(self,headers):
        now=int(time.time());cookie=SimpleCookie()
        try:
            cookie.load(headers.get('cookie',''));value=cookie[COOKIE].value
            sid,issued,signature=value.split('.')
            payload=sid+'.'+issued
            if (not re.fullmatch('[0-9a-f]{64}',sid) or not issued.isdigit()
                or not 0<=now-int(issued)<=AGE
                or not hmac.compare_digest(signature,hmac.new(self.secret.encode(),payload.encode(),hashlib.sha256).hexdigest())):raise ValueError()
            return sid,value
        except (CookieError,KeyError,ValueError):
            sid=secrets.token_hex(32);payload=sid+'.'+str(now)
            return sid,payload+'.'+hmac.new(self.secret.encode(),payload.encode(),hashlib.sha256).hexdigest()

    async def __call__(self,scope,receive,send):
        if scope['type']=='lifespan':
            while True:
                message=await receive()
                if message['type']=='lifespan.startup':await send({'type':'lifespan.startup.complete'})
                elif message['type']=='lifespan.shutdown':await send({'type':'lifespan.shutdown.complete'});return
        if scope['type']!='http':return
        async def error(status,detail):await JSONResponse({'detail':detail},status_code=status,headers={'Cache-Control':'private, no-store'})(scope,receive,send)
        raw_headers=scope.get('headers',[])
        try:
            if len([v for k,v in raw_headers if k.lower()==b'host'])!=1:raise ValueError()
            headers={k.decode().lower():v.decode() for k,v in raw_headers};host=headers.get('host','').lower()
            if host not in self.hosts:raise ValueError()
        except (ValueError,UnicodeError):return await error(400,'Configured deployment host required')
        if scope['method'] not in ('GET','HEAD','OPTIONS'):
            origins=[v for k,v in raw_headers if k.lower()==b'origin']
            if (origins and (len(origins)!=1 or origins[0]!=('https://'+host).encode())) or headers.get('sec-fetch-site')=='cross-site':
                return await error(403,'Same-origin request required')
        if len(self.secret)<32:return await error(503,'Hosted session configuration is unavailable')
        sid,cookie=self.session(headers)
        path=scope.get('path','');method=scope['method']
        cookie_header=f'{COOKIE}={cookie}; Path=/; Max-Age={AGE}; Secure; HttpOnly; SameSite=Lax'
        if method=='POST' and path=='/api/hosted-session':
            return await JSONResponse({'hosting':{'persistence':'private Vercel Blob','session_scope':'browser cookie','operation_limit':64}},headers={'Set-Cookie':cookie_header,'Cache-Control':'private, no-store'})(scope,receive,send)
        stateless=(method in ('GET','HEAD') and path in ('/api/health','/api/research','/api/guided-demo')) or (method=='POST' and path=='/api/lab/validate')
        mutate=method not in ('GET','HEAD','OPTIONS') and not stateless
        previous=None;lease_etag=None;operation=None;oid=None
        try:
            state,etag=(empty_state(),None) if stateless else await asyncio.to_thread(self.storage.read,sid)
            if method=='GET' and path.startswith('/api/operations/'):
                oid=path.rsplit('/',1)[-1]
                if not OPERATION.fullmatch(oid) or oid not in state.get('requests',{}):return await error(404,'Operation not found in this session')
                return await JSONResponse(operation_view(oid,state['requests'][oid]),headers={'Cache-Control':'private, no-store'})(scope,receive,send)
            if mutate:
                try:
                    body,receive=await read_body(receive)
                    validate_direct(path,body)
                except (ValueError,UnicodeError):return await error(422,'Invalid request; no execution admitted')
                ids=[v.decode() for k,v in raw_headers if k.lower()==b'x-qfault-operation']
                oid=ids[0] if len(ids)==1 else 'operation_'+secrets.token_hex(16)
                if len(ids)>1 or not OPERATION.fullmatch(oid):return await error(422,'Invalid operation identity')
                bound=fingerprint(method,path,body);existing=state.get('requests',{}).get(oid)
                if existing:
                    if existing['fingerprint']!=bound:return await error(409,'Operation ID is bound to a different request')
                    view=operation_view(oid,existing)
                    if view['state']!='COMPLETED':return await JSONResponse(view,status_code=202 if view['state'] in ('RUNNING','ADMITTED','UNKNOWN') else existing.get('status_code',422),headers={'Cache-Control':'private, no-store'})(scope,receive,send)
                    if existing.get('result_id','').startswith('experiment_'):
                        from .storage import ArtifactStore
                        with tempfile.TemporaryDirectory(prefix='qfault-recover-') as folder:
                            root=Path(folder);restore(root,state['files']);result=ArtifactStore(root).load(existing['result_id'])
                    else:result=existing['response']
                    return await JSONResponse(result,status_code=existing['status_code'],headers={'Cache-Control':'private, no-store','X-QFault-Operation':oid})(scope,receive,send)
                if state['lease_until']>time.time():return await error(409,'Another operation is running in this browser session. Recover its identity before submitting.')
                if state['operations']>=64:return await error(429,'This hosted session reached its 64-operation limit. Export important reports.')
                previous=state
                operation={'fingerprint':bound,'state':'RUNNING','created_at':time.time(),'lease_until':time.time()+310}
                state={**state,'operations':state['operations']+1,'lease_until':operation['lease_until'],
                       'requests':{**state.get('requests',{}),oid:operation}}
                lease_etag=await asyncio.to_thread(self.storage.write,sid,state,etag)
            with tempfile.TemporaryDirectory(prefix='qfault-hosted-') as folder:
                root=Path(folder);restore(root,state['files'])
                internal={**scope,'scheme':'http','headers':[(k,v) for k,v in raw_headers if k.lower() not in (b'host',b'origin')]+[(b'host',b'127.0.0.1')]}
                if 'origin' in headers:internal['headers'].append((b'origin',b'http://127.0.0.1'))
                messages=[];response_bytes=0
                async def capture(message):
                    nonlocal response_bytes
                    response_bytes+=len(message.get('body',b''))
                    if response_bytes>MAX_RESPONSE:raise ValueError('Hosted response limit reached')
                    messages.append(message)
                await create_app(root)(internal,receive,capture)
                if mutate:
                    status=messages[0]['status'];value=json.loads(b''.join(m.get('body',b'') for m in messages))
                    result_id=value.get('experiment_id') or value.get('challenge_id') or ''
                    operation={**operation,'state':'COMPLETED' if status<400 else 'FAILED','status_code':status,
                               'result_id':result_id,'result_path':('/api/experiments/' if result_id.startswith('experiment_') else '/api/challenges/')+result_id if result_id else None,'lease_until':0}
                    if not result_id.startswith('experiment_'):operation['response']=value
                    if status>=400:operation['detail']='The server returned a known failure; no successful result is claimed.'
                    state={**state,'files':snapshot(root),'lease_until':0,'requests':{**state['requests'],oid:operation}}
                    await asyncio.to_thread(self.storage.write,sid,state,lease_etag)
                    lease_etag=None
                if path=='/api/health':
                    health=json.loads(b''.join(m.get('body',b'') for m in messages))
                    health['hosting']={'persistence':'private Vercel Blob','session_scope':'signed browser cookie; export before clearing cookies','operation_limit':64}
                    payload=canonical(health);messages=[messages[0],{'type':'http.response.body','body':payload}]
                    messages[0]['headers']=[(k,v) for k,v in messages[0]['headers'] if k.lower()!=b'content-length']+[(b'content-length',str(len(payload)).encode())]
                for message in messages:
                    if message['type']=='http.response.start':
                        message['headers']=[(k,v) for k,v in message.get('headers',[]) if k.lower() not in (b'cache-control',b'vary')]
                        message['headers'] += [(b'cache-control',b'private, no-store'),(b'vary',b'Cookie')]
                        if mutate:message['headers'].append((b'x-qfault-operation',oid.encode()))
                        if mutate and f'{COOKIE}={cookie}' not in headers.get('cookie',''):
                            message['headers'].append((b'set-cookie',cookie_header.encode()))
                    await send(message)
        except Conflict:return await error(409,'Session changed in another request. Inspect history before retrying.')
        except ValueError:return await error(507,'Hosted storage or response limit reached. No successful saved result is claimed.')
        except (OSError,KeyError,TypeError):return await error(503,'Saved-report storage is unavailable. No successful saved result is claimed; retry after checking history.')
        finally:
            if lease_etag is not None:
                try:
                    unknown={**state,'files':previous['files'],'lease_until':0,'requests':{**state.get('requests',{}),oid:{**operation,'state':'UNKNOWN','lease_until':0,'detail':'Execution or durable save was interrupted. Never automatically resubmit this identity.'}}}
                    await asyncio.to_thread(self.storage.write,sid,unknown,lease_etag)
                except (Conflict,OSError,ValueError):pass  # Expiring lease, never overwrite a newer owner.
