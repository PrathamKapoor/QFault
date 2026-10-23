import test from 'node:test';import assert from 'node:assert/strict';
const m=await import('../web/src/guided/requests.ts').catch(()=>null);
test('safe reads retry transient failures, never authorization or invalid JSON',async()=>{
 assert.ok(m);let calls=0;
 const fetcher=async()=>{calls++;if(calls<3)throw Error('offline');return new Response('{"ok":true}')};
 assert.equal((await m.jsonRequest('/read',undefined,{fetcher,backoff:1,timeout:30})).ok,true);assert.equal(calls,3);
 for(const status of [400,401,403,422]){calls=0;await assert.rejects(m.jsonRequest('/read',undefined,{fetcher:async()=>{calls++;return new Response('{"detail":"invalid"}',{status})},backoff:1}));assert.equal(calls,1)}
});
test('execution deadline is unknown completion and never repeats the POST',async()=>{
 assert.ok(m);let calls=0;
 await assert.rejects(m.jsonRequest('/execute',{}, {kind:'execution',timeout:10,fetcher:async(_,{signal})=>{calls++;return new Promise((_,reject)=>signal.addEventListener('abort',()=>reject(Error('aborted'))))}}),e=>e.status===0&&/may still be running/.test(e.message));assert.equal(calls,1);
});
