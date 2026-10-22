import pytest
from scripts import dense_target_study


def test_target_only_allocation_matches_budget_caps_and_known_optimum():
    allocate=getattr(dense_target_study,'allocate',None)
    assert callable(allocate), 'target-only bounded allocation is required for the development study'
    shots=allocate([8.,1.],1000)
    assert sum(shots)==1000 and all(64<=n<=10000 for n in shots)
    # min 8/sqrt(n1)+1/sqrt(n2) has n1/n2=4 for the uncapped continuous optimum.
    assert abs(shots[0]-800)<=1
    assert allocate([1.,1.],128)==[64,64]
    with pytest.raises(ValueError):allocate([1.,1.],127)
