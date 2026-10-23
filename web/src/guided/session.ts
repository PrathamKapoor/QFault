/** Presentation state contains returned identities, never invented engine results. */
export type RunKey='z'|'phase'|'recovery'|'noise'|'budget';
export type Stage='source'|'z'|'phase'|'edits'|'verify'|'export';
export type Mode='phase'|'noise'|'budget';
export type Pending={key:RunKey|'replay';phase:'validating'|'executing'|'unknown';startedAt:number;operationId?:string};
export type Guide={schema_version:1;sessionId:string;stage:Stage;mode:Mode;ids:Partial<Record<RunKey,string>>;replays:string[];pending:Pending|null};
export type Store={getItem:(key:string)=>string|null;setItem:(key:string,value:string)=>void};
const KEY='qfault-guided-demo-v1';
const STAGES:Stage[]=['source','z','phase','edits','verify','export'];
const RUNS:RunKey[]=['z','phase','recovery','noise','budget'];
const validId=(id:unknown):id is string=>typeof id==='string'&&/^experiment_[a-f0-9]{32}$/.test(id);

export function createGuide():Guide{
 return {schema_version:1,sessionId:crypto.randomUUID(),stage:'source',mode:'phase',ids:{},replays:[],pending:null};
}

export function readGuide(storage:Store):{session:Guide;warning:string}{
 try{
  const raw=storage.getItem(KEY);if(!raw)return {session:createGuide(),warning:''};
  if(raw.length>16384)throw Error('size');
  const s=JSON.parse(raw);
  if(!s||s.schema_version!==1||typeof s.sessionId!=='string'||!STAGES.includes(s.stage)||!['phase','noise','budget'].includes(s.mode)||
     !s.ids||typeof s.ids!=='object'||Array.isArray(s.ids)||!Array.isArray(s.replays)||s.replays.length>32||
     Object.entries(s.ids).some(([k,v])=>!RUNS.includes(k as RunKey)||!validId(v))||s.replays.some((v:unknown)=>!validId(v)))throw Error('shape');
  if(s.pending&&(![...RUNS,'replay'].includes(s.pending.key)||!Number.isFinite(s.pending.startedAt)))throw Error('pending');
  if(s.pending){s.pending.phase='unknown';return {session:s,warning:'An earlier request completion is unknown. Nothing is retried automatically. Inspect history before starting another guide.'}};
  return {session:s,warning:''};
 }catch{return {session:createGuide(),warning:'Saved guide state is unavailable or malformed. Server investigations remain preserved; no execution was started.'}};
}

export function writeGuide(storage:Store,session:Guide){storage.setItem(KEY,JSON.stringify(session))}

export function restartGuide(storage:Store,previous:Guide):Guide{
 let history:unknown[]=[];
 try{const raw=storage.getItem(KEY+'-history');if(raw&&raw.length<65536){const parsed=JSON.parse(raw);if(Array.isArray(parsed))history=parsed.slice(-19)}}catch{/* current server records remain authoritative */}
 storage.setItem(KEY+'-history',JSON.stringify([...history,{sessionId:previous.sessionId,ids:previous.ids,replays:previous.replays}]));
 const fresh=createGuide();writeGuide(storage,fresh);return fresh;
}

export function canVisit(stage:Stage,records:Record<string,any>,inspected:boolean):boolean{
 if(stage==='source'||stage==='z')return true;
 if(stage==='phase')return Boolean(records.z);
 if(stage==='edits')return records.phase?.diagnosis?.category==='SIGNIFICANT_DISCREPANCY';
 if(stage==='verify')return inspected&&records.phase?.diagnosis?.category==='SIGNIFICANT_DISCREPANCY';
 return Boolean(records.recovery);
}

export class ExecutionGate{
 private locked=false;
 async run<T>(work:()=>Promise<T>):Promise<T|false>{
  if(this.locked)return false;
  this.locked=true;
  try{return await work()}finally{this.locked=false}
 }
}
