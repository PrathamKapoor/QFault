import test from 'node:test';
import assert from 'node:assert/strict';

const mod=await import('../web/src/guided/session.ts').catch(()=>null);
const id='experiment_'+'a'.repeat(32);

test('a measured discrepancy and inspected limits are required before recovery',()=>{
 assert.ok(mod,'guided stage controller is missing');
 assert.equal(mod.canVisit('phase',{},false),false);
 assert.equal(mod.canVisit('phase',{z:{experiment_id:id,diagnosis:{category:'NO_SIGNIFICANT_DISCREPANCY'}}},false),true);
 assert.equal(mod.canVisit('verify',{phase:{diagnosis:{category:'INSUFFICIENT_EVIDENCE'}}},true),false);
 assert.equal(mod.canVisit('verify',{phase:{diagnosis:{category:'SIGNIFICANT_DISCREPANCY'}}},false),false);
 assert.equal(mod.canVisit('verify',{phase:{diagnosis:{category:'SIGNIFICANT_DISCREPANCY'}}},true),true);
 assert.equal(mod.canVisit('export',{recovery:{experiment_id:id,status:'REJECTED'}},true),true);
});

test('synchronous execution admission suppresses duplicate work and releases on error',async()=>{
 assert.ok(mod,'guided execution guard is missing');
 const gate=new mod.ExecutionGate();let calls=0,finish;
 const pending=gate.run(()=>{calls++;return new Promise(resolve=>{finish=resolve})});
 const duplicate=await gate.run(async()=>{calls++});
 assert.equal(duplicate,false);assert.equal(calls,1);
 finish('done');assert.equal(await pending,'done');
 await assert.rejects(gate.run(async()=>{throw new Error('connection failed')}),/connection failed/);
 assert.equal(await gate.run(async()=>42),42);
});

test('refresh retains returned identities and marks interrupted execution without retrying',()=>{
 assert.ok(mod,'guided session persistence is missing');
 const values=new Map();const storage={getItem:k=>values.get(k)??null,setItem:(k,v)=>values.set(k,v)};
 const session=mod.createGuide();session.ids.z=id;session.pending={key:'recovery',phase:'executing',startedAt:10};
 mod.writeGuide(storage,session);
 const loaded=mod.readGuide(storage);
 assert.equal(loaded.session.ids.z,id);
 assert.equal(loaded.session.pending.phase,'unknown');
 assert.match(loaded.warning,/completion is unknown/i);
 const next=mod.restartGuide(storage,loaded.session);
 assert.equal(next.ids.z,undefined);assert.notEqual(next.sessionId,session.sessionId);
 assert.ok([...values.values()].some(v=>v.includes(id)), 'old returned identities must remain discoverable');
});

test('malformed local state cannot manufacture a completed run',()=>{
 assert.ok(mod,'guided session validation is missing');
 for(const raw of ['null','[]','{"schema_version":999}','{"schema_version":1,"ids":{"z":"../../private"}}']){
  const loaded=mod.readGuide({getItem:()=>raw,setItem:()=>{}});
  assert.deepEqual(loaded.session.ids,{});assert.ok(loaded.warning);
 }
});
