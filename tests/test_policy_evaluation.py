from qfault import experiments


def test_frozen_comparison_records_real_costs_and_all_baselines(tmp_path):
    assert hasattr(experiments,'compare_policies'), 'new frozen policy comparison missing'
    config={'protocol':'test','base_commit':'test','policies':['fixed','threshold','random','evidence','phase'],
        'shots':256,'max_shots':4096,'max_evaluations':6,'scenarios':['phase'],'qft_extra':[],
        'development':{'circuits':[['bell',2]],'seeds':[71]}}
    result=experiments.compare_policies(config,tmp_path/'evaluation','development')
    assert len(result['rows'])==5
    assert set(result['policies'])==set(config['policies'])
    assert all(r['shots']<=4096 and r['evaluations']<=6 for r in result['rows'])
    assert all(r['executions']>=2 for r in result['rows'])
    assert result['configuration_digest']
