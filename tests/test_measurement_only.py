"""The measurement analyst must be unable to inspect the faulty state."""
import pytest
from qfault.workflow import RunRequest, investigate
from qfault import quantum, diagnostics, recovery


def forbidden(*args, **kwargs):
    raise AssertionError('Privileged candidate-state access in measurement-only mode')


@pytest.mark.parametrize('scenario,plan,expected',[
    ('clean','complementary','NO_SIGNIFICANT_FAILURE_DETECTED'),
    ('phase','z_only','NO_SIGNIFICANT_FAILURE_DETECTED'),
    ('phase','complementary','MIXED_OR_AMBIGUOUS'),
    ('remove','complementary','MIXED_OR_AMBIGUOUS'),
    ('readout','complementary','NOISE_CONSISTENT_DEGRADATION'),
    ('gate','complementary','MIXED_OR_AMBIGUOUS'),
])
def test_no_privileged_access(monkeypatch,scenario,plan,expected):
    for module in (quantum,diagnostics,recovery):
        monkeypatch.setattr(module,'ideal_state',forbidden)
    monkeypatch.setattr(diagnostics.DiagnosticAccess,'state_probe',forbidden)
    monkeypatch.setattr(recovery.RecoveryPlanner,'propose',forbidden)
    monkeypatch.setattr(quantum.Statevector,'from_instruction',forbidden)
    monkeypatch.setattr(quantum.DensityMatrix,'evolve',forbidden)
    monkeypatch.setattr(quantum,'noisy_density',forbidden)
    result=investigate(RunRequest(scenario=scenario,seed=883,backend='aer',recover=False,
        diagnostic_mode='measurement_only',measurement_plan=plan))
    assert result['diagnosis']['category']==expected
    assert result['diagnosis']['state_probe'] is None
    assert result['cost']['exact_state_evaluations']==0
    assert result['recovery'] is None
    assert result['diagnosis']['capability_mode']=='measurement_only'
    assert result['cost']['shots']==sum(r['executed_shots'] for r in result['executions'])
    if scenario=='phase' and plan=='complementary':
        assert not result['diagnosis']['discrepancy']['significant_disagreement']
        assert result['diagnosis']['phase_probe']['comparison']['significant_disagreement']


@pytest.mark.parametrize('shots,ceiling',[(64,128),(2048,4096)])
def test_unfunded_measurements_abstain(shots,ceiling):
    r=investigate(RunRequest(scenario='phase',shots=shots,max_shots=ceiling,recover=False,
        diagnostic_mode='measurement_only'))
    assert r['diagnosis']['category']=='INSUFFICIENT_EVIDENCE'
    assert r['cost']['shots']<=ceiling


def test_measurement_recovery_not_silently_simulator_assisted():
    with pytest.raises(ValueError,match='measurement-only recovery'):
        RunRequest(diagnostic_mode='measurement_only',recover=True)


def test_unsupported_contract_has_no_oracle():
    from qfault.measurement import MeasurementOnlyAnalyst
    class Unsupported:
        family='custom'
    assert MeasurementOnlyAnalyst().analyze(Unsupported(),None,None)['category']=='UNSUPPORTED'


def test_cli_measurement_mode_is_explicit(tmp_path,capsys):
    import json
    from qfault.cli import main
    code=main(['--store',str(tmp_path),'run','--scenario','phase','--backend','aer',
               '--diagnostic-mode','measurement_only','--measurement-plan','complementary','--no-recovery'])
    assert code==0
    result=json.loads(capsys.readouterr().out)
    assert result['diagnosis']['category']=='MIXED_OR_AMBIGUOUS'
    assert result['cost']['exact_state_evaluations']==0
