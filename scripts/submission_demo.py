"""Offline judging rehearsal; real executions, exports and reversible tamper control."""
import argparse,json
from pathlib import Path
from qfault.workflow import RunRequest,investigate
from qfault.storage import ArtifactStore,verify_export
from qfault.evidence import canonical,digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--backend',choices=['aer','reference'],default='aer');a=p.parse_args()
    root=Path(a.out);root.mkdir(parents=True,exist_ok=False);store=ArtifactStore(root/'investigations');rows=[]
    for label,settings in [('healthy',{}),('hidden_logical_failure',{'scenario':'remove'}),('noise_control',{'scenario':'readout'}),('relative_phase',{'scenario':'phase'}),('insufficient_evidence',{'scenario':'remove','max_shots':4096,'max_evaluations':2})]:
        r=investigate(RunRequest(policy='phase',backend=a.backend,seed=42,**settings));eid=store.save(r)
        report=store.export(eid);valid=verify_export(report);assert valid['valid']
        export=root/(label+'.json');export.write_bytes(canonical(report))
        rows.append({'label':label,'experiment_id':eid,'diagnosis':r['diagnosis']['category'],'recovery':r['recovery']['status'] if r['recovery'] else None,'shots':r['cost']['shots'],'evaluations':r['cost']['evaluations'],'export':str(export),'export_sha256':digest(report),'verified':valid['valid'],'backends':sorted({e['backend_name'] for e in r['executions']})})
    # Only a dedicated throwaway investigation is altered, and original bytes restored.
    scratch=investigate(RunRequest(backend=a.backend,recover=False,seed=99));eid=store.save(scratch);path=store.folder(eid)/'investigation.json';before=path.read_bytes()
    initial=store.verify(eid)['valid']
    try:
        changed=json.loads(before);counts=changed['executions'][0]['output_counts'];counts[next(iter(counts))]+=1;path.write_bytes(canonical(changed));tampered=store.verify(eid)['valid']
    finally: path.write_bytes(before)
    restored=store.verify(eid)['valid'];assert initial and not tampered and restored
    summary={'backend':a.backend,'rows':rows,'integrity_control':{'original':initial,'tampered':tampered,'restored':restored,'experiment_id':eid},'limitations':['Local simulation only','Ideal attribution uses privileged exact state calculation','Unsigned hashes do not authenticate truth or author','Human review remains pending; no circuit is automatically applied']}
    (root/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
