/// <reference types="vite/client" />
import React,{useEffect,useState} from 'react';
import './HostedSession.css';

export default function HostedSession({children}:{children:React.ReactNode}){
 const hosted=import.meta.env.VITE_QFAULT_HOSTED==='1';
 const [ready,setReady]=useState(!hosted),[attempt,setAttempt]=useState(0),[error,setError]=useState('');
 useEffect(()=>{
  if(!hosted)return;
  let active=true;setError('');
  fetch('/api/hosted-session',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})
   .then(async response=>{if(!response.ok)throw new Error('The hosted report session is unavailable.');const data=await response.json();if(data.hosting?.session_scope!=='browser cookie')throw new Error('Unexpected hosted-session response.');if(active)setReady(true)})
   .catch(()=>{if(active)setError('Could not connect to private report storage. No investigation has started. Retry when the service is available.');});
  return()=>{active=false};
 },[hosted,attempt]);
 if(!hosted)return <>{children}</>;
 if(!ready)return <section className="hosted-connect" aria-live="polite"><h1>Opening your report session</h1>{error?<><p role="alert">{error}</p><button className="button primary" onClick={()=>setAttempt(value=>value+1)}>Retry connection</button></>:<p role="status">Connecting to the hosted workbench. The first request can take longer while the simulator starts.</p>}</section>;
 return <>{children}</>;
}

export function HostedReportNotice(){
 if(import.meta.env.VITE_QFAULT_HOSTED!=='1')return null;
 return <aside className="hosted-notice" aria-label="Hosted report privacy"><strong>Private browser-session reports</strong><span>Reports are saved in private storage. This browser’s cookie controls access for 30 days; export important reports before clearing cookies or changing browsers. Limit: 64 operations per session.</span></aside>;
}
