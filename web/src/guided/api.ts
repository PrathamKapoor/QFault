export class ApiError extends Error{
 status:number;
 constructor(status:number,message:string){super(message);this.status=status}
}

export async function demoRequest(path:string,body?:Record<string,any>){
 let response:Response;
 try{response=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:undefined)}
 catch{throw new ApiError(0,'Connection lost. A submitted operation may still be running; no cancellation or success is assumed.')}
 let value:any;
 try{value=await response.json()}catch{throw new ApiError(0,'The server response could not be read. Inspect history before retrying an execution.')}
 if(!response.ok){
  const detail=typeof value.detail==='string'?value.detail:'Request validation failed. Inspect the setup or backend availability.';
  throw new ApiError(response.status,response.status===409?'Server busy. Another investigation is running; retry when it finishes.':detail);
 }
 return value;
}
