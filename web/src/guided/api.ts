import {notifyCompleted} from './history';
import {ApiError,jsonRequest} from './requests';
export {ApiError} from './requests';
export function newOperationId(){return 'operation_'+crypto.randomUUID().replaceAll('-','')}
export async function recoverOperation(id:string){
 const operation=await jsonRequest('/api/operations/'+id);
 if(operation.state==='COMPLETED'&&operation.result_path){const result=await jsonRequest(operation.result_path);notifyCompleted(result);return {operation,result}}
 return {operation,result:null};
}
export async function demoRequest(path:string,body?:Record<string,any>,options:{signal?:AbortSignal;operationId?:string;kind?:'bootstrap'|'read'|'validation'|'execution'}={}){
 const kind=options.kind??(body?(path.endsWith('/validate')?'validation':path==='/api/hosted-session'?'bootstrap':'execution'):'read');
 const operationId=body&&kind==='execution'&&import.meta.env.VITE_QFAULT_HOSTED==='1'?(options.operationId??newOperationId()):undefined;
 if(operationId){try{sessionStorage.setItem('qfault-last-operation',JSON.stringify({id:operationId,path,startedAt:Date.now()}))}catch{/* status stays recoverable by ID */}}
 const value=await jsonRequest(path,body,{...options,kind,operationId});
 if(operationId&&['RUNNING','ADMITTED','UNKNOWN'].includes(value.state))throw new ApiError(0,'The existing operation is '+value.state.toLowerCase()+'. Recover its status; no new computation was submitted.');
 if(body)notifyCompleted(value);
 return value;
}
