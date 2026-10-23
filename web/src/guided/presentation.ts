/** Display transforms only. Never mutate records or make a scientific decision. */
export function displayInterval(raw:unknown,metric:string){
 if(raw==null)return {state:'unmeasured',raw,display:null};
 if(!Array.isArray(raw)||raw.length!==2||!raw.every(v=>typeof v==='number'&&Number.isFinite(v))||raw[0]>raw[1])return {state:'inconsistent',raw,display:null};
 const domain=metric==='tv'?[0,1]:metric==='pauli'?[-1,1]:null;
 const display=domain?[Math.max(raw[0],domain[0]),Math.min(raw[1],domain[1])]:[...raw];
 return {state:display[0]>display[1]?'inconsistent':'measured',raw,display:display[0]>display[1]?null:display};
}
const TITLES:Record<string,string>={NO_SIGNIFICANT_DISCREPANCY:'Declared measured behavior supported',SIGNIFICANT_DISCREPANCY:'A measured discrepancy was detected',VERIFIED_UNDER_DECLARED_CONTRACT:'Intervention verified for this contract',REJECTED:'Intervention rejected by fresh evidence',INSUFFICIENT_EVIDENCE:'More evidence is needed',INSUFFICIENT_BUDGET:'The required measurements could not be funded',NOISE_CONTROL_ABSTENTION:'Noise control: no edit recommended',BACKEND_ERROR:'Backend execution failed',UNKNOWN:'Completion is unknown',NO_REPAIR_NEEDED:'No repair needed under this contract',INCONCLUSIVE:'Fresh evidence is inconclusive'};
function assessment(value:any){const v=value?.loss_interval;return !Array.isArray(v)||!v.every(Number.isFinite)||v[0]>v[1]?'Not established':v[1]<=1?'Declared contract supported':v[0]>1?'Contract discrepancy supported':'Unresolved at this budget'}
export function resultSummary(r:Record<string,any>){
 const status=r.status||r.diagnosis?.category||'UNKNOWN',edit=r.selected_candidate?.edit;
 const before=edit?.before,after=edit?.after;
 return {status,title:TITLES[status]||status.replaceAll('_',' ').toLowerCase(),
  edit:edit?`${edit.operator} ${before?.name?.toUpperCase()||after?.name?.toUpperCase()||'gate'} on qubit ${(before?.qubits||after?.qubits||[]).join(', ')}${after&&before?' → '+after.name.toUpperCase():''} (operation ${edit.index})`:null,
  original:assessment(r.verification?.original||r.original_evidence),candidate:assessment(r.verification?.candidate),
  shots:r.cost?.shots??0,tested:r.cost?.tested_candidates,generated:r.cost?.generated_candidates,
  originalFresh:r.cost?.phase_shots?.verification_original??0,candidateFresh:r.cost?.phase_shots?.verification_candidate??0,
  freshShots:(r.cost?.phase_shots?.verification_original??0)+(r.cost?.phase_shots?.verification_candidate??0),
  scope:`Applies to input ${r.circuit?.input?.bitstring??'declared in this record'} and this contract. No universal equivalence or unique cause is established.`};
}
