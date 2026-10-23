export const HISTORY_EVENT='qfault:history-changed';
export const completedIdentity=(value:any)=>/^experiment_[a-f0-9]{32}$/.test(value?.experiment_id??'')||/^challenge_[a-f0-9]{32}$/.test(value?.challenge_id??'');
export function notifyCompleted(value:any){if(completedIdentity(value)&&typeof window!=='undefined')window.dispatchEvent(new Event(HISTORY_EVENT));}
export function historyLoader(read:()=>Promise<any>,commit:(rows:any)=>void){let generation=0;return async()=>{const mine=++generation;const rows=await read();if(mine===generation)commit(rows)};}
