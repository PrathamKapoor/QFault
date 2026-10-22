import json
from scripts.verify_recovery_archive import verify


def test_missing_and_unsupported_recovery_evidence_fail_closed(tmp_path):
    assert not verify(tmp_path)['valid']
    (tmp_path/'manifest.json').write_text(json.dumps({'schema_version':999}))
    result=verify(tmp_path)
    assert not result['valid']
    assert 'unsupported' in result['errors'][0]
