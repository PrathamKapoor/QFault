import json
from pathlib import Path
import shutil
from scripts.verify_replication import verify


def test_replication_raw_records_verify_and_cost_edit_is_rejected(tmp_path):
    source=Path('benchmarks/current-release-replication-v4')
    assert verify(source)['valid']
    shutil.copyfile(source/'summary.json',tmp_path/'summary.json')
    shutil.copyfile(source/'reports.jsonl.gz',tmp_path/'reports.jsonl.gz')
    summary=json.loads((tmp_path/'summary.json').read_bytes())
    summary['rows'][0]['shots']+=1
    (tmp_path/'summary.json').write_text(json.dumps(summary))
    assert not verify(tmp_path)['valid']


def test_replication_source_fingerprints_are_bound_to_frozen_protocol(tmp_path):
    source=Path('benchmarks/current-release-replication-v4')
    shutil.copyfile(source/'summary.json',tmp_path/'summary.json')
    shutil.copyfile(source/'reports.jsonl.gz',tmp_path/'reports.jsonl.gz')
    summary=json.loads((tmp_path/'summary.json').read_bytes())
    summary['source_sha256_normalized_lf']['qfault/api.py']='0'*64
    (tmp_path/'summary.json').write_text(json.dumps(summary))
    assert not verify(tmp_path)['valid']
