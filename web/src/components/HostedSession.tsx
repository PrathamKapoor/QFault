/// <reference types="vite/client" />
import React,{useEffect,useState} from 'react';
import './HostedSession.css';
import {demoRequest} from '../guided/api';
import SessionControls from './SessionControls';

export default function HostedSession({children}:{children:React.ReactNode}){
 const hosted=import.meta.env.VITE_QFAULT_HOSTED==='1';
 const [ready,setReady]=useState(!hosted),[attempt,setAttempt]=useState(0),[error,setError]=useState(''),[elapsed,setElapsed]=useState(0);
 useEffect(()=>{
  if(!hosted)return;
  let active=true;setError('');
  const controller=new AbortController();
  demoRequest('/api/hosted-session',{}, {kind:'bootstrap',signal:controller.signal})
   .then(data=>{if(data.hosting?.session_scope!=='browser cookie')throw new Error('Unexpected hosted-session response.');if(active)setReady(true)})
   .catch(()=>{if(active)setError('Could not connect to private report storage. No investigation has started. Retry when the service is available.');});
  return()=>{active=false;controller.abort()};
 },[hosted,attempt]);
 useEffect(()=>{if(ready)return;const began=Date.now(),timer=setInterval(()=>setElapsed((Date.now()-began)/1000),500);return()=>clearInterval(timer)},[ready,attempt]);
 if(!hosted)return <>{children}</>;
 if(!ready)return <section className="hosted-connect" aria-live="polite"><h1>Opening your report session</h1>{error?<><p role="alert">{error}</p><button className="button primary" onClick={()=>setAttempt(value=>value+1)}>Retry connection</button></>:<p role="status">{elapsed.toFixed(0)} seconds elapsed. Connecting to the hosted workbench. The first request can take longer while the simulator starts.</p>}</section>;
 return <>{children}</>;
}

export function HostedReportNotice(){
 if(import.meta.env.VITE_QFAULT_HOSTED!=='1')return null;
 return <aside className="hosted-notice" aria-label="Hosted report privacy"><strong>Private browser-session reports</strong><span>Real Qiskit Aer simulation — executed on the server. No quantum-hardware execution. Hosted usage limits apply. Reports are saved privately; this browser’s cookie controls access.</span><SessionControls/></aside>;
}
