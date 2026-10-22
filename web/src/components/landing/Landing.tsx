import React,{useEffect,useRef,useState} from 'react';
import Mark from '../branding/Mark';
import PixelSwap from '../effects/PixelSwap';
import MentalHero from '../hero/MentalHero';
import ResearchEvidence from '../ResearchEvidence';
import './landing.css';

export function useReducedMotion(){const [value,setValue]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);useEffect(()=>{const m=matchMedia('(prefers-reduced-motion: reduce)'),change=()=>setValue(m.matches);m.addEventListener('change',change);return()=>m.removeEventListener('change',change)},[]);return value}
function seen(){try{return sessionStorage.getItem('qfault-intro')==='1'}catch{return false}}
function remember(){try{sessionStorage.setItem('qfault-intro','1')}catch{/* private browsing */}}

export default function Landing({navigate}:{navigate:(route:string)=>void}){
  const reduced=useReducedMotion();
  const [instant]=useState(()=>seen()),[phase,setPhase]=useState('hero'),[swap,setSwap]=useState(false);
  const locked=useRef(false),destination=useRef('/workbench');
  const finish=()=>{remember();navigate(destination.current)};
  useEffect(()=>{
    if(phase==='hero')remember();
    const timer=phase==='reframe'?window.setTimeout(()=>setPhase('swap'),470):phase==='swap'?window.setTimeout(finish,1150):0;
    return()=>clearTimeout(timer);
  },[phase,reduced]);
  useEffect(()=>{if(phase==='swap'){const timer=window.setTimeout(()=>setSwap(true),40);return()=>clearTimeout(timer)}},[phase]);
  useEffect(()=>{const escape=(e:KeyboardEvent)=>{if(e.key==='Escape'&&locked.current)finish()};window.addEventListener('keydown',escape);return()=>window.removeEventListener('keydown',escape)},[]);
  function enter(route='/workbench'){if(locked.current)return;locked.current=true;destination.current=route;window.scrollTo(0,0);if(reduced)finish();else setPhase('reframe')}
  function scrollTo(e:React.MouseEvent,id:string){e.preventDefault();document.getElementById(id)?.scrollIntoView({behavior:reduced?'instant':'smooth'});}
  const hero=phase==='hero'||phase==='reframe'||phase==='swap';
  return <div className={'landing '+(phase==='reframe'||phase==='swap'?'landing--reframe':'')} data-phase={phase}>
    <h1 className="sr-only">QFAULT</h1>
    <header className="landing-nav"><a href="#/" className="landing-brand"><Mark/><span>QFAULT</span></a><nav aria-label="Primary"><a href="#/" onClick={e=>scrollTo(e,'platform')}>Platform</a><a href="#/" onClick={e=>scrollTo(e,'research')}>Research</a><button onClick={()=>enter('/benchmarks')}>Benchmarks</button><a href="https://github.com/PrathamKapoor/QFault" target="_blank" rel="noreferrer">GitHub ↗</a><button className="nav-enter" aria-label="Enter Workbench from navigation" onClick={()=>enter()}>Enter Workbench <span aria-hidden="true">↗</span></button></nav></header>
    {hero&&<>
      <MentalHero instant={instant} handover={phase!=='hero'} onEnter={()=>enter()} onResearch={e=>scrollTo(e,'research')}/>
      <div className="landing-details" inert={phase!=='hero'}>
        <section id="platform" className="platform-section"><p className="landing-eyebrow">THE INVESTIGATION LOOP</p><h2>How QFAULT works</h2><p className="section-intro">From a circuit that behaves unexpectedly to a conclusion you can inspect.</p><div className="workflow-steps">{[['Execute','Run Bell, GHZ and QFT circuits with Qiskit Aer.'],['Observe','Compare measured distributions with the circuit contract.'],['Diagnose','Test competing causes within a declared shot budget.'],['Verify','Evaluate a bounded repair with independent measurements.']].map(([name,copy],i)=><article key={name}><span className="mono">0{i+1} /</span><h3>{name}</h3><p>{copy}</p></article>)}</div></section>
        <section className="capabilities-section"><div><p className="landing-eyebrow">PRECISION OVER PROMISES</p><h2>A failure is a question.<br/><span>Evidence is the answer.</span></h2><p className="section-intro">A local quantum laboratory for investigating what changed, what remains ambiguous, and whether a proposed recovery holds up.</p></div><div className="capability-list">{[['Genuine circuit execution','Qiskit circuits and Aer simulation, with explicit fault, noise and backend settings.'],['Evidence-based diagnosis','Competing hypotheses, phase-sensitive measurements and visible abstention when evidence is insufficient.'],['Bounded recovery','Inspect the proposed edit, resource cost and before/after behavior. Repairs can be rejected or inconclusive.'],['Independent verification','Separate verification measurements, hashed artifacts and exportable reports.']].map(([title,copy])=><article key={title}><h3>{title}</h3><p>{copy}</p></article>)}</div></section>
        <section id="research" className="research-section"><p className="landing-eyebrow">SCIENTIFIC EVIDENCE</p><h2>Measured. Bounded. Reported.</h2><ResearchEvidence/><button className="research-button" onClick={()=>enter('/lab')}>Investigate your circuit <span aria-hidden="true">↗</span></button><button className="research-button" onClick={()=>enter('/benchmarks')}>Inspect historical benchmarks <span aria-hidden="true">↗</span></button></section>
        <footer className="landing-final"><Mark/><p className="landing-eyebrow">EXECUTE. DIAGNOSE. RECOVER. VERIFY.</p><h2>Bring the evidence<br/>into focus.</h2><button className="enter-button" onClick={()=>enter()}>Open the Quantum Workbench <span aria-hidden="true">↗</span></button><span className="mono">QFAULT / QUANTUM FAILURE ANALYSIS & RECOVERY</span></footer>
      </div>
    </>}
    {phase==='swap'&&<div className="transition-overlay" aria-hidden="true"><PixelSwap firstContent={<div className="swap-dark"/>} secondContent={<div className="swap-light"><Mark/><span>QFAULT / WORKBENCH</span></div>} trigger="manual" active={swap} pattern="left-to-right" pixelSize={64} pixelSpin={0} pixelRadius={0} randomness={0} gap={0} duration={850} onComplete={finish} style={{height:'100dvh'}}/></div>}
  </div>
}
