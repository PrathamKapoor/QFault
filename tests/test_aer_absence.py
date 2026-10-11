import sys,pytest
from qfault.quantum import benchmark,Noise,execute

def test_missing_aer_never_disguised_as_success(monkeypatch):
    monkeypatch.setitem(sys.modules,'qiskit_aer',None)
    with pytest.raises(ImportError):execute(benchmark('bell',2),Noise(),128,1,backend='aer')
    r=execute(benchmark('bell',2),Noise(),128,1,backend='reference')
    assert r['backend_name']=='basic_simulator' and r['executed_shots']==128
