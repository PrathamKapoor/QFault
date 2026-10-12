import React,{lazy,Suspense,useEffect,useRef,useState} from 'react';
import Mark from '../branding/Mark';
import TechText from '../effects/TechText';
import PixelSwap from '../effects/PixelSwap';
import './landing.css';

const Hyperspeed=lazy(()=>import('../effects/Hyperspeed'));
const MoltenMetal=lazy(()=>import('../effects/MoltenMetal'));
const Sculpture=lazy(()=>import('./Sculpture'));
export function useReducedMotion(){const [value,setValue]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);useEffect(()=>{const m=matchMedia('(prefers-reduced-motion: reduce)'),change=()=>setValue(m.matches);m.addEventListener('change',change);return()=>m.removeEventListener('change',change)},[]);return value}
function seen(){try{return sessionStorage.getItem('qfault-intro')==='1'}catch{return false}}
function remember(){try{sessionStorage.setItem('qfault-intro','1')}catch{/* private browsing */}}

export default function Landing({navigate}:{navigate:(route:string)=>void}){
  const reduced=useReducedMotion();
  const [phase,setPhase]=useState(()=>reduced||seen()?'hero':'hyperspeed'),[swap,setSwap]=useState(false);
  const locked=useRef(false),destination=useRef('/workbench');
  const finish=()=>{remember();navigate(destination.current)};
  useEffect(()=>{
    // Fetch the sculpture chunk while the introduction runs, without creating a GL context.
    void import('./Sculpture');
    if(reduced&&(phase==='hyperspeed'||phase==='techtext'))setPhase('hero');
    const timer=phase==='hyperspeed'?window.setTimeout(()=>setPhase('techtext'),650):phase==='techtext'?window.setTimeout(()=>{remember();setPhase('hero')},650):phase==='reframe'?window.setTimeout(()=>setPhase('swap'),470):phase==='swap'?window.setTimeout(finish,1150):0;
    return()=>clearTimeout(timer);
  },[phase,reduced]);
  useEffect(()=>{if(phase==='swap'){const timer=window.setTimeout(()=>setSwap(true),40);return()=>clearTimeout(timer)}},[phase]);
  useEffect(()=>{const escape=(e:KeyboardEvent)=>{if(e.key==='Escape'){if(locked.current)finish();else{remember();setPhase('hero')}}};window.addEventListener('keydown',escape);return()=>window.removeEventListener('keydown',escape)},[]);
  function enter(route='/workbench'){if(locked.current)return;locked.current=true;destination.current=route;window.scrollTo(0,0);if(reduced)finish();else setPhase('reframe')}
  function scrollTo(e:React.MouseEvent,id:string){e.preventDefault();document.getElementById(id)?.scrollIntoView({behavior:reduced?'instant':'smooth'});}
  const hero=phase==='hero'||phase==='reframe'||phase==='swap';
  return <div className={'landing '+(phase==='reframe'||phase==='swap'?'landing--reframe':'')} data-phase={phase}>
    <h1 className="sr-only">QFAULT</h1>
    <header className="landing-nav"><a href="#/" className="landing-brand"><Mark/><span>QFAULT</span></a><nav aria-label="Primary"><a href="#/" onClick={e=>scrollTo(e,'platform')}>Platform</a><a href="#/" onClick={e=>scrollTo(e,'research')}>Research</a><button onClick={()=>enter('/benchmarks')}>Benchmarks</button><a href="https://github.com/PrathamKapoor/QTrust" target="_blank" rel="noreferrer">GitHub ↗</a><button className="nav-enter" aria-label="Enter Workbench from navigation" onClick={()=>enter()}>Enter Workbench <span aria-hidden="true">↗</span></button></nav></header>
    {!hero&&<><div className="intro-status" role="status">{phase==='hyperspeed'?'Initializing quantum workspace':'Quantum failure analysis & recovery'}</div><button className="skip-intro" onClick={()=>{remember();setPhase('hero')}}>Skip intro <span>Esc</span></button></>}
    {phase==='hyperspeed'&&<Suspense fallback={<div className="intro-fallback"/>}><Hyperspeed className="intro-speed" curve="straight" curvature={.2} speed={1.4} density={45} trailLength={2.5} poles={0} dust={80} glow={.22} reflections={0} roadOpacity={0} lineColor="#000000" roadColor="#050507" background="#050507" tailColors={['#55408a','#77659c']} headColors={['#b9b6d2','#5362a2']} interactive={false}/></Suspense>}
    {phase==='techtext'&&<div className="tech-reveal" aria-hidden="true"><TechText text="QFAULT" color="#e3deed" accentColor="#7b5cff" fontWeight={750} fontSize={innerWidth*.152} letterSpacing={-.065} specks={8} selection={false} labels={false} draggable={false} speed={16} reveal="letter"/></div>}
    {hero&&<>
      <div className="landing-hero">
      {phase==='hero'&&<Suspense fallback={null}><MoltenMetal className="metal-atmosphere" color1="#17151e" color2="#4b395f" color3="#8b7d9e" speed={.12} opacity={.48} glow={1.6} coreSize={.23} scale={3.3} detail={4} blackPoint={.02} brightness={1.35} grain={false} mouseInteraction={false} animated={!reduced&&innerWidth>=768&&(navigator.hardwareConcurrency||4)>4}/></Suspense>}
      <div className="landing-vignette" aria-hidden="true"/>
      <div className="hero-composition">
        <div className="hero-field-label mono" aria-hidden="true">01 / INTERFERENCE STUDY <span>PATHS, RECONNECTED.</span></div>
        <Suspense fallback={<div className="sculpture-placeholder"/>}><Sculpture reduced={reduced} frozen={phase!=='hero'}/></Suspense>
        <div className="sculpture-caption mono" aria-hidden="true"><i/> DECORATIVE INTERFERENCE STUDY / WEBGL</div>
      </div>
      <section className="landing-copy"><p className="landing-eyebrow">QUANTUM FAILURE ANALYSIS / QISKIT</p><div className="hero-brand" aria-hidden="true">QFAULT</div><h2>Find the fault.<br/><span>Test the fix.</span></h2><p className="landing-description">Investigate quantum circuit failures, diagnose supported causes, test bounded repairs and verify the evidence.</p><div className="landing-actions"><button disabled={locked.current} className="enter-button" onClick={()=>enter()}>Enter Workbench <span aria-hidden="true">↗</span></button><button disabled={locked.current} className="research-button" onClick={e=>scrollTo(e,'research')}>Explore the Research <span aria-hidden="true">→</span></button></div><p className="simulation-label mono"><i/> QISKIT AER · SIMULATED EXECUTION</p></section>
      <div className="entry-access" aria-hidden={phase!=='reframe'}><Mark/><p className="landing-eyebrow">QFAULT / WORKSPACE ACCESS</p><h2>Your quantum<br/>laboratory is ready.</h2><p>Continue to the local demonstration environment.</p><span className="mono">EXECUTE. DIAGNOSE. RECOVER. VERIFY.</span></div>
      <div className="landing-foot mono"><span>QISKIT AER · SIMULATED QUANTUM EXECUTION</span><span>EVIDENCE BEFORE CONCLUSIONS <i>↘</i></span></div>
      </div>
      <div className="landing-details" inert={phase!=='hero'}>
        <section id="platform" className="platform-section"><p className="landing-eyebrow">THE INVESTIGATION LOOP</p><h2>How QFAULT works</h2><p className="section-intro">From a circuit that behaves unexpectedly to a conclusion you can inspect.</p><div className="workflow-steps">{[['Execute','Run Bell, GHZ and QFT circuits with Qiskit Aer.'],['Observe','Compare measured distributions with the circuit contract.'],['Diagnose','Test competing causes within a declared shot budget.'],['Verify','Evaluate a bounded repair with independent measurements.']].map(([name,copy],i)=><article key={name}><span className="mono">0{i+1} /</span><h3>{name}</h3><p>{copy}</p></article>)}</div></section>
        <section className="capabilities-section"><div><p className="landing-eyebrow">PRECISION OVER PROMISES</p><h2>A failure is a question.<br/><span>Evidence is the answer.</span></h2><p className="section-intro">A local quantum laboratory for investigating what changed, what remains ambiguous, and whether a proposed recovery holds up.</p></div><div className="capability-list">{[['Genuine circuit execution','Qiskit circuits and Aer simulation, with explicit fault, noise and backend settings.'],['Evidence-based diagnosis','Competing hypotheses, phase-sensitive measurements and visible abstention when evidence is insufficient.'],['Bounded recovery','Inspect the proposed edit, resource cost and before/after behavior. Repairs can be rejected or inconclusive.'],['Independent verification','Separate verification measurements, hashed artifacts and exportable reports.']].map(([title,copy])=><article key={title}><h3>{title}</h3><p>{copy}</p></article>)}</div></section>
        <section id="research" className="research-section"><p className="landing-eyebrow">SCIENTIFIC EVIDENCE</p><h2>Measured. Bounded. Reported.</h2><p className="section-intro">68-case controlled simulation evaluation. Frozen reported results, not live telemetry.</p><div className="research-metrics"><article><strong>66<span>/68</span></strong><h3>Phase-sensitive diagnosis</h3><p>487,424 total shots</p></article><article><strong>58<span>/68</span></strong><h3>Fixed-policy diagnosis</h3><p>348,160 total shots</p></article><article><strong>+40<span>%</span></strong><h3>Phase-sensitive shot cost</h3><p>Approximately, relative to fixed</p></article><article><strong>10<span>/12</span></strong><h3>Selected recoveries verified</h3><p>Two remained inconclusive</p></article></div><p className="research-limit">Higher classification accuracy came with higher resource cost in this finite evaluation. Two QFT2 angle-fault cases failed phase-sensitive diagnosis. These results do not establish universal superiority or quantum advantage.</p><button className="research-button" onClick={()=>enter('/benchmarks')}>Inspect the benchmarks <span aria-hidden="true">↗</span></button></section>
        <footer className="landing-final"><Mark/><p className="landing-eyebrow">EXECUTE. DIAGNOSE. RECOVER. VERIFY.</p><h2>Bring the evidence<br/>into focus.</h2><button className="enter-button" onClick={()=>enter()}>Open the Quantum Workbench <span aria-hidden="true">↗</span></button><span className="mono">QFAULT / QUANTUM FAILURE ANALYSIS & RECOVERY</span></footer>
      </div>
    </>}
    {phase==='swap'&&<div className="transition-overlay" aria-hidden="true"><PixelSwap firstContent={<div className="swap-dark"/>} secondContent={<div className="swap-light"><Mark/><span>QFAULT / WORKBENCH</span></div>} trigger="manual" active={swap} pattern="left-to-right" pixelSize={64} pixelSpin={0} pixelRadius={0} randomness={0} gap={0} duration={850} onComplete={finish} style={{height:'100dvh'}}/></div>}
  </div>
}
