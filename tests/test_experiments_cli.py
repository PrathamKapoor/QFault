import json
from qfault.cli import main
from qfault.experiments import summarize


def test_summary_counts_abstention_and_false_diagnosis():
    rows=[{"truth":"LOGICAL_CIRCUIT_DEFECT","prediction":"INSUFFICIENT_EVIDENCE","shots":100,"evaluations":2},
          {"truth":"NO_SIGNIFICANT_FAILURE_DETECTED","prediction":"LOGICAL_CIRCUIT_DEFECT","shots":100,"evaluations":2}]
    r=summarize(rows)
    assert r["accuracy"]["successes"]==0 and r["accuracy"]["n"]==2
    assert r["abstention"]["successes"]==1
    assert r["clean_false_diagnosis"]["successes"]==1
    assert r["selective_accuracy"]["n"]==1


def test_cli_lists_and_runs_real_quantum(tmp_path,capsys):
    assert main(["circuits"])==0
    assert "bell" in capsys.readouterr().out
    assert main(["--store",str(tmp_path),"run","--family","bell","--scenario","remove"])==0
    r=json.loads(capsys.readouterr().out)
    eid=r["experiment_id"]
    assert r["recovery"]["verification"]["verified_status"]=="VERIFIED"
    assert main(["--store",str(tmp_path),"verify",eid])==0
    assert json.loads(capsys.readouterr().out)["valid"]


def test_cli_demo_includes_tamper_check(tmp_path,capsys):
    assert main(["--store",str(tmp_path),"demo"])==0
    r=json.loads(capsys.readouterr().out)
    assert r["integrity_demonstration"]=={"original":True,"tampered":False,"restored":True}
    assert len(r["investigations"])==6
