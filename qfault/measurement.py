"""Finite-shot diagnosis with no candidate, noise metadata or state oracle.

The executor supplies an opaque measurement capability. Analytical expectations
belong to the declared target, never an evolved state of the faulty system.
"""
from dataclasses import dataclass
from typing import Callable
from .quantum import Contract, probabilities, measurement_probabilities
from .diagnostics import comparison


@dataclass(frozen=True)
class MeasurementPort:
    measure: Callable  # (basis, shots) -> allowlisted MeasuredEvidence
    can: Callable      # budget predicate, no execution internals


class MeasurementOnlyAnalyst:
    def analyze(self, contract, measured, port, plan='complementary'):
        if not isinstance(contract,Contract):
            return {'category':'UNSUPPORTED','reason':'No supported analytical contract',
                    'capability_mode':'measurement_only','confidence':None}
        if plan not in {'z_only','complementary'}:
            raise ValueError('unsupported measurement plan')
        discrepancy=comparison(measured,probabilities(contract.state()),contract.distribution_tolerance)
        phase=None
        calibration=None
        refs=[measured.execution_id]
        if measured.shots>=128 and plan=='complementary' and port.can(min(2048,measured.shots)):
            evidence=port.measure('complementary',min(2048,measured.shots))
            expected=measurement_probabilities(contract)
            phase={'basis':'X parity' if contract.family in {'bell','ghz'} else 'analytic Fourier product basis',
                   'execution_id':evidence.execution_id,'measured':evidence.model_dump(),
                   'comparison':comparison(evidence,expected,contract.distribution_tolerance),
                   'expected_probabilities':expected}
            refs.append(evidence.execution_id)
        if measured.shots>=128 and port.can(1024):
            evidence=port.measure('readout_control',1024)
            expected={format(i,f'0{contract.n_qubits}b'):float(i==0) for i in range(2**contract.n_qubits)}
            calibration=comparison(evidence,expected,.10)
            refs.append(evidence.execution_id)
        failure=discrepancy['significant_disagreement'] or bool(phase and phase['comparison']['significant_disagreement'])
        noise=bool(calibration and calibration['significant_disagreement'])
        if measured.shots<128 or (plan=='complementary' and phase is None):
            category='INSUFFICIENT_EVIDENCE'
            reason='The required finite-shot measurement plan was not funded; no attribution is made.'
        elif noise:
            category='NOISE_CONSISTENT_DEGRADATION'
            reason='A measured readout control disagrees. This supports noise consistency, not a unique cause; concurrent logical faults remain possible.'
        elif failure:
            category='MIXED_OR_AMBIGUOUS'
            reason='Supported contract discrepancy. A logical-fault hypothesis and gate noise remain indistinguishable with these measurements.'
        else:
            category='NO_SIGNIFICANT_FAILURE_DETECTED'
            reason='No significant discrepancy in the measured bases; unmeasured or small faults remain possible.'
        return {'category':category,'reason':reason,'policy':'measurement_'+plan,
                'capability_mode':'measurement_only','supported_discrepancy':failure,
                'discrepancy':discrepancy,'phase_probe':phase,'readout_probe':calibration,
                'state_probe':None,'state_infidelity':None,'candidate_distribution_comparison':None,
                'hypotheses':[{'hypothesis':'logical fault','support':'consistent, not uniquely established' if failure else 'not established'},
                              {'hypothesis':'execution noise','support':'control-supported' if noise else 'gate noise not excluded'},
                              {'hypothesis':'finite-shot variation','support':'bounded; no calibrated class probability'}],
                'evidence_references':refs,'confidence':None,'confidence_semantics':'No class probability claimed',
                'limitations':['No faulty-state oracle, injected metadata or evaluator truth is available',
                    'Calibration cannot rule out gate noise or simultaneous logical defects',
                    'Complementary witnesses are incomplete; no full tomography or unitary equivalence',
                    'Z-only measurements can miss relative phase faults',
                    'Recovery is disabled: measured candidate selection/validation is not implemented',
                    'At most three TV comparisons; per-comparison alpha=0.001; union bound <=0.003']}
