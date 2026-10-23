import React,{Suspense,lazy,useEffect,useRef,useState} from 'react';
import Landing from './components/landing/Landing';
import HostedSession from './components/HostedSession';
const Workbench=lazy(()=>import('./main'));
const route=()=>location.hash.replace(/^#/,'')||'/';
export default function App(){
 const [page,setPage]=useState(route),[visited,setVisited]=useState(()=>route()!=='/');
 const workspaceRoute=useRef(page==='/'?'/workbench':page);
 if(page!=='/')workspaceRoute.current=page;
 useEffect(()=>{const change=()=>setPage(route());window.addEventListener('hashchange',change);return()=>window.removeEventListener('hashchange',change)},[]);
 useEffect(()=>{if(page!=='/')setVisited(true)},[page]);
 const navigate=(r:string)=>{location.hash=r};
 return <>{page==='/'&&<Suspense fallback={<div className="boot-status" role="status">QFAULT / Initializing workspace</div>}><Landing navigate={navigate}/></Suspense>}{(visited||page!=='/')&&<div hidden={page==='/'}><Suspense fallback={<div className="boot-status" role="status">QFAULT / Opening workbench</div>}><HostedSession><Workbench page={workspaceRoute.current} navigate={navigate}/></HostedSession></Suspense></div>}</>;
}
