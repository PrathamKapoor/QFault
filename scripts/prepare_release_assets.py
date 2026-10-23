"""Deliberately select reviewed source, research evidence and controlled demonstration assets."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

from qfault.evidence import canonical
from qfault.storage import verify_export
from scripts.audit_counterfactual import audit_record
from scripts.package_submission import build_package,verify_package
from scripts.release_delivery import bundle_package,sha256
from scripts.public_release import required_assets,validate_assets

ROOT=Path(__file__).resolve().parents[1]
STAGES=('z','phase','recovery','noise','budget')


def make_demo_archive(folder,out,source_commit):
    folder=Path(folder);metadata=json.loads((folder/'recording.json').read_bytes())
    if metadata['source_commit']!=source_commit:raise ValueError('Recording source differs from package source')
    playback=json.loads((folder/'playback-verification.json').read_bytes())
    if metadata['media']!='guided-demo-silent.webm':raise ValueError('Unexpected media member')
    media=folder/'guided-demo-silent.webm'
    if media.is_symlink() or sha256(media)!=metadata['sha256'] or playback['sha256']!=metadata['sha256']:
        raise ValueError('Recording digest differs from verified playback bytes')
    quality=playback['quality']
    if playback['source_commit']!=source_commit or playback['valid'] is not True or playback['playback_speed']!=1 or not quality['ended'] or quality['error'] is not None or quality['corrupted_frames']!=0 or quality['audio_tracks']!=0 or quality['total_frames']<=0:
        raise ValueError('Silent normal-speed playback is not verified')
    if metadata['input_sha256']!=sha256(ROOT/'examples/qrng-phase-demo.json'):
        raise ValueError('Demonstration input identity differs')
    rows=metadata['rows'];by_stage={r['stage']:r for r in rows}
    if len(rows)!=5 or set(by_stage)!=set(STAGES):raise ValueError('Missing/duplicate demonstration case')
    fixture=json.loads((ROOT/'examples/qrng-phase-demo.json').read_bytes());ids=set();members={}
    for key in STAGES:
        path=folder/(key+'-report.json')
        if path.is_symlink() or path.stat().st_size>16*1024*1024:raise ValueError('Unsafe demonstration report')
        raw=path.read_bytes();report=json.loads(raw);record=report['investigation'];row=by_stage[key]
        if not verify_export(report)['valid'] or record['experiment_id']!=row['experiment_id'] or row['report_sha256']!=hashlib.sha256(raw).hexdigest():
            raise ValueError('Demonstration export identity/digest mismatch')
        if record['experiment_id'] in ids or record['configuration']!=fixture['requests'][key]['body']:
            raise ValueError('Demonstration request membership mismatch')
        if record['human_decisions']:raise ValueError('Human reviews are not selected for public demonstration evidence')
        ids.add(record['experiment_id'])
        if key in ('recovery','noise','budget'):audit_record(record)
        members[path.name]=raw
    public={'schema_version':1,'source_commit':source_commit,'fixture_id':fixture['id'],'source':fixture['source'],
        'input_sha256':metadata['input_sha256'],'rows':rows,'media_sha256':metadata['sha256'],
        'scope':'Controlled current demonstration exports, not personal runtime investigations or a frozen performance evaluation'}
    members['demonstration.json']=canonical(public)
    members['QASMBench-LICENSE.txt']=(ROOT/'benchmarks/external/qasmbench/LICENSE').read_bytes()
    members['QASMBench-NOTICE.txt']=(ROOT/'benchmarks/external/qasmbench/NOTICE').read_bytes()
    members['LICENSE.txt']=(ROOT/'LICENSE').read_bytes()
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,body in members.items():archive.writestr(name,body)
    return public,quality


def prepare(tag,recording,verification,out,packages_root=None):
    command=['git','-c','safe.directory='+ROOT.as_posix()]
    def git(*args):return subprocess.check_output(command+list(args),cwd=ROOT,text=True).strip()
    if git('status','--porcelain'):raise ValueError('Commit reviewed source before packaging')
    revision=git('rev-parse','HEAD');required_assets(tag)
    checked=json.loads(Path(verification).read_bytes())
    if checked['source_commit']!=revision or not checked['checks'] or any(c['status']!='PASS' for c in checked['checks']):
        raise ValueError('Verification record differs from clean source or has incomplete checks')
    out=Path(out).resolve()
    if not out.is_relative_to((ROOT/'artifacts').resolve()):raise ValueError('Release outputs must be in a new artifacts directory')
    out.mkdir(parents=True,exist_ok=False);assets=out/'assets';assets.mkdir();packages=[]
    demo,quality=make_demo_archive(recording,assets/f'qfault-{tag}-demo-evidence.zip',revision)
    for label,mode in [('source','source-only'),('evidence','evidence-inclusive')]:
        if packages_root is None:
            package=out/'packages'/mode;package_manifest=build_package(ROOT,package,mode)
        else:
            package=Path(packages_root)/mode
            if not verify_package(package)['valid']:raise ValueError('Previously tested package is inconsistent')
            package_manifest=json.loads((package/'manifest.json').read_bytes())
            if package_manifest['source_commit']!=revision or package_manifest['mode']!=mode:
                raise ValueError('Previously tested package source/mode differs')
        packages.append(bundle_package(package,assets/f'qfault-{tag}-{label}.zip'))
    for source,name in [('docs/judging-guide.md','judging-guide.md'),('docs/three-minute-demo.md','three-minute-demo.md')]:
        shutil.copyfile(ROOT/source,assets/name)
    for source,name in [('guided-demo-silent.webm',f'qfault-{tag}-guided-demo-silent.webm'),
                        ('guided-demo-captions.vtt',f'qfault-{tag}-guided-demo-captions.vtt')]:
        path=Path(recording)/source
        if path.is_symlink():raise ValueError('Do not select linked media')
        shutil.copyfile(path,assets/name)
    external=json.loads((ROOT/'benchmarks/external-holdout-v1/summary.json').read_bytes())
    conservative=external['recovery_summaries']['conservative'];point=external['recovery_summaries']['point_discrepancy']
    replication=json.loads((ROOT/'benchmarks/current-release-replication-v4/summary.json').read_bytes())
    summary={'schema_version':1,'tag':tag,'source_commit':revision,'checks':checked['checks'],'packages':packages,
        'media':{'file':f'qfault-{tag}-guided-demo-silent.webm','sha256':sha256(assets/f'qfault-{tag}-guided-demo-silent.webm'),
            'narration':'Silent recording; complete text narration and actual-time captions supplied','playback':quality},
        'demonstration':demo,'scientific_evidence':{
            'external':{'protocol':external['protocol']['name'],'execution_revision':external['execution_revision'],
                'membership':package_manifest['evidence']['counts'],'holdout_programs':external['architecture_count'],
                'recovery':{name:{'runs':row['runs'],'eligible':row['eligible'],
                    'verified':row['outcomes'].get('VERIFIED_UNDER_DECLARED_CONTRACT',0),
                    'rejected':row['outcomes'].get('REJECTED',0),'shots':row['shots']}
                    for name,row in [('conservative',conservative),('point_discrepancy',point)]},
                'relative_shot_reduction':(point['shots']-conservative['shots'])/point['shots']},
            'historical_recovery':{**package_manifest['evidence']['historical_recovery'],
                'other_historical_families':'Unavailable/unknown as availability ledger states'},
            'replication':{'source_commit':replication['source_commit'],'protocol':replication['protocol'],
                'matched':replication['matched'],'runs':replication['runs'],'errors':replication['errors'],
                'scope':'Observed-design scientific replication, not repair accuracy or new untouched holdout'}},
        'limitations':['Local simulator, one declared input/contract, bounded edits; no universal equivalence/hardware/unique-cause claim',
            'Small correlated simulation cases; no population superiority',
            'Uncalibrated noise and dense/inadequate-budget cases can abstain; time guards cooperative',
            'Unsigned hashes are consistency checks, not authenticity or scientific correctness; preserve third-party licenses',
            'No narrated voiceover, competition submission or macOS/ARM claim'],
        'documentation_boundary':'Packages contain this exact source snapshot; later main documentation does not move the release tag or change these bytes'}
    (assets/'release-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    names=required_assets(tag)
    with (assets/'SHA256SUMS').open('x',encoding='utf8',newline='\n') as stream:
        for name in sorted(names):stream.write(sha256(assets/name)+'  '+name+'\n')
    validate_assets(assets,tag,revision)
    print(json.dumps({'source_commit':revision,'assets':str(assets),'names':sorted(names|{'SHA256SUMS'})},indent=2))
    return assets


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tag',required=True)
    parser.add_argument('--recording',type=Path,required=True);parser.add_argument('--verification',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--packages-root',type=Path,help='Reuse independently installed/verified package bytes from this exact commit')
    args=parser.parse_args();prepare(args.tag,args.recording,args.verification,args.out,args.packages_root)


if __name__=='__main__':main()
