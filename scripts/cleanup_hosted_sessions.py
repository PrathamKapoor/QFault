"""Explicit operator retention sweep. No scheduled automatic purge is claimed."""
import argparse,json
from pathlib import Path
from qfault.hosted_retention import cleanup
from qfault.hosting import BlobState

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session-list',required=True,help='Private JSON array of at most100session IDs')
    parser.add_argument('--apply',action='store_true',help='Purge only expired prospective snapshots; default dry run')
    args=parser.parse_args();raw=Path(args.session_list).read_bytes()
    if len(raw)>8192:raise ValueError('Session list exceeds bound')
    values=json.loads(raw)
    if not isinstance(values,list):raise ValueError('Session list must be an array')
    print(json.dumps(cleanup(BlobState(),values,apply=args.apply)))

if __name__=='__main__':main()
