"""Verify a downloaded session ZIP independently of the live application."""
import argparse,json
from pathlib import Path
from qfault.session_export import MAX_ARCHIVE,verify_session_export

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args()
    try:
        with args.archive.open('rb') as stream:raw=stream.read(MAX_ARCHIVE+1)
        result=verify_session_export(raw)
    except OSError:result={'valid':False,'errors':['Session export unavailable']}
    print(json.dumps(result,indent=2));return 0 if result['valid'] else 1

if __name__=='__main__':raise SystemExit(main())
