"""Controlled copied-report storage profile, never new scientific measurements."""
import argparse,base64,json,time,zlib
from pathlib import Path
from qfault.evidence import canonical
from qfault.hosting import empty_state,restore,snapshot
import tempfile

def profile(report,counts=(1,4,16,64)):
    raw=Path(report).read_text(encoding='utf8');rows=[]
    for count in counts:
        state={**empty_state(),'files':{f'profile_{i}.json':raw for i in range(count)}}
        start=time.perf_counter();data=canonical(state);serialization=time.perf_counter()-start
        start=time.perf_counter();encoded=zlib.compress(data,6);compression=time.perf_counter()-start
        start=time.perf_counter()
        with tempfile.TemporaryDirectory() as temp:
            restore(Path(temp),state['files']);assert snapshot(Path(temp))==state['files']
        restore_save=time.perf_counter()-start
        rows.append({'copied_reports':count,'snapshot_bytes':len(data),'compressed_base64_bytes':len(base64.b64encode(encoded)),
                     'serialization_seconds':serialization,'compression_seconds':compression,'restore_save_seconds':restore_save,
                     'read_storage_requests':2,'mutation_storage_requests':4,
                     'scope':'CPU/file/network-byte model for deliberately repeated report copies; no new shots or independent cases. Provider latency is not measured here.'})
    return rows

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as stream:json.dump(profile(args.report),stream,indent=2)
