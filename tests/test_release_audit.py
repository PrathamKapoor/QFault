"""Independent audit must detect incorrect science even in a rehashed valid bundle."""
import copy
import pytest
from tests.test_counterfactual import request


@pytest.mark.parametrize('kind', ['target_state', 'pauli_expectations', 'measurement_distribution'])
def test_reconstruct_real_aer_recovery_without_running_engine(kind, monkeypatch):
    import qfault.counterfactual as engine
    record = engine.recover(request(kind))
    from scripts.audit_counterfactual import audit_record
    def forbidden(*args, **kwargs):
        raise AssertionError('audit reused recovery decision implementation')
    monkeypatch.setattr(engine, 'recover', forbidden)
    monkeypatch.setattr(engine, 'verification_verdict', forbidden)
    result = audit_record(record)
    assert result['status'] == 'VERIFIED_UNDER_DECLARED_CONTRACT'
    assert result['shots'] == record['cost']['shots']
    assert result['contract_type'] == kind
    v = record['verification']
    assert result['improvement_interval'] == pytest.approx([
        v['original']['loss_interval'][0] - v['candidate']['loss_interval'][1],
        v['original']['loss_interval'][1] - v['candidate']['loss_interval'][0]])


def test_rehashed_but_incorrect_improvement_is_rejected(tmp_path):
    from qfault.counterfactual import recover
    from qfault.storage import ArtifactStore, verify_export
    from scripts.audit_counterfactual import audit_record
    record = copy.deepcopy(recover(request('target_state')))
    record['verification']['improvement_lower'] = .123
    store = ArtifactStore(tmp_path)
    eid = store.save(record)
    assert verify_export(store.export(eid))['valid']  # hash consistency is not scientific validity
    with pytest.raises(ValueError, match='improvement'):
        audit_record(record)


def test_fresh_samples_cannot_reuse_screening_execution():
    from qfault.counterfactual import recover
    from scripts.audit_counterfactual import audit_record
    record = copy.deepcopy(recover(request()))
    record['verification']['candidate']['events'][0]['execution_id'] = record['selected_candidate']['evidence']['events'][0]['execution_id']
    with pytest.raises(ValueError):
        audit_record(record)
