"""Package the committed source, referenced measured evidence and optional real demo media."""
import argparse,hashlib,json,subprocess,zipfile
import os
import shutil
import tempfile
import zlib
from pathlib import Path, PurePosixPath
from qfault.storage import ArtifactStore

SOURCES=['results.json','diagnostic-final.json','diagnostic-development.json','diagnostic-low-shot.json','recovery-stabilization.json','backend-conformance.json','submission-demo.json','measurement-boundary-holdout-20261013.json']

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
                if isinstance(value.get(key),str):add(value[key],value.get('manifest_digest') or value.get('manifest_sha256') or value.get('artifact_digest') or value.get('export_sha256') or value.get('sha256'))
            for child in value.values():visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    for source in summaries:
        data=json.loads(source.read_bytes());visit(data)  # Summaries belong to the source bundle, not the evidence ZIP.
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

def legacy_main():
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

def _git(repo, *args):
    return subprocess.check_output(['git', '-c', f'safe.directory={repo.as_posix()}',
                                    '-C', str(repo), *args])


def _safe_member(name):
    path = PurePosixPath(name)
    return bool(name and not path.is_absolute() and '\\' not in name and ':' not in name
                and all(p not in ('', '.', '..') for p in name.split('/')))


def verify_package(folder):
    """Verify bounded ZIP contents without extracting or trusting a stored flag."""
    folder = Path(folder)
    errors = []
    try:
        manifest_path = folder / 'manifest.json'
        if manifest_path.stat().st_size > 1024 * 1024:
            raise ValueError('manifest exceeds 1 MiB')
        data = json.loads(manifest_path.read_bytes())
        if data.get('schema_version') != 1 or data.get('mode') not in ('source-only', 'evidence-inclusive'):
            raise ValueError('unsupported package schema or mode')
        packages = data['packages']
        if not isinstance(packages, list) or not 1 <= len(packages) <= 2:
            raise ValueError('invalid package membership')
        expected = {'qfault-source.zip'}
        if {item['file'] for item in packages} != expected:
            raise ValueError('invalid package membership')
        for item in packages:
            target = folder / item['file']
            if target.is_symlink() or target.stat().st_size > 128 * 1024 * 1024:
                raise ValueError('unsafe package file')
            if target.stat().st_size != item['bytes'] or sha(target) != item['sha256']:
                raise ValueError('package size/digest mismatch')
            with zipfile.ZipFile(target) as archive_file:
                entries = archive_file.infolist()
                names = [e.filename for e in entries]
                if len(names) != len(set(names)) or len(names) > 10000:
                    raise ValueError('duplicate or excessive archive membership')
                if sum(e.file_size for e in entries) > 256 * 1024 * 1024:
                    raise ValueError('archive expansion exceeds 256 MiB')
                for entry in entries:
                    if not _safe_member(entry.filename) or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ValueError('unsafe archive member')
                if archive_file.testzip():
                    raise ValueError('archive CRC failure')
                actual = {e.filename: hashlib.sha256(archive_file.read(e)).hexdigest() for e in entries}
                if actual != data['source_members_sha256']:
                    raise ValueError('source member digest mismatch')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, zipfile.BadZipFile, zlib.error) as exc:
        errors.append(f'{type(exc).__name__}: {exc}')
    return {'valid': not errors, 'errors': errors,
            'assurance': 'Unsigned byte consistency only; not authenticity or scientific correctness'}


def build_package(repo, output, mode='source-only'):
    """Snapshot reviewed committed source, never reachable Git history/runtime data.

    Evidence-inclusive means complete current external study. Historical summary
    availability is separately described in docs/evidence-availability.md.
    """
    repo, output = Path(repo).resolve(), Path(output).resolve()
    if mode not in ('source-only', 'evidence-inclusive'):
        raise ValueError('unsupported package mode')
    if not output.is_relative_to((repo / 'artifacts').resolve()) or output.exists():
        raise ValueError('choose a new output directory inside artifacts')
    if _git(repo, 'status', '--porcelain').strip():
        raise ValueError('Commit reviewed changes before packaging')
    revision = _git(repo, 'rev-parse', 'HEAD').decode().strip()
    branch = _git(repo, 'branch', '--show-current').decode().strip()
    if not branch:
        raise ValueError('Package a named branch')
    evidence = {'current_external': 'UNAVAILABLE', 'historical': 'See docs/evidence-availability.md'}
    if mode == 'evidence-inclusive':
        from scripts.verify_external_results import verify_results
        from scripts.reconcile_external_evidence import reconcile_rows, frozen_case_grid
        import gzip
        summary_path = repo / 'benchmarks/external-holdout-v1/summary.json'
        reports_path = repo / 'benchmarks/external-holdout-v1/reports.jsonl.gz'
        if not summary_path.is_file() or not reports_path.is_file():
            raise FileNotFoundError('Current evidence missing: benchmarks/external-holdout-v1/{summary.json,reports.jsonl.gz}')
        audit = verify_results(summary_path, reports_path)
        if not audit['valid']:
            raise ValueError('Current evidence failed verification: ' + '; '.join(audit['errors'][:3]))
        summary = json.loads(summary_path.read_bytes())
        corpus = json.loads((repo / 'configs/external-corpus.json').read_bytes())
        with gzip.open(reports_path, 'rb') as stream:
            recount = reconcile_rows(summary['rows'], summary['recovery_rows'],
                (json.loads(line) for line in stream), expected_cases=frozen_case_grid(summary, corpus))
        if not recount['valid']:
            raise ValueError('Current evidence membership failed verification')
        evidence.update(current_external='VERIFIED', counts=recount['counts'])
        historical=repo/'benchmarks/historical-recovery-v1'
        if (repo/'benchmarks/counterfactual-recovery-holdout.json').is_file():
            from scripts.verify_recovery_archive import verify
            checked=verify(historical)
            if not checked['valid']: raise ValueError('Historical recovery evidence missing/corrupt: '+str(checked['errors'][:3]))
            evidence['historical_recovery']={'status':'VERIFIED','reports':checked['reports']}
        replication=repo/'benchmarks/current-release-replication-v4'
        if (replication/'summary.json').is_file():
            from scripts.verify_replication import verify
            checked=verify(replication)
            if not checked['valid']:raise ValueError('Current replication evidence missing/corrupt: '+str(checked['errors'][:3]))
            evidence['current_replication']={'status':'VERIFIED','reports':checked['reports']}
    records = _git(repo, 'ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0')
    members = {}
    for record in records:
        if not record:
            continue
        meta, raw_name = record.split(b'\t', 1)
        name = raw_name.decode('utf-8')
        parts = PurePosixPath(name).parts
        if not _safe_member(name) or meta.startswith(b'120000'):
            raise ValueError('unsafe tracked source member')
        if parts[0] in ('paper', 'research') or name.endswith('.tex'):
            continue
        if parts[0] in ('.git', '.local', 'artifacts', 'node_modules') or any(p in ('node_modules', '__pycache__') for p in parts):
            raise ValueError('private/runtime member tracked; review before packaging')
        if mode == 'source-only' and name.startswith('benchmarks/') and name.endswith('/reports.jsonl.gz'):
            continue
        members[name] = _git(repo, 'show', f'{revision}:{name}')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.package-', dir=output.parent))
    try:
        target = temporary / 'qfault-source.zip'
        with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive_file:
            for name, body in sorted(members.items()):
                archive_file.writestr(name, body)
        manifest = {'schema_version': 1, 'version': 'qfault-release-package-v1',
            'mode': mode, 'source_commit': revision, 'branch': branch, 'dirty_policy': 'clean committed snapshot only',
            'evidence_complete': mode == 'evidence-inclusive', 'evidence_scope': 'available studies explicitly listed in evidence; other historical families excluded',
            'evidence': evidence, 'packages': [{'file': target.name, 'bytes': target.stat().st_size, 'sha256': sha(target)}],
            'source_members_sha256': {name: hashlib.sha256(body).hexdigest() for name, body in members.items()},
            'integrity': 'Unsigned SHA256 and ZIP CRC; not authenticity or scientific truth',
            'setup': 'Extract into a new directory, then follow README.md; no Git history or private runtime data included'}
        (temporary / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
        checked = verify_package(temporary)
        if not checked['valid']:
            raise ValueError('; '.join(checked['errors']))
        os.rename(temporary, output)
        return manifest
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main():
    parser = argparse.ArgumentParser(description='Package a clean source snapshot with explicit evidence availability')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--mode', choices=['source-only', 'evidence-inclusive'], default='source-only')
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            result = verify_package(args.verify)
            print(json.dumps(result, indent=2))
            return 0 if result['valid'] else 1
        if args.out is None:
            parser.error('--out is required unless --verify is supplied')
        result = build_package(Path(__file__).resolve().parents[1], args.out, args.mode)
        print(json.dumps({k:v for k,v in result.items() if k != 'source_members_sha256'}, indent=2))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'status': 'FAILED', 'error': str(exc)}))
        return 1


if __name__=='__main__':raise SystemExit(main())
