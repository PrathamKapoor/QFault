import React,{useEffect,useMemo,useState} from 'react';
import Circuit from './quantum/Circuit';
type Data=Record<string,any>;
type Gate={name:string;qubits:number[];angle?:number};
const GATES=['h','x','z','s','rx','ry','rz','cx','cz','cp','swap'];
const TWO=['cx','cz','cp','swap'],ROT=['rx','ry','rz','cp'];
const label=(s:string)=>String(s).replaceAll('_',' ').toLowerCase();
async function api(path:string,body?:Data){
 const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:undefined);
 const v=await r.json();
 if(!r.ok)throw new Error(Array.isArray(v.detail)?v.detail.map((d:Data)=>(d.loc||[]).slice(1).join('.')+': '+d.msg).join(' · '):typeof v.detail==='string'?v.detail:JSON.stringify(v.detail));
 return v;
}
const CLUSTER:Data={schema_version:1,name:'Three-qubit cluster state',n_qubits:3,input:{kind:'computational_basis',bitstring:'000'},
 gates:[{name:'h',qubits:[0]},{name:'h',qubits:[1]},{name:'h',qubits:[2]},{name:'cz',qubits:[0,1]},{name:'cz',qubits:[1,2]}]};
const STAB={kind:'pauli_expectations',observables:['XZI','ZXZ','IZX'].map(p=>({pauli:p,expected:1,tolerance:0.1}))};
const TARGET_POLICIES=['adaptive_witness','coefficient_weighted','fixed','complementary_schedule','random'];
const zeroTarget=(n:number)=>({kind:'target_state',fidelity_tolerance:0.2,provenance:'user-declared',amplitudes:Array.from({length:2**n},(_,i)=>[i===0?1:0,0])});
const fmt=(x:number,d=3)=>Number.isFinite(x)?x.toFixed(d):'—';
function TargetEditor({contract,n,set}:{contract:Data;n:number;set:(c:Data)=>void}){
 const a:number[][]=contract.amplitudes||[];const norm=a.reduce((s,[r,i])=>s+r*r+i*i,0);
 const put=(k:number,j:number,v:number)=>set({...contract,amplitudes:a.map((x,i)=>i===k?(j===0?[v,x[1]]:[x[0],v]):x)});
 return <><p className="note">A pure target |ψ⟩ = Σ c<sub>k</sub>|k⟩, with k in Qiskit order (rightmost bit = q0). The claim is fidelity F = ⟨ψ|ρ|ψ⟩ ≥ 1 − tolerance; global phase is irrelevant. Measured witnesses can only <em>bound</em> F; exact F requires privileged simulation.</p>
  <div className="lab-row"><label>Fidelity tolerance<input name="fidelity_tolerance" type="number" min="0.01" max="0.99" step="0.01" value={contract.fidelity_tolerance} onChange={e=>set({...contract,fidelity_tolerance:+e.target.value})}/></label>
   <p className={'small '+(Math.abs(norm-1)<=1e-6?'muted':'lab-warn')} role="status">‖ψ‖² = {norm.toFixed(9)} {Math.abs(norm-1)<=1e-6?'· normalized':'· must be 1 within 1e-6 (not normalized silently)'}{a.length!==2**n?` · needs ${2**n} amplitudes for ${n} qubits`:''}</p>
   <button type="button" className="button secondary" onClick={()=>{const r=Math.sqrt(norm)||1;set({...contract,amplitudes:a.map(([x,y])=>[x/r,y/r])})}}>Normalize explicitly</button></div>
  <div className="table-scroll"><table><thead><tr><th>|k⟩</th><th>Re c<sub>k</sub></th><th>Im c<sub>k</sub></th><th>|c<sub>k</sub>|²</th></tr></thead><tbody>{a.map(([r,i],k)=><tr key={k}><td className="mono">|{k.toString(2).padStart(n,'0')}⟩</td>
   <td><input name={`re_${k}`} aria-label={`Real amplitude ${k}`} type="number" step="0.0001" value={r} onChange={e=>put(k,0,+e.target.value)}/></td>
   <td><input name={`im_${k}`} aria-label={`Imaginary amplitude ${k}`} type="number" step="0.0001" value={i} onChange={e=>put(k,1,+e.target.value)}/></td>
   <td>{fmt(r*r+i*i,4)}</td></tr>)}</tbody></table></div></>
}
function basisGates(setting:string){const n=setting.length,out:Gate[]=[];for(let q=0;q<n;q++){const c=setting[n-1-q];if(c==='Y')out.push({name:'rz',qubits:[q],angle:-Math.PI/2});if(c==='X'||c==='Y')out.push({name:'h',qubits:[q]})}return out}
function Intervals({claims}:{claims:Data[]}){
 const rows=claims.filter(c=>c.estimate!=null);if(!rows.length)return null;
 const dist=rows[0].kind==='distribution';const lo=dist?0:-1,hi=dist?1:1,W=640,L=150,span=W-L-20,x=(v:number)=>L+(Math.min(hi,Math.max(lo,v))-lo)/(hi-lo)*span;
 return <svg className="lab-intervals" viewBox={`0 0 ${W} ${rows.length*38+34}`} role="img" aria-label="Estimates with uncertainty intervals and tolerance bands per declared claim">
 {rows.map((c,i)=>{const y=24+i*38,e=c.kind==='distribution'?0:c.expected;return <g key={c.claim_id}>
  <text x="8" y={y+4} className="axis">{c.claim_id}</text>
  <rect x={x(e-c.tolerance)} y={y-9} width={Math.max(2,x(e+c.tolerance)-x(e-c.tolerance))} height="18" rx="3" fill="var(--slate)" opacity=".25"><title>tolerance band</title></rect>
  <line x1={x(c.interval[0])} x2={x(c.interval[1])} y1={y} y2={y} stroke={c.status==='VIOLATED'?'#c0392b':c.status==='UNRESOLVED'?'#b8860b':'#2e7d32'} strokeWidth="4"/>
  <circle cx={x(c.estimate)} cy={y} r="5" fill="var(--accent)"><title>{`estimate ${c.estimate.toFixed(3)} ± ${c.uncertainty_radius.toFixed(3)}`}</title></circle></g>})}
  <text x={L} y={rows.length*38+26} className="axis">{lo}</text><text x={W-20} y={rows.length*38+26} className="axis" textAnchor="end">{hi}</text></svg>
}
export default function CustomLab({page,navigate}:{page:string;navigate:(r:string)=>void}){
 const id=page.startsWith('/lab/')?page.slice(5):'';
 const [circuit,setCircuit]=useState<Data>(CLUSTER),[contract,setContract]=useState<Data>(STAB);
 const [circuitText,setCircuitText]=useState(JSON.stringify(CLUSTER,null,1)),[contractText,setContractText]=useState(JSON.stringify(STAB,null,1));
 const [mode,setMode]=useState('measurement_only'),[policy,setPolicy]=useState('adaptive'),[backend,setBackend]=useState('aer');
 const [readout,setReadout]=useState(0),[depol,setDepol]=useState(0),[batch,setBatch]=useState(1024),[maxShots,setMaxShots]=useState(8192),[maxEval,setMaxEval]=useState(24),[looks,setLooks]=useState(4),[seed,setSeed]=useState(42);
 const [examples,setExamples]=useState<Data[]>([]),[checked,setChecked]=useState<Data|null>(null),[result,setResult]=useState<Data|null>(null),[integrity,setIntegrity]=useState<Data|null>(null);
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[draft,setDraft]=useState<Gate>({name:'h',qubits:[0]});
 useEffect(()=>{api('/api/lab/examples').then(setExamples).catch(()=>{})},[]);
 useEffect(()=>{if(!id){setResult(null);return}let live=true;setError('');Promise.all([api('/api/experiments/'+id),api('/api/experiments/'+id+'/verification')]).then(([r,v])=>{if(live){setResult(r);setIntegrity(v)}}).catch(e=>live&&setError(e.message));return()=>{live=false}},[id]);
 const body=useMemo(()=>({circuit,contract,diagnostic_mode:mode,policy,backend,environment:{readout,depolarizing:depol},batch_shots:batch,max_shots:maxShots,max_evaluations:maxEval,max_looks:looks,seed}),[circuit,contract,mode,policy,backend,readout,depol,batch,maxShots,maxEval,looks,seed]);
 const syncCircuit=(c:Data)=>{setCircuit(c);setCircuitText(JSON.stringify(c,null,1));setChecked(null)};
 const syncContract=(c:Data)=>{setContract(c);setContractText(JSON.stringify(c,null,1));setChecked(null)};
 function applyJson(text:string,set:(v:Data)=>void,setText:(s:string)=>void,name:string){try{const v=JSON.parse(text);if(typeof v!=='object'||v===null||Array.isArray(v))throw new Error('must be an object');set(v)}catch(e){setError(name+' JSON: '+(e as Error).message);return}setError('');setText(text)}
 const gates:Gate[]=circuit.gates||[];
 const addGate=()=>{const g:Gate={name:draft.name,qubits:TWO.includes(draft.name)?draft.qubits.slice(0,2):draft.qubits.slice(0,1)};if(ROT.includes(draft.name))g.angle=draft.angle??0;syncCircuit({...circuit,gates:[...gates,g]})};
 const move=(i:number,d:number)=>{const j=i+d;if(j<0||j>=gates.length)return;const g=[...gates];[g[i],g[j]]=[g[j],g[i]];syncCircuit({...circuit,gates:g})};
 async function validate(){setBusy(true);setError('');try{setChecked(await api('/api/lab/validate',body))}catch(e){setChecked(null);setError((e as Error).message)}finally{setBusy(false)}}
 async function run(e:React.FormEvent){e.preventDefault();setBusy(true);setError('');try{const r=await api('/api/lab/investigations',body);navigate('/lab/'+r.experiment_id)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function replay(){setBusy(true);setError('');try{const r=await api('/api/lab/investigations/'+id+'/replay',{});navigate('/lab/'+r.experiment_id)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 const n=circuit.n_qubits||3;
 const d=result?.diagnosis;
 return <div className="lab">
  <p>Supply a validated structured circuit and an <strong>independently declared</strong> contract. QFAULT executes real Qiskit measurements, chooses further measurements under a strict budget, and reports what the evidence can and cannot establish. Bit and Pauli strings use Qiskit order: the leftmost character is the highest qubit.</p>
  {error&&<div className="error" role="alert">{error}</div>}
  {!id&&<>
  <section className="panel"><div className="panel-heading"><h2>1 · Submitted circuit</h2></div><div className="lab-body">
   <div className="lab-row"><label>Example<select name="example" aria-label="Example" defaultValue="" onChange={e=>{const x=examples.find(v=>v.id===e.target.value);if(x){syncCircuit(x.circuit);syncContract(x.contract)}}}><option value="">Load an example…</option>{examples.map(x=><option key={x.id} value={x.id}>{x.id}</option>)}</select></label>
    <label>Qubits<input name="n_qubits" type="number" min="2" max="5" value={n} onChange={e=>{const q=+e.target.value;syncCircuit({...circuit,n_qubits:q,input:{...circuit.input,bitstring:'0'.repeat(q)},gates:gates.filter(g=>g.qubits.every(x=>x<q))})}}/></label>
    <label>Input bitstring<input name="input_bitstring" aria-label="Input bitstring" className="mono" value={circuit.input?.bitstring||''} onChange={e=>syncCircuit({...circuit,input:{kind:'computational_basis',bitstring:e.target.value}})}/></label></div>
   <Circuit circuit={{n_qubits:n,gates}}/>
   <p className="small muted">Input preparation (X on qubits whose bit is 1) is added by QFAULT and is not part of this gate list.</p>
   <div className="lab-row"><label>Gate<select name="gate" aria-label="Gate" value={draft.name} onChange={e=>setDraft({...draft,name:e.target.value})}>{GATES.map(g=><option key={g}>{g}</option>)}</select></label>
    <label>{TWO.includes(draft.name)?'Control / first qubit':'Qubit'}<input name="gate_qubit" aria-label="Qubit" type="number" min="0" max={n-1} value={draft.qubits[0]} onChange={e=>setDraft({...draft,qubits:[+e.target.value,draft.qubits[1]??1]})}/></label>
    {TWO.includes(draft.name)&&<label>Target / second qubit<input name="gate_qubit2" aria-label="Second qubit" type="number" min="0" max={n-1} value={draft.qubits[1]??1} onChange={e=>setDraft({...draft,qubits:[draft.qubits[0],+e.target.value]})}/></label>}
    {ROT.includes(draft.name)&&<label>Angle (rad)<input name="gate_angle" aria-label="Angle" type="number" step="0.01" value={draft.angle??0} onChange={e=>setDraft({...draft,angle:+e.target.value})}/></label>}
    <button type="button" className="button secondary" onClick={addGate}>Add gate</button></div>
   <ol className="lab-gates">{gates.map((g,i)=><li key={i}><span className="mono">{g.name} {g.qubits.join(',')}{g.angle!=null?' · '+g.angle.toFixed(4):''}</span>
    <button type="button" className="text-button" aria-label={`Move gate ${i} earlier`} onClick={()=>move(i,-1)}>↑</button>
    <button type="button" className="text-button" aria-label={`Move gate ${i} later`} onClick={()=>move(i,1)}>↓</button>
    <button type="button" className="text-button" aria-label={`Remove gate ${i}`} onClick={()=>syncCircuit({...circuit,gates:gates.filter((_,j)=>j!==i)})}>remove</button></li>)}</ol>
   <details><summary>Circuit JSON (paste to import)</summary><textarea name="circuit_json" aria-label="Circuit JSON" className="mono" rows={10} value={circuitText} onChange={e=>setCircuitText(e.target.value)}/><button type="button" className="button secondary" onClick={()=>applyJson(circuitText,syncCircuit,setCircuitText,'Circuit')}>Apply circuit JSON</button></details>
  </div></section>
  <section className="panel"><div className="panel-heading"><h2>2 · Declared behavioral contract</h2></div><div className="lab-body">
   <label>Contract type<select aria-label="Contract type" value={contract.kind} name="contract_kind" onChange={e=>{const k=e.target.value;syncContract(k==='pauli_expectations'?STAB:k==='target_state'?zeroTarget(n):{kind:'measurement_distribution',basis:'Z',tolerance:0.1,expected_probabilities:{[ '0'.repeat(n)]:1}});setPolicy(k==='target_state'?'adaptive_witness':'adaptive')}}><option value="pauli_expectations">Pauli-observable expectations</option><option value="measurement_distribution">Measurement distribution</option><option value="target_state">Target state (pure)</option></select></label>
   {contract.kind==='target_state'?<TargetEditor contract={contract} n={n} set={syncContract}/>:contract.kind==='measurement_distribution'?<p className="note">A Z-basis distribution cannot reveal relative phase: two states with the same Z probabilities pass or fail together. Use Pauli expectations for phase-sensitive claims.</p>:<p className="note">Each observable is measured through a real basis-change circuit. Mutually qubit-wise compatible observables share shots. A violated expectation does not identify a faulty gate.</p>}
   {contract.kind==='pauli_expectations'&&<div className="table-scroll"><table><thead><tr><th>Pauli (q[n−1]…q[0])</th><th>Expected ∈ [−1,1]</th><th>Tolerance</th><th/></tr></thead><tbody>{(contract.observables||[]).map((o:Data,i:number)=><tr key={i}>
    <td><input name={`pauli_${i}`} aria-label={`Pauli ${i}`} className="mono" value={o.pauli} onChange={e=>syncContract({...contract,observables:contract.observables.map((x:Data,j:number)=>j===i?{...x,pauli:e.target.value.toUpperCase()}:x)})}/></td>
    <td><input name={`expected_${i}`} aria-label={`Expected ${i}`} type="number" step="0.1" value={o.expected} onChange={e=>syncContract({...contract,observables:contract.observables.map((x:Data,j:number)=>j===i?{...x,expected:+e.target.value}:x)})}/></td>
    <td><input name={`tolerance_${i}`} aria-label={`Tolerance ${i}`} type="number" step="0.01" value={o.tolerance} onChange={e=>syncContract({...contract,observables:contract.observables.map((x:Data,j:number)=>j===i?{...x,tolerance:+e.target.value}:x)})}/></td>
    <td><button type="button" className="text-button" onClick={()=>syncContract({...contract,observables:contract.observables.filter((_:Data,j:number)=>j!==i)})}>remove</button></td></tr>)}</tbody></table>
    <button type="button" className="button secondary" onClick={()=>syncContract({...contract,observables:[...contract.observables,{pauli:'Z'.repeat(n),expected:1,tolerance:0.1}]})}>Add observable</button></div>}
   <details open={contract.kind==='measurement_distribution'}><summary>Contract JSON</summary><textarea name="contract_json" aria-label="Contract JSON" className="mono" rows={8} value={contractText} onChange={e=>setContractText(e.target.value)}/><button type="button" className="button secondary" onClick={()=>applyJson(contractText,syncContract,setContractText,'Contract')}>Apply contract JSON</button></details>
  </div></section>
  <form onSubmit={run}><section className="panel"><div className="panel-heading"><h2>3 · Capability, policy and budget</h2></div><div className="lab-body lab-grid">
   <label>Diagnostic capability<select name="diagnostic_mode" aria-label="Diagnostic capability" value={mode} onChange={e=>setMode(e.target.value)}><option value="measurement_only">Measurement-only · sampled evidence only</option><option value="simulator_assisted">Simulator-assisted · privileged exact expectations</option></select></label>
   <label>Measurement policy<select name="policy" aria-label="Measurement policy" value={policy} onChange={e=>setPolicy(e.target.value)}>{contract.kind==='target_state'?<><option value="adaptive_witness">Adaptive witness · projected bound improvement</option><option value="coefficient_weighted">Coefficient-weighted order</option><option value="fixed">Fixed catalog order</option><option value="complementary_schedule">Predetermined complementary schedule</option><option value="random">Random admissible</option></>:<><option value="adaptive">Adaptive · unresolved-claim coverage</option><option value="fixed">Fixed round-robin</option><option value="complementary_schedule">Predetermined complementary schedule</option><option value="random">Random admissible</option></>}</select></label>
   <label>Backend<select name="backend" aria-label="Backend" value={backend} onChange={e=>setBackend(e.target.value)}><option value="aer">Qiskit Aer (density matrix)</option><option value="reference">Qiskit reference simulator</option></select></label>
   <label>Simulated readout error<input name="readout" type="number" min="0" max="0.5" step="0.01" value={readout} onChange={e=>setReadout(+e.target.value)}/></label>
   <label>Simulated gate depolarizing<input name="depolarizing" type="number" min="0" max="1" step="0.01" value={depol} onChange={e=>setDepol(+e.target.value)}/></label>
   <label>Shots per measurement<input name="batch_shots" type="number" min="64" max="10000" value={batch} onChange={e=>setBatch(+e.target.value)}/></label>
   <label>Total shot ceiling<input name="max_shots" type="number" min={2*batch} max="100000" value={maxShots} onChange={e=>setMaxShots(+e.target.value)}/></label>
   <label>Evaluation ceiling<input name="max_evaluations" type="number" min="2" max="100" value={maxEval} onChange={e=>setMaxEval(+e.target.value)}/></label>
   <label>Looks per measurement group<input name="max_looks" type="number" min="1" max="8" value={looks} onChange={e=>setLooks(+e.target.value)}/></label>
   <label>Seed<input name="seed" type="number" min="0" value={seed} onChange={e=>setSeed(+e.target.value)}/></label>
  </div><div className="lab-body"><p className="small muted">The simulated environment is chosen by you and is never visible to the measurement-only analyst.</p>
   <button type="button" className="button secondary" disabled={busy} onClick={validate}>Validate and check feasibility</button>{' '}
   <button className="button primary" disabled={busy}>{busy?'Executing…':'Run investigation'}</button></div></section></form>
  {checked&&<section className="panel"><div className="panel-heading"><h2>Validation and measurement feasibility</h2><span className="badge neutral">valid · {checked.circuit_id}</span></div><div className="lab-body">
   <p>Error allocation: α = {checked.feasibility.alpha_total} split over {checked.feasibility.alpha_per_interval.toExponential(2)} per interval; {checked.feasibility.claim_shots_available} shots available for claims, {checked.feasibility.reserved_control_shots} reserved for a readout control.</p>
   {checked.feasibility.catalog&&<p>Target witness catalog ({checked.feasibility.catalog.version}): {checked.feasibility.catalog.terms} non-identity Pauli terms in {checked.feasibility.catalog.groups} measurement groups · {checked.feasibility.catalog.stabilizer_target?'stabilizer target (projector bound available)':'non-stabilizer target (Pauli-expansion bound only)'} · {checked.feasibility.catalog.looks_affordable} batches affordable. Best-case measured lower bound {fmt(checked.feasibility.claims[0].best_case_lower)} vs threshold {fmt(checked.feasibility.claims[0].threshold)}: {checked.feasibility.claims[0].confirmable_within_tolerance?'confirmation possible':'confirmation impossible at this budget; only violations are detectable'}.</p>}
   {!checked.feasibility.catalog&&<div className="table-scroll"><table><thead><tr><th>Claim</th><th>Measurement setting</th><th>Best-case radius</th><th>Confirmable in tolerance</th></tr></thead><tbody>{checked.feasibility.claims.map((c:Data)=>{const g=checked.feasibility.groups.find((x:Data)=>x.claims.includes(c.claim_id));return <tr key={c.claim_id}><td className="mono">{c.claim_id}</td><td className="mono">{g?.setting}</td><td>{c.best_case_radius==null?'—':c.best_case_radius.toFixed(3)}</td><td>{c.confirmable_within_tolerance?'yes':'no — only large violations detectable'}</td></tr>})}</tbody></table></div>}
   <h3>Diagnostic measurement circuits (added by QFAULT; not part of your circuit)</h3>
   {checked.feasibility.groups.map((g:Data)=><details key={g.group_id}><summary className="mono lab-wrap">{g.setting} · {g.basis_gates} basis gate(s) · {g.terms?`${g.terms.length} witness term(s): ${g.terms.join(', ')}`:'covers '+g.claims.join(', ')}</summary><Circuit circuit={{n_qubits:n,gates:[...checked.executed_subject.gates,...basisGates(g.setting)]}}/><p className="small muted">Preparation + submitted gates + basis rotations; readout is in the computational basis. X: H. Y: rz(−π/2) then H.</p></details>)}
  </div></section>}</>}
  {id&&!result&&<p role="status">{error?'Investigation could not be loaded.':'Loading saved investigation…'}</p>}
  {id&&result&&d&&<>
  <section className="panel"><div className="panel-heading"><h2 id="lab-result" tabIndex={-1}>{label(d.category)}</h2><span className="badge neutral">{label(d.capability_mode)} · {d.policy}</span></div><div className="lab-body">
   <p>{d.reason}</p>
   <ul><li><strong>Detection:</strong> {label(d.detection.status)}{d.detection.violated_claims.length>0&&<> — violated: <span className="mono">{d.detection.violated_claims.join(', ')}</span></>}{d.detection.unresolved_claims.length>0&&<> — unresolved: <span className="mono">{d.detection.unresolved_claims.join(', ')}</span></>}</li>
    <li><strong>Attribution:</strong> {label(d.attribution.status)}. {d.attribution.statement}</li>
    <li><strong>Localization:</strong> {label(d.localization.status)}. {d.localization.statement}</li>
    <li><strong>Recovery:</strong> {label(result.recovery.status)} — {result.recovery.reason}</li>
    <li><strong>Stop:</strong> {label(d.stop.code)} — {d.stop.reason}</li></ul>
   <p>{result.cost.shots} / {result.cost.max_shots} shots · {result.cost.evaluations} / {result.cost.max_evaluations} evaluations · {result.cost.circuit_executions} circuit executions · {result.cost.exact_state_evaluations} privileged exact-state evaluations · {result.cost.basis_gates} basis gates.</p>
   {result.privileged_operations.length>0?<p><strong>Privileged simulator operation used:</strong> {result.privileged_operations.map((p:Data)=>p.operation+' ('+p.note+')').join('; ')}</p>:<p>No privileged simulator operation was used.</p>}
   <p className="small muted">Intervals are not class probabilities. A confirmed claim does not establish circuit correctness.</p>
  </div></section>
  {result.target_evidence&&<section className="panel"><div className="panel-heading"><h2>Target-state evidence</h2></div><div className="lab-body">
   <h3>Measurement-derived witness bound</h3>
   <svg className="lab-intervals" viewBox="0 0 640 70" role="img" aria-label={`Measured fidelity bound from ${fmt(result.target_evidence.fidelity_bound[0])} to ${fmt(result.target_evidence.fidelity_bound[1])}; threshold ${fmt(result.target_evidence.threshold)}`}>
    <line x1="20" x2="620" y1="34" y2="34" stroke="var(--border)" strokeWidth="2"/>
    <line x1={20+600*result.target_evidence.threshold} x2={20+600*result.target_evidence.threshold} y1="12" y2="56" stroke="#b8860b" strokeDasharray="4 3"/>
    <line x1={20+600*result.target_evidence.fidelity_bound[0]} x2={20+600*Math.max(result.target_evidence.fidelity_bound[0],result.target_evidence.fidelity_bound[1])} y1="34" y2="34" stroke={result.target_evidence.status==='VIOLATED'?'#c0392b':result.target_evidence.status==='UNRESOLVED'?'#b8860b':'#2e7d32'} strokeWidth="8"/>
    {result.target_evidence.exact&&<circle cx={20+600*result.target_evidence.exact.ideal_fidelity} cy="34" r="6" fill="none" stroke="var(--accent)" strokeWidth="2"><title>privileged ideal fidelity</title></circle>}
    <text x="20" y="66" className="axis">0</text><text x="620" y="66" className="axis" textAnchor="end">1</text><text x={20+600*result.target_evidence.threshold} y="10" className="axis" textAnchor="middle">threshold</text></svg>
   <p><strong>{result.target_evidence.label}</strong>: F ∈ [{fmt(result.target_evidence.fidelity_bound[0])}, {fmt(result.target_evidence.fidelity_bound[1])}] · threshold {fmt(result.target_evidence.threshold)} · {label(result.target_evidence.status)} · {result.target_evidence.terms_measured} of {result.target_evidence.terms_total} witness terms measured{result.target_evidence.stabilizer_target?' · stabilizer projector bound applied':''}.</p>
   <p className="small muted">{result.target_evidence.bound_method}. An unresolved bound is not a certification.</p>
   {result.target_evidence.witness_discrepancies.length>0&&<><h3>Witness discrepancies</h3><p className="small">{result.target_evidence.witness_discrepancy_note}</p><div className="table-scroll"><table><thead><tr><th>Pauli</th><th>Target</th><th>Measured</th><th>±</th></tr></thead><tbody>{result.target_evidence.witness_discrepancies.map((w:Data)=><tr key={w.pauli}><td className="mono">{w.pauli}</td><td>{fmt(w.target)}</td><td>{fmt(w.estimate)}</td><td>{fmt(w.radius)}</td></tr>)}</tbody></table></div></>}
   {result.target_evidence.exact?<div className="lab-privileged"><h3>SIMULATOR_ASSISTED_EXACT_STATE · privileged</h3><p>Ideal-circuit fidelity {fmt(result.target_evidence.exact.ideal_fidelity,4)} · gate-noise state fidelity {fmt(result.target_evidence.exact.gate_noise_state_fidelity,4)}.</p><p className="small">{result.target_evidence.exact.note}</p></div>:<p className="small muted">Measurement-only: no exact candidate state or fidelity was computed.</p>}
  </div></section>}
  <section className="panel"><div className="panel-heading"><h2>Claims and uncertainty</h2></div><div className="lab-body"><Intervals claims={result.claims}/>
   <div className="table-scroll"><table><thead><tr><th>Claim</th><th>Status</th><th>Estimate</th><th>±</th><th>Shots</th><th>Looks</th></tr></thead><tbody>{result.claims.map((c:Data)=><tr key={c.claim_id}><td className="mono">{c.claim_id}</td><td>{label(c.status)}</td><td>{c.estimate!=null?c.estimate.toFixed(3):c.interval?`[${fmt(c.interval[0])}, ${fmt(c.interval[1])}]`:'—'}</td><td>{c.uncertainty_radius!=null?c.uncertainty_radius.toFixed(3):'bound'}</td><td>{c.shots}</td><td>{c.looks}</td></tr>)}</tbody></table></div></div></section>
  <section className="panel"><div className="panel-heading"><h2>Evidence-action timeline</h2><span className="small muted">completed history · recorded after synchronous execution</span></div><div className="lab-body"><ol className="lab-timeline">
   {result.action_ledger.map((a:Data)=><li key={a.action_id}><strong>{a.action_id} · measure <span className="mono">{a.measurement_specification.setting}</span> (look {a.measurement_specification.look})</strong>
    <p>{a.reason_selected}</p>
    {a.derived_expectations?<p className="small lab-wrap">Witnesses: {Object.entries(a.derived_expectations).map(([k,v]:[string,any])=>`${k} ${v.estimate.toFixed(3)} ± ${v.radius.toFixed(3)} (target ${v.target.toFixed(3)})`).join('; ')} → bound [{fmt(a.observed_result['target:fidelity'].bounds[0])}, {fmt(a.observed_result['target:fidelity'].bounds[1])}] · {label(a.observed_result['target:fidelity'].status)}</p>
    :<p className="small">Result: {Object.entries(a.observed_result).map(([k,v]:[string,any])=>`${k} ${label(v.status)} (${v.estimate.toFixed(3)} ± ${a.uncertainty[k].toFixed(3)})`).join('; ')}</p>}
    <p className="small muted">{a.shots_executed} shots · {a.basis_gates} basis gates · {a.execution_backend} · remaining {a.remaining_budget.shots} shots / {a.remaining_budget.evaluations} evaluations</p></li>)}
   {d.attribution.readout_control&&<li><strong>Readout control</strong><p>TV {d.attribution.readout_control.total_variation.toFixed(3)} ± {d.attribution.readout_control.uncertainty_radius.toFixed(3)} · {d.attribution.readout_control.significant_disagreement?'significant: noise consistent':'not significant: gate noise and logical faults remain indistinguishable'}</p></li>}
   <li><strong>Stop</strong><p>{d.stop.reason}</p></li></ol></div></section>
  <section className="panel"><div className="panel-heading"><h2>Provenance and export</h2></div><div className="lab-body">
   <p className="mono small">{result.experiment_id} · circuit {result.circuit_id} · {result.contract.contract_id}</p>
   <p>{integrity?.valid?'Artifact hashes verified.':'Integrity check failed or pending.'} Statistical design: {result.statistical_design.method}.</p>
   <details><summary>Executed subject circuit (preparation + submitted gates)</summary><Circuit circuit={result.executed_subject}/><pre className="mono small">{result.circuit_diagram}</pre></details>
   <a className="button secondary" href={'/api/experiments/'+id+'/report'} download>Export verified report</a>{' '}
   <button className="button secondary" disabled={busy} onClick={replay}>Replay recorded configuration</button>{' '}
   <button className="text-button" onClick={()=>navigate('/lab')}>New custom investigation</button></div></section></>}
 </div>
}
