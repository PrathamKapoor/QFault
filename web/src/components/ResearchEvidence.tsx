import React,{useEffect,useState} from 'react';
import './ResearchEvidence.css';
import {demoRequest} from '../guided/api';
type Data=Record<string,any>;

export default function ResearchEvidence(){
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState('');
 useEffect(()=>{let active=true;const controller=new AbortController();demoRequest('/api/research',undefined,{signal:controller.signal}).then(v=>{if(active)setData(v)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false;controller.abort()}},[]);
 if(error)return <p role="status">{error}. No result is substituted.</p>;
 if(!data)return <p role="status">Loading recorded research evidence…</p>;
 const conservative=data.recovery.conservative,point=data.recovery.point_discrepancy;
 return <div data-research="measured-recovery"><p>Bounded measured recovery on {data.architectures} external holdout programs. Recorded simulation results, not live telemetry.</p>
 <div className="research-metrics"><article><strong>{conservative.verified}<span>/{conservative.runs}</span></strong><h3>Conservative repairs verified</h3><p>{conservative.verified}/{conservative.eligible} measurement-eligible cases</p></article>
 <article><strong>{point.verified}<span>/{point.runs}</span></strong><h3>Point-ranked repairs verified</h3><p>{point.verified}/{point.eligible} measurement-eligible cases · same resource ceilings</p></article>
 <article><strong>{conservative.rejected}<span> / {point.rejected}</span></strong><h3>Fresh proposals rejected</h3><p>Conservative / point ranking</p></article>
 <article><strong>{conservative.noise_only_proposals}<span> / {point.noise_only_proposals}</span></strong><h3>Noise-only proposals</h3><p>Conservative / point ranking</p></article></div>
 <p className="research-limit">{data.comparison.equal_verified_yield?'Equal verified yield in this corpus.':'Verified yield differs in this corpus.'} Conservative used {conservative.shots.toLocaleString()} shots; point ranking used {point.shots.toLocaleString()}.{data.comparison.relative_shot_reduction!=null&&` Conservative used ${(data.comparison.relative_shot_reduction*100).toFixed(1)}% fewer shots.`} Rejected proposals are not falsely verified repairs. Small, correlated simulation cases do not establish population superiority.</p>
 <p className="small lab-wrap">Protocol: {data.protocol}. Evaluated source: <span className="mono">{data.source_commit}</span>. Raw evidence: {data.evidence.available?'available':'unavailable in this source-only copy'}. Historical template findings remain in Benchmarks.</p>
 <a href="https://github.com/PrathamKapoor/QFault/blob/main/docs/evidence-availability.md" target="_blank" rel="noreferrer">Evidence availability and verification ↗</a></div>
}
