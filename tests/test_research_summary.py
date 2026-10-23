import json
import pytest
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


def test_recovery_comparison_keeps_both_denominators_and_uses_recorded_shot_totals(tmp_path):
    data=TestClient(create_app(tmp_path/'store')).get('/api/research').json()
    comparison=data['comparison']
    assert comparison['equal_verified_yield'] is True
    assert comparison['relative_shot_reduction']==pytest.approx(565248/5902336)
    for policy in ('conservative','point_discrepancy'):
        assert data['recovery'][policy]['runs']==90
        assert data['recovery'][policy]['eligible']==41
        assert data['recovery'][policy]['verified']==10
    assert round(comparison['relative_shot_reduction']*100,1)==9.6


def test_judging_guide_headlines_stay_consistent_with_recorded_summary():
    source=json.loads(Path('benchmarks/external-holdout-v1/summary.json').read_bytes())
    guide=Path('docs/judging-guide.md').read_text(encoding='utf8')
    for name in ('conservative','point_discrepancy'):
        row=source['recovery_summaries'][name];verified=row['outcomes']['VERIFIED_UNDER_DECLARED_CONTRACT']
        assert f"{verified}/{row['runs']}" in guide
        assert f"{verified}/{row['eligible']}" in guide
        assert f"{row['shots']:,}" in guide
