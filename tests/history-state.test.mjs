import test from 'node:test';import assert from 'node:assert/strict';
const m=await import('../web/src/guided/history.ts').catch(()=>null);
test('newer history request wins and only real completed identities invalidate',async()=>{
 assert.ok(m,'history controller missing');let pending=[],seen=[];
 const loader=m.historyLoader(()=>new Promise(r=>pending.push(r)),rows=>seen.push(rows));
 const a=loader(),b=loader();pending[1](['new']);await b;pending[0](['old']);await a;assert.deepEqual(seen,[['new']]);
 assert.equal(m.completedIdentity({experiment_id:'experiment_'+'a'.repeat(32)}),true);
 assert.equal(m.completedIdentity({status:'BACKEND_ERROR'}),false);
});
test('obsolete read errors cannot replace a successful newer history',async()=>{
 assert.ok(m);let pending=[],seen=[];
 const loader=m.historyLoader(()=>new Promise((resolve,reject)=>pending.push({resolve,reject})),r=>seen.push(r));
 const old=loader(),fresh=loader();pending[1].resolve(['new']);await fresh;pending[0].reject(Error('stale failure'));await old;
 assert.deepEqual(seen,[['new']]);
});
