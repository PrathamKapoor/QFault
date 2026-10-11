from math import pi
from qfault.quantum import Circuit,Gate
from qfault.recovery import edit_candidates

def test_rotation_at_input_bound_only_generates_admissible_edits():
    c=Circuit(n_qubits=2,gates=(Gate(name='rz',qubits=(0,),angle=8*pi),))
    edits=list(edit_candidates(c))
    assert edits and all(abs(g.angle)<=8*pi for candidate,_ in edits for g in candidate.gates if g.angle is not None)
    assert any(e['operator']=='angle' for _,e in edits)
