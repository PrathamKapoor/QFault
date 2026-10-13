"""Exclusive-output, source-gated recovery evaluation. Never overwrites frozen results."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from qfault.counterfactual import RecoveryRequest,recover
from qfault.recovery_corpus import cases,POLICIES,SEEDS
from qfault.evidence import canonical,digest
from qfault.storage import ArtifactStore,verify_export

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['qfault/counterfactual.py','qfault/interventions.py','qfault/recovery_observation.py',
         'qfault/recovery_corpus.py','qfault/lab.py','qfault/target.py','qfault/quantum.py',
         'qfault/backends.py','qfault/diagnostics.py','scripts/evaluate_counterfactual.py']


def hashes(): return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}


def protocol():
    return {'name':'counterfactual-recovery-v1','source_sha256':hashes(),'seeds':SEEDS,'policies':POLICIES,
        'cases_sha256':digest(list(cases('holdout'))),'case_count':len(list(cases('holdout'))),
        'backend':'aer','ranking':'Interval dominance / conservative upper loss; resources break operational ties only',
        'verification':'Fresh original and selected candidate: candidate upper loss <=1, original lower loss > candidate upper',
        'error':'alpha .01 divided by (C+3)*M+1; one look per group per subject',
        'budget':'Identical ceilings, candidate sets and single-look samples for all selection baselines; no-repair stops after observation/control',
        'metrics':['detection','eligible','generated/tested','selected','verdicts','plausible locus coverage',
                   'alternative restoring edits','noise-only proposals','shots by phase','evaluations','runtime','resource deltas'],
        'analysis':'Descriptive paired case outcomes, no inferential population claims; repeated designs are not independent architectures',
        'negative_controls':'Clean, readout, gate noise, incomplete Bell distribution, insufficient budget, ambiguous repeated X',
        'exclusions':'None; failed runs retained. No exact-state comparator is claimed information-matched.'}


def run(split,out):
    frozen=json.loads((ROOT/'configs/counterfactual-protocol.json').read_text())
    if split=='holdout':
        if frozen['source_sha256']!=hashes() or frozen['cases_sha256']!=digest(list(cases(split))):
            raise RuntimeError('Frozen recovery sources/cases differ; do not call this the untouched evaluation')
        status=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'status','--porcelain','--',*SOURCES,'configs/counterfactual-protocol.json'],cwd=ROOT,text=True)
        if status.strip(): raise RuntimeError('Commit the protocol and frozen scientific sources before execution')
    out.mkdir(parents=True,exist_ok=False); store=ArtifactStore(out/'investigations');rows=[]
    for case in cases(split):
        for policy in POLICIES:
            row={k:v for k,v in case.items() if k!='request'};row['policy']=policy
            try:
                result=recover(RecoveryRequest.model_validate({**case['request'],'backend':'aer','selection_policy':policy}))
                eid=store.save(result)
                assert verify_export(store.export(eid))['valid']
                selected=result['selected_candidate']; original=result['original_evidence']
                row.update(status=result['status'],experiment_id=eid,manifest_sha256=digest(store.export(eid)['manifest']),
                    discrepancy=bool(original and original['loss_interval'][0]>1),
                    eligible=bool(original and original['loss_interval'][0]>1 and not result['readout_control']['significant']),
                    selected=bool(selected),selected_locus=selected['edit']['index'] if selected else None,
                    plausible_loci=result['localization']['plausible_loci'],causal_origin=result['localization']['causal_origin'],
                    verification=result['verification']['status'],improvement=result['verification'].get('improvement_lower'),
                    cost={k:v for k,v in result['cost'].items() if k!='actions'},
                    resource_delta=selected['resource_delta'] if selected else None)
            except Exception as exc: row.update(status='ERROR',error=repr(exc))
            rows.append(row)
    summaries={}
    for policy in POLICIES:
        rs=[r for r in rows if r['policy']==policy]; noise=[r for r in rs if r['variant'] in ('readout','gate_noise')]
        truth=[r for r in rs if r['truth_locus'] is not None]
        logical=[r for r in rs if r['variant']=='logical']
        variants={v:{'cases':sum(r['variant']==v for r in rs),
                     'statuses':dict(Counter(r['status'] for r in rs if r['variant']==v)),
                     'proposals':sum(r.get('selected',False) for r in rs if r['variant']==v),
                     'verified':sum(r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT' for r in rs if r['variant']==v)}
                  for v in sorted({r['variant'] for r in rs})}
        confusion={expected:{observed:sum(r['variant']==expected and r['status']==observed for r in rs)
                              for observed in sorted({r['status'] for r in rs})}
                   for expected in sorted({r['variant'] for r in rs})}
        summaries[policy]={'cases':len(rs),'outcomes':dict(Counter(r['status'] for r in rs)),
            'detected':sum(r.get('discrepancy',False) for r in rs),'eligible':sum(r.get('eligible',False) for r in rs),
            'proposals':sum(r.get('selected',False) for r in rs),'noise_controls':len(noise),
            'noise_only_proposals':sum(r.get('selected',False) for r in noise),
            'noise_only_verified':sum(r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT' for r in noise),
            'truth_cases':len(truth),'true_locus_in_plausible_set':sum(r['truth_locus'] in r.get('plausible_loci',[]) for r in truth),
            'per_class_recall':{'logical_discrepancy_detected':sum(r.get('discrepancy',False) for r in logical)/len(logical) if logical else None,
                                'logical_repair_verified':sum(r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT' for r in logical)/len(logical) if logical else None,
                                'clean_not_proposed':sum(not r.get('selected',False) for r in rs if r['variant']=='clean')/max(1,sum(r['variant']=='clean' for r in rs))},
            'variant_outcomes':variants,'variant_confusion_matrix':confusion,
            'alternative_verified_loci':sum(r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT' and r.get('selected_locus')!=r['truth_locus'] for r in truth),
            'rejected':sum(r['status']=='REJECTED' for r in rs),
            'inconclusive':sum(r['status'] in ('INCONCLUSIVE','INSUFFICIENT_EVIDENCE','INSUFFICIENT_BUDGET') for r in rs),
            'unique_causal_claims':0,
            'total_shots':sum(r.get('cost',{}).get('shots',0) for r in rs),
            'evaluations':sum(r.get('cost',{}).get('evaluations',0) for r in rs),
            'runtime_seconds':sum(r.get('cost',{}).get('runtime_seconds',0) for r in rs)}
    result={'protocol':frozen,'execution_source_sha256':hashes(),
            'revision':subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'split':split,'summaries':summaries,'rows':rows,'raw_root':str(out/'investigations')}
    (out/'summary.json').write_bytes(canonical(result));print(json.dumps(summaries,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--split',choices=SEEDS,default='development');ap.add_argument('--out',type=Path);args=ap.parse_args()
    if args.freeze:
        path=ROOT/'configs/counterfactual-protocol.json'
        with path.open('xb') as f:f.write(canonical(protocol()))
    else:run(args.split,args.out)
