import copy
import pytest
from qfault import storage
from qfault.workflow import RunRequest,investigate


def test_export_verifies_and_detects_covered_changes(tmp_path):
    store=storage.ArtifactStore(tmp_path)
    eid=store.save(investigate(RunRequest(scenario='phase',policy='phase',seed=71)))
    store.review(eid,'PrathamKapoor','acknowledge','Reviewed independent phase verification')
    report=store.export(eid)
    assert hasattr(storage,'verify_export'), 'standalone exported-report verification missing'
    assert storage.verify_export(report)['valid']
    tampered=copy.deepcopy(report)
    tampered['investigation']['diagnosis']['category']='NO_SIGNIFICANT_FAILURE_DETECTED'
    assert not storage.verify_export(tampered)['valid']
    tampered=copy.deepcopy(report)
    tampered['reviews']=[]
    assert not storage.verify_export(tampered)['valid']

@pytest.mark.parametrize('bad',[None,[],{}, {'manifest':None}])
def test_malformed_export_fails_closed(bad):
    assert hasattr(storage,'verify_export'), 'standalone exported-report verification missing'
    assert not storage.verify_export(bad)['valid']
