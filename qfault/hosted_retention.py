"""Prospective retention. Legacy snapshots without metadata are never expired."""
import time
RETENTION_SECONDS=90*86400

def tombstone(state,reason):
    return {'schema_version':1,'operations':state['operations'],'lease_until':0,'files':{},
            'deleted_at':time.time(),'deletion_reason':reason}

def expired(state,now=None):
    return (state.get('retention_policy')=='prospective-90d-v1' and
            state.get('retention_expires_at',float('inf'))<(time.time() if now is None else now))

def cleanup(storage,session_ids,apply=False,now=None):
    """Operator-driven bounded purge; default dry run; no legacy deletion."""
    import re
    if len(session_ids)>100 or any(not re.fullmatch('[0-9a-f]{64}',s) for s in session_ids):raise ValueError('At most100explicit session IDs required')
    counts={'examined':0,'eligible':0,'purged':0,'legacy_or_active':0}
    for sid in session_ids:
        state,etag=storage.read(sid);counts['examined']+=1
        if etag and expired(state,now) and state.get('lease_until',0)<(time.time() if now is None else now):
            counts['eligible']+=1
            if apply:storage.write(sid,tombstone(state,'retention'),etag);counts['purged']+=1
        else:counts['legacy_or_active']+=1
    return counts
