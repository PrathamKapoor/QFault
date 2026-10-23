"""Publish reviewed QFault assets or independently verify their public downloads."""
import argparse
import json
import mimetypes
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError
from urllib.parse import quote,urlsplit
from urllib.request import HTTPRedirectHandler,Request,build_opener,urlopen

from scripts.release_delivery import sha256,verify_release_archive

ROOT=Path(__file__).resolve().parents[1]
REPO='PrathamKapoor/QFault'


def read_checksums(folder):
    folder=Path(folder);path=folder/'SHA256SUMS'
    if path.is_symlink() or path.stat().st_size>65536:raise ValueError('Unsafe checksum file')
    values={}
    for line in path.read_text(encoding='utf8').splitlines():
        match=re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._-]{0,120})',line)
        if not match:raise ValueError('Unsafe or malformed checksum member')
        checksum,name=match.groups()
        if name in values or name=='SHA256SUMS':raise ValueError('Duplicate/self-referential checksum member')
        item=folder/name
        if item.is_symlink() or not item.is_file() or item.stat().st_size>130*1024*1024:
            raise ValueError('Missing/unsafe/oversized checksum member')
        if sha256(item)!=checksum:raise ValueError('Checksum mismatch for '+name)
        values[name]=checksum
    if not values:raise ValueError('No release assets listed')
    return values


def required_assets(tag):
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?',tag):raise ValueError('Invalid version tag')
    prefix='qfault-'+tag
    return {prefix+'-source.zip',prefix+'-evidence.zip',prefix+'-demo-evidence.zip',
        prefix+'-guided-demo-silent.webm',prefix+'-guided-demo-captions.vtt',
        'judging-guide.md','three-minute-demo.md','release-verification.json'}


def validate_assets(folder,tag,source_commit):
    folder=Path(folder);checks=read_checksums(folder)
    if set(checks)!=required_assets(tag):raise ValueError('Required reviewed release assets differ')
    if {p.name for p in folder.iterdir()}!=set(checks)|{'SHA256SUMS'}:
        raise ValueError('Unlisted files/directories found; do not sweep runtime data into a release')
    for suffix,mode in [('source','source-only'),('evidence','evidence-inclusive')]:
        result=verify_release_archive(folder/f'qfault-{tag}-{suffix}.zip')
        if not result['valid'] or result['source_commit']!=source_commit or result['mode']!=mode:
            raise ValueError('Release package invalid or bound to another source')
    verification=json.loads((folder/'release-verification.json').read_bytes())
    if type(verification.get('schema_version')) is not int or verification['schema_version']!=1 or verification['source_commit']!=source_commit:
        raise ValueError('Public verification summary source/version mismatch')
    if not verification['checks'] or any(c['status']!='PASS' for c in verification['checks']):
        raise ValueError('Release checks are incomplete')
    media=verification['media']
    if media['sha256']!=checks[f'qfault-{tag}-guided-demo-silent.webm'] or media['playback']['ended'] is not True or media['playback']['corrupted_frames']!=0 or media['playback']['audio_tracks']!=0:
        raise ValueError('Silent recording verification differs from reviewed bytes')
    return checks,verification


def credential():
    env=os.environ.copy();env.update(GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never')
    result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',
        capture_output=True,text=True,env=env,timeout=30)
    fields=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    if result.returncode or not fields.get('password'):raise RuntimeError('Configured GitHub authentication is unavailable; no credential values printed')
    return fields['password']


class GitHub:
    def __init__(self,token=None):self.token=token

    def request(self,method,path,body=None,content_type=None):
        url=path if path.startswith('https://') else 'https://api.github.com/repos/'+REPO+'/'+path
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.hostname not in ('api.github.com','uploads.github.com') or parsed.username:
            raise ValueError('Unexpected GitHub API host')
        if method=='GET':url+=('&' if '?' in url else '?')+'verification='+str(time.time_ns())
        headers={'User-Agent':'QFault-release-verification','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
        if self.token:headers['Authorization']='Bearer '+self.token
        if body is not None:
            if not isinstance(body,bytes):body=json.dumps(body).encode('utf8')
            headers['Content-Type']=content_type or 'application/json'
        request=Request(url,data=body,headers=headers,method=method)
        with urlopen(request,timeout=90 if method=='POST' else 30) as response:
            raw=response.read(8*1024*1024+1)
        if len(raw)>8*1024*1024:raise ValueError('GitHub metadata response too large')
        return json.loads(raw)


def resolve_tag(client,tag):
    value=client.request('GET','git/ref/tags/'+quote(tag,safe=''))['object']
    for _ in range(3):
        if value['type']=='commit':return value['sha']
        if value['type']!='tag':break
        value=client.request('GET','git/tags/'+value['sha'])['object']
    raise ValueError('Release tag does not resolve to a bounded commit identity')


class PublicRedirect(HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        parsed=urlsplit(newurl)
        if parsed.scheme!='https' or not (parsed.hostname=='github.com' or (parsed.hostname or '').endswith('.githubusercontent.com')):
            raise ValueError('Unexpected public asset redirect')
        return super().redirect_request(request,fp,code,msg,headers,newurl)


def download(url,path,limit):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname!='github.com' or not parsed.path.startswith('/'+REPO+'/releases/download/'):
        raise ValueError('Unexpected release asset URL')
    request=Request(url,headers={'User-Agent':'QFault-release-verification'})
    temporary=path.with_name(path.name+'.part');start=time.monotonic();size=0
    with build_opener(PublicRedirect()).open(request,timeout=30) as response,temporary.open('xb') as stream:
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>limit or time.monotonic()-start>180:raise ValueError('Download size/time guard exceeded')
            stream.write(chunk)
    if path.exists():raise FileExistsError('Download destination already exists')
    temporary.rename(path)


def verify_public(tag,out,source_commit=None):
    required=required_assets(tag);client=GitHub();release=client.request('GET','releases/tags/'+quote(tag,safe=''))
    if release['draft'] or release['tag_name']!=tag:raise ValueError('Release is not public at the requested tag')
    assets=release['assets'];by_name={a['name']:a for a in assets}
    if len(by_name)!=len(assets) or set(by_name)!=required|{'SHA256SUMS'} or any(a['state']!='uploaded' for a in assets):
        raise ValueError('Remote asset membership/state differs')
    if sum(a['size'] for a in assets)>512*1024*1024:raise ValueError('Public asset total exceeds limit')
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    for name in ['SHA256SUMS',*sorted(required)]:
        asset=by_name[name];limit=65536 if name=='SHA256SUMS' else 130*1024*1024
        if asset['size']>limit:raise ValueError('Remote asset exceeds bound')
        download(asset['browser_download_url'],out/name,limit)
        if (out/name).stat().st_size!=asset['size']:raise ValueError('Remote/download size mismatch')
        if asset.get('digest') and asset['digest']!='sha256:'+sha256(out/name):raise ValueError('Remote/download digest mismatch')
    summary=json.loads((out/'release-verification.json').read_bytes());source=summary['source_commit']
    if source_commit is not None and source!=source_commit:raise ValueError('Public source differs from expected commit')
    checks,_=validate_assets(out,tag,source)
    if resolve_tag(client,tag)!=source:raise ValueError('Remote tag differs from package source')
    return {'valid':True,'tag':tag,'source_commit':source,'release_url':release['html_url'],
        'assets':[{'name':name,'url':by_name[name]['browser_download_url'],'bytes':by_name[name]['size'],
                   'sha256':sha256(out/name)} for name in sorted(by_name)],
        'assurance':'Downloaded bytes and tag/package bindings verified; unsigned hashes are not authenticity guarantees'}


def publish(tag,folder,source_commit,download_out):
    if not re.fullmatch('[0-9a-f]{40}',source_commit):raise ValueError('Expected a full source commit')
    checks,_=validate_assets(folder,tag,source_commit);folder=Path(folder)
    command=['git','-c','safe.directory='+ROOT.as_posix()]
    def git(*args):return subprocess.check_output(command+list(args),cwd=ROOT,text=True).strip()
    if git('status','--porcelain') or git('rev-parse','HEAD')!=source_commit:raise ValueError('Publish from the exact clean package source')
    if git('remote','get-url','origin') not in ('https://github.com/'+REPO+'.git','https://github.com/'+REPO):
        raise ValueError('Unexpected publication origin')
    client=GitHub(credential())
    user=client.request('GET','https://api.github.com/user')
    if user.get('login')!='PrathamKapoor':raise ValueError('Configured GitHub account differs from owner')
    if client.request('GET','git/ref/heads/main')['object']['sha']!=source_commit:raise ValueError('Remote main differs from reviewed source')
    runs=client.request('GET','actions/runs?per_page=50')['workflow_runs']
    matches=[client.request('GET','actions/runs/'+str(r['id'])) for r in runs if r['head_sha']==source_commit]
    if not any(r['status']=='completed' and r['conclusion']=='success' for r in matches):
        raise ValueError('Exact-source hosted CI has not succeeded')
    if any(r['tag_name']==tag for r in client.request('GET','releases?per_page=100')):
        raise ValueError('Existing release preserved; use verify-only or a new tag')
    try:client.request('GET','git/ref/tags/'+quote(tag,safe=''))
    except HTTPError as exc:
        if exc.code!=404:raise
    else:raise ValueError('Existing tag preserved; choose a new version')
    base='https://github.com/'+REPO+'/releases/download/'+tag+'/'
    links='\n'.join('- ['+name+']('+base+quote(name)+')' for name in sorted(required_assets(tag)|{'SHA256SUMS'}))
    body=f'''QFault connects declared contracts, measured discrepancies, bounded interventions and fresh verification in one local workbench.

Open Guided demo for the source-qualified QASMBench QRNG phase example and real noise/budget abstentions. The recording is silent; the full narration and captions are supplied separately.

Package source commit: `{source_commit}`. Source-only intentionally omits raw evidence; evidence-inclusive includes the three explicitly available archives. Other historical evidence remains unavailable as documented. Checksums provide unsigned consistency, not authenticity.

{links}

See the judging guide for locked setup, the real-engine text fallback, independent verification and the three-minute presentation. No hardware validation, universal equivalence, unique fault cause or population superiority is claimed.'''
    release=client.request('POST','releases',{'tag_name':tag,'target_commitish':source_commit,
        'name':'QFault '+tag+' — guided investigations and inspectable evidence','body':body,'draft':True,'prerelease':False})
    upload=release['upload_url'].split('{',1)[0]
    expected_path='/repos/'+REPO+'/releases/'+str(release['id'])+'/assets'
    if urlsplit(upload).hostname!='uploads.github.com' or urlsplit(upload).path!=expected_path:raise ValueError('Unexpected upload endpoint')
    all_checks={**checks,'SHA256SUMS':sha256(folder/'SHA256SUMS')}
    for name,checksum in sorted(all_checks.items()):
        path=folder/name
        asset=client.request('POST',upload+'?name='+quote(name),path.read_bytes(),mimetypes.guess_type(name)[0] or 'application/octet-stream')
        if asset['name']!=name or asset['state']!='uploaded' or asset['size']!=path.stat().st_size or (asset.get('digest') and asset['digest']!='sha256:'+checksum):
            raise ValueError('Upload metadata mismatch; draft retained for inspection')
    remote=client.request('GET','releases/'+str(release['id'])+'/assets?per_page=100')
    if {a['name'] for a in remote}!=set(all_checks):raise ValueError('Draft asset membership mismatch; not published')
    client.request('PATCH','releases/'+str(release['id']),{'draft':False})
    return verify_public(tag,download_out,source_commit)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tag',required=True)
    parser.add_argument('--assets',type=Path);parser.add_argument('--source-commit');parser.add_argument('--download-out',type=Path,required=True)
    parser.add_argument('--publish',action='store_true',help='Explicitly publish reviewed owner-authorized assets; otherwise public verification only')
    args=parser.parse_args()
    try:
        if args.publish:
            if not args.assets or not args.source_commit:parser.error('--publish requires --assets and --source-commit')
            result=publish(args.tag,args.assets,args.source_commit,args.download_out)
        else:result=verify_public(args.tag,args.download_out,args.source_commit)
        print(json.dumps(result,indent=2))
        (args.download_out.parent/(args.download_out.name+'-verification.json')).write_text(json.dumps(result,indent=2))
        return 0
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print(json.dumps({'valid':False,'error':type(exc).__name__+': '+str(exc),'credential_values':'never printed'}));return 1


if __name__=='__main__':raise SystemExit(main())
