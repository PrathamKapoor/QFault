import React,{useEffect,useRef,useState} from 'react';
import {createQuantumSculpture} from './quantumSculpture';

export default function Sculpture({reduced,frozen}:{reduced:boolean;frozen:boolean}){
  const ref=useRef<HTMLCanvasElement>(null),engine=useRef<ReturnType<typeof createQuantumSculpture>>(null);
  const [fallback,setFallback]=useState(false);
  useEffect(()=>{try{engine.current=createQuantumSculpture(ref.current!,reduced,()=>setFallback(true));if(!engine.current)setFallback(true);else ref.current!.dataset.engine='webgl'}catch{setFallback(true)}return()=>{engine.current?.destroy();engine.current=null}},[reduced]);
  useEffect(()=>{if(frozen)engine.current?.pause()},[frozen]);
  return <div className="sculpture" aria-hidden="true"><canvas ref={ref} data-engine={fallback?'fallback':'webgl'} hidden={fallback}/>{fallback&&<div className="sculpture-fallback"><svg viewBox="0 0 500 500"><defs><linearGradient id="chrome"><stop stopColor="#15141c"/><stop offset=".35" stopColor="#aaa7bb"/><stop offset=".48" stopColor="#22202b"/><stop offset=".8" stopColor="#6e5b9a"/><stop offset="1" stopColor="#121218"/></linearGradient></defs>{['M25 350C120 385 140 110 240 180S350 250 475 80','M30 390C160 220 205 410 270 200S350 55 460 70','M25 320C180 100 220 295 360 170S435 100 475 85','M70 380C110 210 230 400 310 170S420 130 465 70'].map((d,i)=><path key={d} d={d} fill="none" stroke="url(#chrome)" strokeWidth={i<2?16:6}/>) }</svg><span>Quantum interference study · static view</span></div>}</div>
}
