import React,{useEffect,useRef,useState} from 'react';
import {demoRequest,recoverOperation} from '../guided/api';
import {HISTORY_EVENT} from '../guided/history';
export default function SessionControls(){
 const [info,setInfo]=useState<any>(null),[error,setError]=useState(''),[confirmation,setConfirmation]=useState(false),[busy,setBusy]=useState(false),[operation,setOperation]=useState<any>(null);
 const generation=useRef(0);
 async function refresh(){const mine=++generation.current;try{const value=await demoRequest('/api/session');if(mine===generation.current)setInfo(value)}catch(e){if(mine===generation.current)setError((e as Error).message)}}
 useEffect(()=>{void refresh();const update=()=>void refresh();window.addEventListener(HISTORY_EVENT,update);return()=>{generation.current++;window.removeEventListener(HISTORY_EVENT,update)}},[]);
 async function remove(){if(!confirmation||busy)return;setBusy(true);setError('');try{
  const response=await demoRequest('/api/session/delete',{confirm:'DELETE MY SESSION DATA'},{kind:'validation'});
  if(!response.deleted)throw Error('Deletion was not confirmed by the server.');
  for(let i=sessionStorage.length-1;i>=0;i--){const key=sessionStorage.key(i);if(key?.startsWith('qfault-'))sessionStorage.removeItem(key)}
  location.reload();
 }catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function reset(){setError('');try{
  await demoRequest('/api/hosted-session',{reset:true},{kind:'bootstrap'});
  for(let i=sessionStorage.length-1;i>=0;i--){const key=sessionStorage.key(i);if(key?.startsWith('qfault-'))sessionStorage.removeItem(key)}location.reload();
 }catch(e){setError((e as Error).message)}}
 async function recover(){setError('');try{
  const raw=sessionStorage.getItem('qfault-last-operation');if(!raw)throw Error('No operation identity is stored in this tab.');
  const value=await recoverOperation(JSON.parse(raw).id);setOperation(value.operation);await refresh();
 }catch(e){setError((e as Error).message)}}
 return <details className="hosted-session-controls"><summary>Session allowance, export, recovery and deletion {info?`— ${info.remaining_operations} operations remaining`:''}</summary>
  {error&&<><p role="alert">{error}</p><button className="button secondary" onClick={reset}>Open a new session after confirmed deletion</button></>}
  {info?<><p>{info.remaining_operations} / {info.operation_limit} operations remaining. {info.consumes}</p><p>Cookie access expires {new Date(info.access_expires_at*1000).toLocaleString()}. Clearing cookies or changing browsers loses access. Export important reports.</p><p>Retention: {info.retention.expires_at?`eligible for prospective cleanup after90days on ${new Date(info.retention.expires_at*1000).toLocaleString()}`:'Legacy content preserved; no new deletion deadline applied'}. {info.retention.cleanup}</p></>:<p>Loading your session limits…</p>}
  <button className="button secondary" onClick={()=>void refresh()}>Refresh session status</button>{' '}<a className="button secondary" href="/api/session/export" download>Export all accessible reports</a>
  <p>Public admission permits one active execution and at most100 admissions /5million reserved shot-ceilings per UTC day across all sessions. No queue; busy requests start no computation. Hosted custom limits are250,000shots,160evaluations and120cooperative seconds per request. Local mode remains available for larger work.</p><p>Complete exports include report identities, manifests and raw evidence, limited to 4 MiB compressed / 32 MiB expanded. A missing or corrupt report refuses the complete export.</p>
  <button className="button secondary" onClick={recover}>Recover last submitted operation</button>
  {operation&&<p role="status">Operation {operation.operation_id}: {operation.state}. {operation.result_id&&<>Saved result <code>{operation.result_id}</code>. Open Saved investigations to inspect it.</>} No computation was resubmitted.</p>}
  <p><strong>Delete this session’s data permanently.</strong> Reports cannot be recovered after deletion. An active operation prevents deletion; expired interrupted writers are fenced. Other browser sessions are unaffected.</p>
  <label><input type="checkbox" checked={confirmation} onChange={e=>setConfirmation(e.target.checked)}/> I understand the permanent loss and have exported reports I need.</label>{' '}
  <button className="button secondary" disabled={!confirmation||busy} onClick={remove}>{busy?'Waiting for server deletion…':'Permanently delete this session data'}</button>
 </details>;
}
