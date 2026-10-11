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
  function enter(route='/workbench'){if(locked.current)return;locked.current=true;destination.current=route;if(reduced)finish();else setPhase('reframe')}
  const hero=phase==='hero'||phase==='reframe'||phase==='swap';
  return <div className={'landing '+(phase==='reframe'||phase==='swap'?'landing--reframe':'')} data-phase={phase}>
    <h1 className="sr-only">QFAULT</h1>
    <header className="landing-nav"><a href="#/" className="landing-brand"><Mark/><span>QFAULT</span></a><nav aria-label="Primary"><a href="#/methodology">Methodology</a><a href="#/benchmarks">Research <span aria-hidden="true">↗</span></a><span className="local-tag">LOCAL SIMULATION</span></nav></header>
    {!hero&&<><div className="intro-status" role="status">{phase==='hyperspeed'?'Initializing quantum workspace':'Quantum failure analysis & recovery'}</div><button className="skip-intro" onClick={()=>{remember();setPhase('hero')}}>Skip intro <span>Esc</span></button></>}
    {phase==='hyperspeed'&&<Suspense fallback={<div className="intro-fallback"/>}><Hyperspeed className="intro-speed" curve="straight" curvature={.2} speed={1.4} density={45} trailLength={2.5} poles={0} dust={80} glow={.22} reflections={0} roadOpacity={0} lineColor="#000000" roadColor="#050507" background="#050507" tailColors={['#55408a','#77659c']} headColors={['#b9b6d2','#5362a2']} interactive={false}/></Suspense>}
    {phase==='techtext'&&<div className="tech-reveal" aria-hidden="true"><TechText text="QFAULT" color="#e3deed" accentColor="#7b5cff" fontWeight={750} fontSize={innerWidth*.152} letterSpacing={-.065} specks={8} selection={false} labels={false} draggable={false} speed={16} reveal="letter"/></div>}
    {hero&&<>
      {phase==='hero'&&!reduced&&innerWidth>=768&&(navigator.hardwareConcurrency||4)>4&&<Suspense fallback={null}><MoltenMetal className="metal-atmosphere" color1="#0d0b12" color2="#211538" color3="#5b3c95" speed={.12} opacity={.28} glow={.8} detail={3} brightness={.9} grain={false} mouseStrength={.04}/></Suspense>}
      <div className="landing-vignette" aria-hidden="true"/>
      <div className="hero-composition">
        <div className="hero-field-label mono" aria-hidden="true">01 / INTERFERENCE STUDY <span>LOGICAL PATHS · BOUNDED RECOVERY</span></div>
        <div className="word-plane word-back" aria-hidden="true">QFAULT</div>
        <Suspense fallback={<div className="sculpture-placeholder"/>}><Sculpture reduced={reduced} frozen={phase!=='hero'}/></Suspense>
        <div className="word-plane word-front" aria-hidden="true">QFAULT</div>
        <div className="sculpture-caption mono" aria-hidden="true"><i/> SIGNAL / DISCREPANCY / RECOVERY</div>
      </div>
      <section className="landing-copy"><p className="landing-eyebrow">QUANTUM FAILURE ANALYSIS / QISKIT</p><h2>Find the fault.<br/><span>Test the fix.</span></h2><p className="landing-description">Investigate quantum circuit failures, compare evidence, test bounded recovery, and verify what changed.</p><div className="landing-actions"><button disabled={locked.current} className="enter-button" onClick={()=>enter()}>Enter Workbench <span aria-hidden="true">↗</span></button><button disabled={locked.current} className="research-button" onClick={()=>enter('/benchmarks')}>Explore the Research <span aria-hidden="true">→</span></button></div></section>
      <div className="entry-access" aria-hidden={phase!=='reframe'}><Mark/><p className="landing-eyebrow">QFAULT / WORKSPACE ACCESS</p><h2>Your quantum<br/>laboratory is ready.</h2><p>Continue to the local demonstration environment.</p><span className="mono">EXECUTE. DIAGNOSE. RECOVER. VERIFY.</span></div>
      <div className="landing-foot mono"><span>QISKIT AER · SIMULATED QUANTUM EXECUTION</span><span>EVIDENCE BEFORE CONCLUSIONS <i>↘</i></span></div>
    </>}
    {phase==='swap'&&<div className="transition-overlay" aria-hidden="true"><PixelSwap firstContent={<div className="swap-dark"/>} secondContent={<div className="swap-light"><Mark/><span>QFAULT / WORKBENCH</span></div>} trigger="manual" active={swap} pattern="left-to-right" pixelSize={64} pixelSpin={0} pixelRadius={0} randomness={0} gap={0} duration={850} onComplete={finish} style={{height:'100dvh'}}/></div>}
  </div>
}
