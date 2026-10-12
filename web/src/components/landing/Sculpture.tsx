import React,{useEffect,useRef,useState} from 'react';
import {createQuantumSculpture} from './quantumSculpture';

export default function Sculpture({reduced,frozen}:{reduced:boolean;frozen:boolean}){
  const ref=useRef<HTMLCanvasElement>(null),engine=useRef<ReturnType<typeof createQuantumSculpture>>(null);
  const [fallback,setFallback]=useState(false);
  useEffect(()=>{try{engine.current=createQuantumSculpture(ref.current!,reduced,()=>setFallback(true));if(!engine.current)setFallback(true);else ref.current!.dataset.engine='webgl'}catch{setFallback(true)}return()=>{engine.current?.destroy();engine.current=null}},[reduced]);
  useEffect(()=>{if(frozen)engine.current?.pause()},[frozen]);
  return <div className="sculpture" aria-hidden="true"><canvas ref={ref} data-engine={fallback?'fallback':'webgl'} hidden={fallback}/>{fallback&&<div className="sculpture-fallback"><svg viewBox="0 0 500 500"><defs><linearGradient id="chrome"><stop stopColor="#15141c"/><stop offset=".35" stopColor="#aaa7bb"/><stop offset=".48" stopColor="#22202b"/><stop offset=".8" stopColor="#6e5b9a"/><stop offset="1" stopColor="#121218"/></linearGradient></defs>{['M245 55C90 75 80 220 230 270S410 390 265 450','M260 65C430 140 400 245 230 280S90 410 245 445','M245 55C30 120 60 380 265 450','M265 65C460 180 210 250 205 435','M220 70C70 250 460 225 310 430'].map((d,i)=><path key={d} d={d} fill="none" stroke="url(#chrome)" strokeWidth={i<2?12:4}/>) }</svg><span>Quantum interference study · static view</span></div>}</div>
}
