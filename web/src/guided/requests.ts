export type RequestClass='bootstrap'|'read'|'validation'|'execution';
export class ApiError extends Error{status:number;constructor(status:number,message:string){super(message);this.status=status}}
type Options={kind?:RequestClass;timeout?:number;backoff?:number;fetcher?:typeof fetch;signal?:AbortSignal;operationId?:string;onAttempt?:(attempt:number)=>void};
export async function jsonRequest(path:string,body?:Record<string,any>,options:Options={}){
 const kind=options.kind??(body?'execution':'read'),safe=kind==='read'||kind==='bootstrap';
 const timeout=options.timeout??({bootstrap:20000,read:20000,validation:30000,execution:280000}[kind]);
 for(let attempt=0;attempt<(safe?3:1);attempt++){
  const controller=new AbortController(),abort=()=>controller.abort();
  options.signal?.addEventListener('abort',abort,{once:true});if(options.signal?.aborted)abort();
  const timer=setTimeout(abort,timeout);options.onAttempt?.(attempt+1);
  try{
   const response=await (options.fetcher??fetch)(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json',...(options.operationId?{'X-QFault-Operation':options.operationId}:{})}:undefined,body:body?JSON.stringify(body):undefined,signal:controller.signal});
   let value:any;try{value=await response.json()}catch{throw new ApiError(kind==='execution'?0:422,kind==='execution'?'The response could not be decoded. The operation may still be running; recover its identity.':'Unsupported or malformed response. Retry is not automatic; inspect service compatibility.')}
   if(!response.ok){const detail=typeof value.detail==='string'?value.detail:'Request validation or schema failed.';throw new ApiError(response.status,response.status===409&&/already running|another operation|busy/i.test(detail)?'Server busy. '+detail:detail)}
   return value;
  }catch(exc){
   const error=exc instanceof ApiError?exc:new ApiError(0,kind==='execution'?'Connection lost or waiting deadline reached. The operation may still be running; recover its identity without resubmitting.':'Connection or loading deadline failed. No investigation has started.');
   if(!safe||options.signal?.aborted||![0,408,425,429,502,503,504].includes(error.status)||attempt===2)throw error;
  }finally{clearTimeout(timer);options.signal?.removeEventListener('abort',abort)}
  await new Promise<void>((resolve,reject)=>{const done=()=>{options.signal?.removeEventListener('abort',cancel);resolve()},timer=setTimeout(done,(options.backoff??500)*2**attempt);const cancel=()=>{clearTimeout(timer);options.signal?.removeEventListener('abort',cancel);reject(new ApiError(0,'Loading stopped on navigation.'))};options.signal?.addEventListener('abort',cancel,{once:true})});
 }
 throw new ApiError(0,'Loading attempts exhausted.');
}
