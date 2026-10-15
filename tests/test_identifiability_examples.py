"""Qiskit counterexamples distinguish observability from causal identifiability."""
import importlib
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from qiskit.quantum_info import DensityMatrix, Kraus, Statevector

from qfault.evidence import digest
from qfault.quantum import Circuit


def test_reproducible_identifiability_runner_exists():
    assert Path("scripts/identifiability_examples.py").is_file()


@pytest.fixture(scope="module")
def report():
    script = importlib.import_module("scripts.identifiability_examples")
    return script.build_report(shot_grid=(64, 512), seed=20261016)


def example(report, name):
    return next(row for row in report["examples"] if row["example_id"] == name)


def test_phase_equal_z_distribution_is_broken_by_xx(report):
    case = example(report, "phase_visibility")
    assert case["evaluator_oracle"]["z_total_variation"] == pytest.approx(0., abs=1e-12)
    assert case["evaluator_oracle"]["xx_total_variation"] == pytest.approx(1., abs=1e-12)
    assert case["evaluator_oracle"]["state_fidelity"] == pytest.approx(0., abs=1e-12)
    samples = {row["measurement_id"]: row for row in report["measurements"]}
    for measurement_id in case["measurement_ids"]:
        row = samples[measurement_id]
        if row["setting"] == "XX":
            parity = {sum(int(bit) for bit in k) % 2 for k, n in row["counts"].items() if n}
            assert parity == ({0} if row["subject"] == "bell_plus" else {1})


def test_distinct_edits_have_identical_fixed_input_state(report):
    case = example(report, "equivalent_repairs")
    assert len({s["circuit_id"] for s in case["subjects"]}) == 3
    assert {s["edit"]["operator"] for s in case["subjects"]} == {"remove", "replace", "insert"}
    oracle = case["evaluator_oracle"]
    assert oracle["maximum_pairwise_density_distance"] < 1e-12
    assert oracle["some_full_unitaries_differ"]
    assert case["identifiability"]["all_povms_indistinguishable_on_declared_input"]
    programs = [Circuit.model_validate(s["circuit"]).native() for s in case["subjects"]]
    states = [DensityMatrix.from_instruction(q).data for q in programs]
    for state in states:
        np.testing.assert_allclose(state, np.diag([1., 0., 0., 0.]), atol=1e-12)
    # A new input distinguishes I from Z; fixed-input equality was not unitary equality.
    probe = Statevector([2**-.5, 2**-.5, 0., 0.])
    assert not probe.evolve(programs[0]).equiv(probe.evolve(programs[1]))


def test_physical_channel_and_logical_unitary_share_output_density(report):
    case = example(report, "logical_vs_channel")
    assert case["evaluator_oracle"]["density_distance"] < 1e-12
    assert case["channel"]["definition"] == "E(rho) = X_0 rho X_0"
    assert case["channel"]["supported_by_qfault_noise_schema"] is False
    assert case["identifiability"]["causal_origin"] == "NOT_IDENTIFIABLE_FROM_OUTPUT_STATE"
    logical = Circuit.model_validate(case["subjects"][0]["circuit"])
    rho_logical = DensityMatrix.from_instruction(logical.native())
    channel = Kraus([np.asarray(k, dtype=complex) for k in case["channel"]["kraus_operators"]])
    rho_channel = DensityMatrix.from_label("00").evolve(channel, qargs=[0])
    np.testing.assert_allclose(rho_logical.data, rho_channel.data, atol=1e-12)
    samples = [m for m in report["measurements"] if m["measurement_id"] in case["measurement_ids"]]
    assert {m["backend"] for m in samples} == {"reference", "aer"}
    for sample in samples:
        if sample["setting"] == "ZZ":
            assert sample["counts"] == {"01": sample["shots"]}


def test_more_shots_do_not_resolve_structural_ambiguity(report):
    case = example(report, "more_shots_unchanged")
    assert case["shot_grid"] == [64, 512]
    assert case["exact_product_distributions_equal_for_any_shot_count"]
    assert case["ambiguity_at_each_shot_count"] == [3, 3]
    assert case["basis_of_conclusion"] == "Equal density matrices imply identical POVM probabilities; tensor powers preserve equality"


def test_supported_readout_can_mimic_a_logical_z_distribution(report):
    case = example(report, "readout_z_ambiguity")
    assert case["noise_configuration"] == {"readout": .5, "depolarizing": 0.}
    assert case["evaluator_oracle"]["z_total_variation"] < 1e-12
    assert case["evaluator_oracle"]["xx_total_variation"] == pytest.approx(.75, abs=1e-12)
    assert case["identifiability"]["z_only_causal_attribution"] == "NOT_ESTABLISHED"


def test_export_accounts_for_real_measurements_and_provenance(report, tmp_path):
    script = importlib.import_module("scripts.identifiability_examples")
    measurements = report["measurements"]
    assert {m["backend"] for m in measurements} == {"reference", "aer"}
    assert len({m["seed"] for m in measurements}) == len(measurements)
    assert report["cost"]["executions"] == len(measurements)
    assert report["cost"]["shots"] == sum(m["shots"] for m in measurements)
    assert all(sum(m["counts"].values()) == m["shots"] for m in measurements)
    assert all(m["execution_status"] == "SUCCEEDED" for m in measurements)
    assert "qiskit-aer" in report["software_versions"]
    assert report["provenance"]["source_sha256"]["scripts/identifiability_examples.py"]
    for path, expected in report["provenance"]["source_sha256"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
    assert report["report_digest"] == digest({k: v for k, v in report.items() if k != "report_digest"})
    path = tmp_path / "examples.json"
    script.write_report(path, report)
    original = path.read_bytes()
    assert json.loads(original) == report
    with pytest.raises(FileExistsError):
        script.write_report(path, report)
    assert path.read_bytes() == original


def test_reproduction_repeats_every_count_and_digest(report):
    script = importlib.import_module("scripts.identifiability_examples")
    repeated = script.build_report(shot_grid=(64, 512), seed=20261016)
    assert repeated == report


@pytest.mark.parametrize("shots,seed", [((0, 64), 1), ((64, 100001), 1), ((64, 64), 1), ((64, 512), -1)])
def test_invalid_reproduction_settings_fail_before_execution(shots, seed):
    script = importlib.import_module("scripts.identifiability_examples")
    with pytest.raises(ValueError):
        script.build_report(shot_grid=shots, seed=seed)
