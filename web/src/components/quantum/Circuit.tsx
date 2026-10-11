import React from 'react';
type Gate={name:string;qubits:number[];angle?:number|null};
export default function Circuit({circuit}:{circuit:{n_qubits:number;gates:Gate[]}}){
 const n=circuit.n_qubits,gates=circuit.gates,width=Math.max(500,190+gates.length*65),height=55+n*58;
 return <div className="circuit-scroll"><svg viewBox={`0 0 ${width} ${height}`} style={{minWidth:Math.min(width,900)}} role="img" aria-label={`Submitted ${n}-qubit circuit with ${gates.length} gates; operations ordered left to right`}>
 {Array.from({length:n},(_,q)=><g key={q}><text x="13" y={47+q*58} className="axis">q_{q}:</text><line x1="64" x2={width-20} y1={42+q*58} y2={42+q*58} stroke="#ccc5dd"/><rect x={width-67} y={25+q*58} width="34" height="34" rx="5" fill="#faf8fd" stroke="#d3c7e1"/><path d={`M${width-61} ${46+q*58}a11 11 0 0 1 22 0m-11 0 7-11`} stroke="#8e7ba2" fill="none"/><title>Computational Z readout for q{q}; basis changes are shown separately in phase evidence</title></g>)}
 {gates.map((g,i)=>{const x=95+i*65,ys=g.qubits.map(q=>42+q*58);return <g key={i}><title>{`${i}: ${g.name} on ${g.qubits.join(', ')}${g.angle!=null?' / '+g.angle.toFixed(4)+' rad':''}`}</title>{ys.length>1&&<line x1={x} x2={x} y1={Math.min(...ys)} y2={Math.max(...ys)} stroke="#8051c9" strokeWidth="2"/>}{ys.map((y,j)=>g.name==='cx'&&j===0?<circle key={j} cx={x} cy={y} r="5" fill="#7c3aed"/>:<g key={j}><rect x={x-20} y={y-17} width="40" height="34" rx="5" fill="#f5f0ff" stroke="#c4afe5"/><text x={x} y={y+5} textAnchor="middle" fill="#6035a0" fontSize="12" fontFamily="Consolas,monospace">{g.name==='cx'?'⊕':g.name.toUpperCase()}</text>{g.angle!=null&&j===0&&<text x={x} y={y+29} textAnchor="middle" className="axis">{g.angle.toFixed(2)}</text>}</g>)}</g>})}
 </svg></div>
}
