import React,{useEffect,useRef,useState} from 'react';
import {createQuantumSculpture} from './quantumSculpture';

export default function Sculpture({reduced,frozen}:{reduced:boolean;frozen:boolean}){
  const ref=useRef<HTMLCanvasElement>(null),engine=useRef<ReturnType<typeof createQuantumSculpture>>(null);
  const [fallback,setFallback]=useState(false);
  useEffect(()=>{try{engine.current=createQuantumSculpture(ref.current!,reduced,()=>setFallback(true));if(!engine.current)setFallback(true);else ref.current!.dataset.engine='webgl'}catch{setFallback(true)}return()=>{engine.current?.destroy();engine.current=null}},[reduced]);
  useEffect(()=>{if(frozen)engine.current?.pause()},[frozen]);
  return <div className="sculpture" aria-hidden="true"><canvas ref={ref} data-engine={fallback?'fallback':'webgl'} hidden={fallback}/>{fallback&&<div className="sculpture-fallback"><svg viewBox="0 0 500 500"><defs><linearGradient id="chrome"><stop stopColor="#15141c"/><stop offset=".35" stopColor="#aaa7bb"/><stop offset=".48" stopColor="#22202b"/><stop offset=".8" stopColor="#6e5b9a"/><stop offset="1" stopColor="#121218"/></linearGradient></defs>{[0,1,2].map(i=><path key={i} d="M250 65C55 20 70 335 270 400S445 130 250 65C110 170 400 360 350 160S90 230 250 435" transform={`rotate(${i*57} 250 250)`} fill="none" stroke="url(#chrome)" strokeWidth="13"/>)}</svg><span>Quantum interference study · static view</span></div>}</div>
}
