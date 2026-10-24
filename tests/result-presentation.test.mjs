import test from 'node:test';
import assert from 'node:assert/strict';
const m=await import('../web/src/guided/presentation.ts').catch(()=>null);
test('physical display intersects only declared TV and Pauli domains, retaining raw evidence',()=>{
 assert.ok(m,'presentation helpers missing');
 for(const [raw,metric,want] of [[[-.037,.147],'tv',[0,.147]],[[-1.134,-.866],'pauli',[-1,-.866]],[[.866,1.134],'pauli',[.866,1]],[[0,1],'tv',[0,1]],[[1,1],'pauli',[1,1]],[[-3,4],'loss',[-3,4]]]){
  const before=JSON.stringify(raw),v=m.displayInterval(raw,metric);assert.deepEqual(v.display,want);assert.equal(v.state,'measured');assert.equal(JSON.stringify(raw),before);assert.deepEqual(v.raw,raw);
 }
 for(const raw of [[2,3],[-3,-2],[1,0],[0,Infinity],[NaN,1]])assert.equal(m.displayInterval(raw,'pauli').state,'inconsistent');
 assert.equal(m.displayInterval(null,'tv').state,'unmeasured');
});
test('summary uses actual verdict/edit/paired cost without manufacturing selections',()=>{
 assert.ok(m);const r={status:'VERIFIED_UNDER_DECLARED_CONTRACT',circuit:{input:{bitstring:'00'}},cost:{shots:120,tested_candidates:2,generated_candidates:4,phase_shots:{verification_original:20,verification_candidate:20}},selected_candidate:{edit:{operator:'remove',index:3,before:{name:'z',qubits:[0]},after:null}},verification:{original:{loss_interval:[2,3]},candidate:{loss_interval:[0,.8]}}};
 const s=m.resultSummary(r);assert.match(s.edit,/remove Z.*qubit 0/i);assert.equal(s.freshShots,40);assert.equal(s.shots,120);assert.match(s.original,/discrepancy/i);assert.match(s.candidate,/supported/i);
 for(const status of ['NO_SIGNIFICANT_DISCREPANCY','SIGNIFICANT_DISCREPANCY','REJECTED','INSUFFICIENT_EVIDENCE','INSUFFICIENT_BUDGET','NOISE_CONTROL_ABSTENTION','BACKEND_ERROR','UNKNOWN']){
  const v=m.resultSummary({status,cost:{shots:0}});assert.ok(v.title);assert.equal(v.edit,null);assert.equal(v.shots,0);
 }
 assert.equal(m.resultSummary({status:'BACKEND_ERROR'}).shots,null,'missing failure cost must not be invented as zero');
});
