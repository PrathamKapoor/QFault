import React from 'react';
import {displayInterval,resultSummary} from '../guided/presentation';
type Data=Record<string,any>;
const pair=(v:any)=>Array.isArray(v)?`[${v.map((n:number)=>Number.isFinite(n)?n.toFixed(3):String(n)).join(', ')}]`:'Unmeasured';
export function ClaimInterval({claim}:{claim:Data}){
 const metric=claim.kind==='pauli_expectation'||claim.claim_id?.startsWith('obs:')?'pauli':claim.kind==='distribution'||claim.claim_id?.startsWith('dist:')?'tv':'other';
 const raw=claim.interval??(Number.isFinite(claim.estimate)&&Number.isFinite(claim.uncertainty_radius)?[claim.estimate-claim.uncertainty_radius,claim.estimate+claim.uncertainty_radius]:null);
 const value=displayInterval(raw,metric);
 return <><span>{value.state==='inconsistent'?'Inconsistent interval — inspect raw evidence':value.state==='unmeasured'?'Unmeasured':pair(value.display)}</span><details><summary>Interval definition and raw evidence</summary><p>Metric: {metric==='tv'?'TV distance [0,1]':metric==='pauli'?'Pauli expectation [−1,1]':'Recorded parameter; no domain transformation'}. Dimensionless. Tolerance: {claim.tolerance??'see contract'}.</p><p>Raw interval: {pair(raw)}. Displayed: {pair(value.display)}.</p><p>Only the display intersects a concentration interval with its known physical domain. Stored evidence and all decisions are unchanged. Empty or nonfinite intervals are inconsistent, never repaired by clipping.</p></details></>;
}
export default function ResultSummary({result}:{result:Data}){
 const s=resultSummary(result);
 return <section className="guided-card result-summary" aria-label="Result summary" data-testid="result-summary"><h3>{s.title}</h3>{s.edit&&<p><strong>Selected edit: {s.edit}.</strong></p>}{result.verification&&<p>Original: {s.original}. Candidate: {s.candidate}.</p>}<p>{s.tested!==undefined?`${s.tested} / ${s.generated} generated edits tested · `:''}<strong>{s.shots.toLocaleString()} total shots</strong>{s.freshShots>0?` · ${s.freshShots.toLocaleString()} fresh verification shots (${s.originalFresh.toLocaleString()} original + ${s.candidateFresh.toLocaleString()} candidate)`:''}.</p><p>{s.scope}</p></section>;
}
