"""Package the committed source, referenced measured evidence and optional real demo media."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
from qfault.storage import ArtifactStore

SOURCES=['results.json','diagnostic-final.json','diagnostic-development.json','diagnostic-low-shot.json','recovery-stabilization.json','backend-conformance.json','submission-demo.json']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def collect_evidence(repo,summaries):
    repo=repo.resolve();allowed=(repo/'artifacts').resolve();files=set()
    def add(value,expected=None):
        path=(repo/str(value).replace('\\','/')).resolve()
        if not path.is_relative_to(allowed):raise ValueError('evidence outside artifacts')
        if path.is_dir():
            if expected and sha(path/'manifest.json')!=expected:raise ValueError('manifest digest mismatch')
            if not ArtifactStore(path.parent).verify(path.name)['valid']:raise ValueError('invalid evidence manifest')
            for item in path.rglob('*'):
                if item.is_file():
                    if item.is_symlink() or item.suffix!='.json':raise ValueError('unexpected evidence file')
                    files.add(item)
        elif path.is_file():
            if path.suffix!='.json' or path.is_symlink():raise ValueError('unexpected evidence file')
            if expected and sha(path)!=expected:raise ValueError('artifact digest mismatch')
            files.add(path)
        else:raise FileNotFoundError(path)
    def visit(value):
        if isinstance(value,dict):
            for key in ['artifact_path','artifact','export']:
                if isinstance(value.get(key),str):add(value[key],value.get('manifest_digest') or value.get('artifact_digest') or value.get('export_sha256') or value.get('sha256'))
            for child in value.values():visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    for source in summaries:
        data=json.loads(source.read_bytes());visit(data);files.add(source.resolve())
        # Original benchmark recovery rows omit a path but use the same stored investigation root.
        if isinstance(data.get('recovery'),dict) and data.get('rows'):
            parent=Path(data['rows'][0]['artifact_path'].replace('\\','/')).parent
            for row in data['recovery'].get('rows',[]):add(parent/row['experiment_id'])
    return sorted(files)

def archive(target,repo,files):
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:z.write(path,path.relative_to(repo).as_posix())
    with zipfile.ZipFile(target) as z:
        if z.testzip():raise ValueError('archive CRC failure')

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--demo',action='append');a=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    def git(*args):return subprocess.run(['git','-c',f'safe.directory={repo}','-C',str(repo),*args],check=True,capture_output=True,text=True).stdout.strip()
    if git('status','--porcelain'):raise ValueError('Commit reviewed changes before packaging')
    revision=git('rev-parse','HEAD');branch=git('branch','--show-current')
    if not branch:raise ValueError('Package a named branch')
    files=collect_evidence(repo,[repo/'benchmarks'/name for name in SOURCES])
    output=Path(a.out).resolve()
    if not output.is_relative_to((repo/'artifacts').resolve()):raise ValueError('output must be inside artifacts')
    output.mkdir(parents=True,exist_ok=False)
    bundle=output/'qfault-source.bundle';git('bundle','create',str(bundle),branch);git('bundle','verify',str(bundle))
    evidence=output/'qfault-evidence.zip';archive(evidence,repo,files)
    packages=[bundle,evidence]
    if a.demo:
        media=[]
        for item in a.demo:
            demo=Path(item).resolve()
            if not demo.is_relative_to((repo/'artifacts').resolve()):raise ValueError('demo outside artifacts')
            media.extend(path for path in demo.rglob('*') if path.is_file())
        if not media or any(path.is_symlink() or path.suffix not in {'.json','.png','.webm'} for path in media):raise ValueError('unexpected demo contents')
        target=output/'qfault-demo-material.zip';archive(target,repo,sorted(set(media)));packages.append(target)
    manifest={'source_commit':revision,'branch':branch,'evidence_files':len(files),'packages':[{'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path)} for path in packages],
        'fresh_install':'NOT VERIFIED; package sources remain environment-blocked','recording':'Any supplied WebM is genuine silent raw browser footage, not a narrated final video','integrity':'Unsigned SHA256 and ZIP CRC; not authenticity or scientific truth'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
