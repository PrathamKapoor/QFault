"""Audit existing paired predictions and their hash-bound raw artifacts; never rerun/tune policies."""
import argparse,json,hashlib
from pathlib import Path
from qfault.storage import ArtifactStore

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    output=Path(args.out)
    if output.exists(): raise FileExistsError(output)
    source=Path('benchmarks/diagnostic-final.json')
    data=json.loads(source.read_bytes())
    fixed={r['case_id']:r for r in data['rows'] if r['policy']=='fixed'}
    phase={r['case_id']:r for r in data['rows'] if r['policy']=='phase'}
    if fixed.keys()!=phase.keys(): raise ValueError('unmatched paired cases')
    paired={k:[] for k in ['both_correct','fixed_only_correct','phase_only_correct','neither_correct']}
    for case,f in fixed.items():
        p=phase[case]
        if f['truth']!=p['truth']: raise ValueError('inconsistent evaluator truth')
        fc=f['prediction']==f['truth'];pc=p['prediction']==p['truth']
        group='both_correct' if fc and pc else 'fixed_only_correct' if fc else 'phase_only_correct' if pc else 'neither_correct'
        paired[group].append({'case_id':case,'truth':f['truth'],'fixed':f['prediction'],'phase':p['prediction']})
    verified=[]
    for row in data['rows']:
        folder=Path(row['artifact_path'].replace('\\','/'))
        actual=hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()
        if actual!=row['manifest_digest']: raise ValueError('manifest digest mismatch: '+row['case_id'])
        check=ArtifactStore(folder.parent).verify(row['experiment_id'])
        if not check['valid']: raise ValueError('invalid stored evidence: '+row['case_id'])
        verified.append(row['experiment_id'])
    summary={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'matched_cases':len(fixed),'paired_counts':{k:len(v) for k,v in paired.items()},'paired_rows':paired,'verified_raw_artifacts':len(verified),'interpretation':'Descriptive paired outcomes, not a significance or generalization claim; no scientific threshold or policy change.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf8') as stream:json.dump(summary,stream,indent=2)
    print(json.dumps({k:v for k,v in summary.items() if k!='paired_rows'},indent=2))
if __name__=='__main__':main()
