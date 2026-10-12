import React,{useEffect,useRef,useState} from 'react';
import {createQuantumSculpture} from './quantumSculpture';

export default function Sculpture({reduced,frozen}:{reduced:boolean;frozen:boolean}){
  const ref=useRef<HTMLCanvasElement>(null),engine=useRef<ReturnType<typeof createQuantumSculpture>>(null);
  const [fallback,setFallback]=useState(false);
  useEffect(()=>{try{engine.current=createQuantumSculpture(ref.current!,reduced,()=>setFallback(true));if(!engine.current)setFallback(true);else ref.current!.dataset.engine='webgl'}catch{setFallback(true)}return()=>{engine.current?.destroy();engine.current=null}},[reduced]);
  useEffect(()=>{if(frozen)engine.current?.pause()},[frozen]);
  return <div className="sculpture" aria-hidden="true"><canvas ref={ref} data-engine={fallback?'fallback':'webgl'} hidden={fallback}/>{fallback&&<div className="sculpture-fallback"><svg viewBox="0 0 500 600"><defs><linearGradient id="chrome"><stop stopColor="#15141c"/><stop offset=".35" stopColor="#aaa7bb"/><stop offset=".48" stopColor="#22202b"/><stop offset=".8" stopColor="#6e5b9a"/><stop offset="1" stopColor="#121218"/></linearGradient></defs><g transform="rotate(16 250 300)">{['M210 25C430 90 70 180 250 240S430 390 250 450S120 530 290 575','M290 25C70 90 430 180 250 240S70 390 250 450S380 530 210 575','M190 25C410 90 50 180 230 240S410 390 230 450S100 530 270 575','M310 25C90 90 450 180 270 240S90 390 270 450S400 530 230 575'].map((d,i)=><path key={d} d={d} fill="none" stroke="url(#chrome)" strokeWidth={i<2?20:4}/>)}</g></svg></div>}</div>
}
