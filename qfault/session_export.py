"""Bounded, complete public projections of one browser session's reports."""
import hashlib
import io
import json
import re
import zipfile
import zlib
from .evidence import canonical
from .storage import ArtifactStore,verify_export
from .challenge import BlindChallenges

MAX_ARCHIVE=4*1024*1024
MAX_EXPANDED=32*1024*1024

def build_session_export(root,operations):
    store=ArtifactStore(root);challenges=BlindChallenges(root);members={};ids=[]
    for folder in sorted(root.glob('experiment_*')):
        value=store.export(folder.name)
        if not verify_export(value)['valid']:raise ValueError('A saved report is unavailable or corrupt; complete export refused')
        members['reports/'+folder.name+'.json']=canonical(value);ids.append(folder.name)
    for folder in sorted((root/'challenges').glob('challenge_*')):
        value=challenges.export(folder.name)
        if not verify_export(value)['valid']:raise ValueError('A challenge report is unavailable or corrupt; complete export refused')
        members['reports/'+folder.name+'.json']=canonical(value);ids.append(folder.name)
    members['operations.json']=canonical(operations)
    if sum(map(len,members.values()))>MAX_EXPANDED or len(members)>130:raise ValueError('Session export exceeds bound')
    manifest={'schema_version':1,'kind':'qfault-session-export','complete':True,'report_ids':ids,
              'members':{name:hashlib.sha256(raw).hexdigest() for name,raw in members.items()},
              'scope':'All completed accessible ordinary and public challenge reports in this snapshot. Hidden challenge evaluator files are excluded until reveal. Unsigned consistency, not authenticity.'}
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,raw in {**members,'manifest.json':canonical(manifest)}.items():archive.writestr(name,raw)
    raw=stream.getvalue()
    if len(raw)>MAX_ARCHIVE:raise ValueError('Compressed session export exceeds response bound')
    checked=verify_session_export(raw)
    if not checked['valid']:raise ValueError('Session export verification failed')
    return raw

def verify_session_export(raw):
    try:
        if len(raw)>MAX_ARCHIVE:raise ValueError('Archive too large')
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            rows=archive.infolist();names=[v.filename for v in rows]
            if len(names)!=len(set(names)) or len(rows)>132 or sum(v.file_size for v in rows)>MAX_EXPANDED:raise ValueError('Invalid archive size/membership')
            if any(not (n in ('manifest.json','operations.json') or re.fullmatch(r'reports/(experiment|challenge)_[0-9a-f]{32}\.json',n)) for n in names):raise ValueError('Unsafe archive member')
            manifest=json.loads(archive.read('manifest.json'))
            if type(manifest.get('schema_version')) is not int or manifest['schema_version']!=1 or manifest.get('complete') is not True or manifest.get('kind')!='qfault-session-export':raise ValueError('Unsupported or partial export')
            if set(names)!={'manifest.json',*manifest['members']}:raise ValueError('Export membership mismatch')
            ids=[]
            for name,expected in manifest['members'].items():
                data=archive.read(name)
                if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Export digest mismatch')
                if name.startswith('reports/'):
                    value=json.loads(data)
                    if not verify_export(value)['valid']:raise ValueError('Invalid report')
                    eid=value.get('investigation',{}).get('experiment_id') or value.get('challenge_id')
                    if name!='reports/'+str(eid)+'.json':raise ValueError('Report identity mismatch')
                    ids.append(eid)
            if len(ids)!=len(manifest['report_ids']) or set(ids)!=set(manifest['report_ids']):raise ValueError('Report index mismatch')
        return {'valid':True,'experiment_ids':[v for v in ids if v.startswith('experiment_')],'report_ids':ids,'assurance':'unsigned consistency only'}
    except (ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile,zlib.error,UnicodeError) as exc:
        return {'valid':False,'errors':[str(exc)[:200]]}
