from qfault import quantum,diagnostics

def test_phase_analyst_ignores_poisoned_execution_metadata(monkeypatch):
    class Forbidden:
        def __getitem__(self,key):raise AssertionError('Evaluator truth was read')
        def get(self,*args):raise AssertionError('Evaluator truth was read')
    real=diagnostics.execute
    def poisoned(*args,**kwargs):
        r=real(*args,**kwargs);r['evaluation_truth']=Forbidden();r['injected_gate_position']=Forbidden();r['hidden_scenario']=Forbidden();return r
    monkeypatch.setattr(diagnostics,'execute',poisoned)
    good=quantum.benchmark('bell',2);bad=quantum.Circuit(n_qubits=2,gates=good.gates+(quantum.Gate(name='z',qubits=(0,)),))
    measured=diagnostics.EvidenceCollector.collect(quantum.execute(bad,quantum.Noise(),2048,71),2)
    access=diagnostics.DiagnosticAccess(bad,quantum.Noise(),diagnostics.ExecutionBudget(8192,6),71)
    result=diagnostics.DiagnosticAnalyst().analyze(bad,quantum.contract('bell',2),measured,access,'phase')
    assert result['category']=='LOGICAL_CIRCUIT_DEFECT'
    assert result['phase_probe']['comparison']['significant_disagreement']
