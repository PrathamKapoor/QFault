import pytest
from pydantic import ValidationError

from qfault.quantum import Gate, Noise
from qfault.lab import PauliObservable, DistributionContract
from qfault.interventions import EditRestrictions


@pytest.mark.parametrize('factory,value', [
    (Gate, {'name':'x','qubits':[True]}),
    (Gate, {'name':'x','qubits':['0']}),
    (Gate, {'name':'rz','qubits':[0],'angle':'0.2'}),
    (Gate, {'name':'rz','qubits':[0],'angle':True}),
    (Noise, {'readout':'0.1'}),
    (PauliObservable, {'pauli':'XX','expected':'1','tolerance':.1}),
    (PauliObservable, {'pauli':'XX','expected':1.,'tolerance':True}),
    (DistributionContract, {'kind':'measurement_distribution','expected_probabilities':{'00':'1'},'tolerance':.1}),
    (EditRestrictions, {'positions':['0']}),
    (EditRestrictions, {'angles':['0.2']}),
])
def test_scientific_input_rejects_coerced_strings_and_booleans(factory, value):
    with pytest.raises(ValidationError):
        factory.model_validate(value)
