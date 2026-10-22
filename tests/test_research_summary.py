import json
from pathlib import Path
from fastapi.testclient import TestClient
from qfault.api import create_app


def test_current_research_headlines_derive_from_frozen_rows(tmp_path):
    response = TestClient(create_app(tmp_path / 'store')).get('/api/research')
    assert response.status_code == 200, 'current measured evidence needs a single reporting source'
    data = response.json()
    source = json.loads(Path('benchmarks/external-holdout-v1/summary.json').read_bytes())
    for policy in ('conservative','point_discrepancy'):
        rows = [r for r in source['recovery_rows'] if r['policy'] == policy]
        assert data['recovery'][policy]['runs'] == len(rows)
        assert data['recovery'][policy]['verified'] == sum(r['status']=='VERIFIED_UNDER_DECLARED_CONTRACT' for r in rows)
        assert data['recovery'][policy]['rejected'] == sum(r['status']=='REJECTED' for r in rows)
        assert data['recovery'][policy]['shots'] == sum(r['cost']['shots'] for r in rows)
    assert data['evidence']['available'] is True
