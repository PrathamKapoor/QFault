"""Lossless bounded wire envelope; embedded canonical scientific strings unchanged."""
import base64,hashlib,json,zlib
from .evidence import canonical
LIMIT=32*1024*1024

def encode_state(state):
    raw=canonical(state)
    if len(raw)>LIMIT:raise ValueError('Expanded snapshot exceeds limit')
    return canonical({'schema_version':2,'encoding':'zlib-base64','expanded_bytes':len(raw),
                      'sha256':hashlib.sha256(raw).hexdigest(),'payload':base64.b64encode(zlib.compress(raw,6)).decode()})

def decode_state(raw):
    if len(raw)>LIMIT:raise ValueError('Wire snapshot exceeds limit')
    state=json.loads(raw)
    if not isinstance(state,dict) or type(state.get('schema_version')) is not int:raise ValueError('Unsupported snapshot')
    if state['schema_version']==1:return state
    if state['schema_version']!=2 or state.get('encoding')!='zlib-base64' or type(state.get('expanded_bytes')) is not int or not 0<=state['expanded_bytes']<=LIMIT:raise ValueError('Unsupported compressed snapshot')
    try:
        decoder=zlib.decompressobj();body=decoder.decompress(base64.b64decode(state['payload'],validate=True),LIMIT+1)
        if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data or len(body)!=state['expanded_bytes'] or hashlib.sha256(body).hexdigest()!=state['sha256']:raise ValueError('Compressed snapshot identity/size mismatch')
        value=json.loads(body)
        if not isinstance(value,dict) or type(value.get('schema_version')) is not int or value['schema_version']!=1:raise ValueError('Unsupported embedded snapshot')
        return value
    except (zlib.error,KeyError,TypeError) as exc:raise ValueError('Corrupt compressed snapshot') from exc
