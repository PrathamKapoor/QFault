from scripts.measurement_holdout import cases,summarize
import json
from pathlib import Path


def test_prespecified_case_membership():
    protocol=json.loads(Path('benchmarks/measurement-holdout-protocol.json').read_bytes())
    generated=list(cases(protocol))
    assert len(generated)==52
    assert len({c['case_id'] for c in generated})==52
    assert {c['seed'] for c in generated}=={1201,3253}
    assert sum(c['condition']['name']=='small_angle' for c in generated)==2


def test_ambiguous_category_match_is_not_measurement_attribution_success():
    rows=[dict(truth='MIXED_OR_AMBIGUOUS',prediction='MIXED_OR_AMBIGUOUS',abstained=True,
               supported_discrepancy=True,shots=7168,additional_shots=3072,evaluations=4,
               executions=4,runtime_seconds=.1,case_id='mixed',strict_correct=False)]
    summary=summarize(rows)
    assert summary['strict_attribution']['successes']==0
    assert summary['abstention']['successes']==1
    assert summary['per_class_recall']['MIXED_OR_AMBIGUOUS']['successes']==0
