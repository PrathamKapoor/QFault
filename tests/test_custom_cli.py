import json

from qfault.cli import main
from qfault.storage import ArtifactStore, verify_export


def test_cli_import_validate_investigate_export_and_replay(tmp_path, capsys):
    source = tmp_path / 'circuit.qasm'
    source.write_text('OPENQASM 2.0; include "qelib1.inc"; qreg q[2]; h q[0]; cx q[0],q[1];')
    circuit_path = tmp_path / 'circuit.json'
    try:
        status = main(['import-qasm', str(source), '--out', str(circuit_path)])
    except SystemExit:
        status = 2
    assert status == 0, 'CLI must convert a local QASM circuit without loading Python'
    circuit = json.loads(circuit_path.read_bytes())
    assert circuit['import_provenance']['format'] == 'qasm2-v1'
    request_path = tmp_path / 'request.json'
    request_path.write_text(json.dumps({'circuit':circuit, 'contract':{'kind':'measurement_distribution',
        'basis':'Z','expected_probabilities':{'00':.5,'11':.5},'tolerance':.2}}))
    capsys.readouterr()
    assert main(['lab', str(request_path), '--validate-only']) == 0
    assert 'feasibility' in json.loads(capsys.readouterr().out)
    root = str(tmp_path / 'records')
    assert main(['--store',root,'lab',str(request_path)]) == 0
    result = json.loads(capsys.readouterr().out)
    store = ArtifactStore(root)
    exported = store.export(result['experiment_id'])
    assert verify_export(exported)['valid']
    assert exported['investigation']['configuration']['circuit']['import_provenance'] == circuit['import_provenance']
