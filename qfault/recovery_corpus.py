"""Independent recovery designs. Contract targets come from intact references only.

Reference state computation is evaluator-side contract construction, not an oracle
given to the recovery engine. Ground-truth edit loci are never part of its request.
"""
from math import pi
from qiskit.quantum_info import Statevector
from .lab import CustomCircuit
from .quantum import benchmark

POLICIES = ['no_repair','first_admissible','random','point_discrepancy','conservative']
SEEDS = {'development':[113], 'holdout':[731,1297]}


def g(name,*qubits,angle=None):
    return {'name':name,'qubits':list(qubits),**({'angle':angle} if angle is not None else {})}


def cases(split):
    designs = [
        ('bell',2,[g('h',0),g('cx',0,1)],'target'),
        ('ghz',3,[g('h',0),g('cx',0,1),g('cx',1,2)],'target'),
        ('cluster',3,[g('h',0),g('h',1),g('h',2),g('cz',0,1),g('cz',1,2)],'pauli'),
        ('product',2,[g('h',0),g('h',1)],'pauli'),
        ('clifford',2,[g('h',0),g('cx',0,1),g('s',1)],'target'),
        ('rotation',2,[g('ry',0,angle=.7),g('cx',0,1)],'target'),
        ('qft',2,[x.model_dump(mode='json') for x in benchmark('qft',2).gates],'target'),
    ]
    for seed in SEEDS[split]:
        for family,n,gates,kind in designs:
            reference=CustomCircuit.model_validate({'schema_version':1,'name':family,'n_qubits':n,
                'input':{'kind':'computational_basis','bitstring':'0'*n},'gates':gates})
            v=Statevector.from_instruction(reference.subject().native()).data
            target={'kind':'target_state','amplitudes':[[float(z.real),float(z.imag)] for z in v],
                    'fidelity_tolerance':.2,'provenance':'Intact reference design, before mutation'}
            if kind=='pauli':
                labels=['XZI','ZXZ','IZX'] if family=='cluster' else ['IX','XI']
                target={'kind':'pauli_expectations','observables':[{'pauli':p,'expected':1,'tolerance':.15} for p in labels]}
            for variant in ['logical','clean','readout','gate_noise']:
                circuit=reference.model_dump(mode='json')
                locus=None
                if variant=='logical':
                    # Appended phase intervention; some fixed-input QFT cases can remain undetected.
                    circuit['gates']=gates+[g('z',0)];locus=len(gates)
                environment={'readout':.25 if variant=='readout' else 0.,'depolarizing':.08 if variant=='gate_noise' else 0.}
                yield {'case_id':f'{family}-{variant}-{seed}','family':family,'variant':variant,
                    'truth_locus':locus,'request':{'circuit':circuit,'contract':target,'environment':environment,
                    'seed':seed,'max_candidates':12,'screen_shots':2048,'verification_shots':4096,
                    'max_shots':200000,'max_evaluations':160}}
        # Partial distribution contract: phase mutation is intentionally invisible.
        circuit={'schema_version':1,'name':'incomplete Bell distribution','n_qubits':2,
                 'input':{'kind':'computational_basis','bitstring':'00'},'gates':[g('h',0),g('cx',0,1),g('z',0)]}
        base={'circuit':circuit,'contract':{'kind':'measurement_distribution','expected_probabilities':{'00':.5,'11':.5},'tolerance':.15},'seed':seed}
        yield {'case_id':f'incomplete-{seed}','family':'bell','variant':'incomplete','truth_locus':2,'request':base}
        # Ambiguity: removing either identical X produces the required |10> input response.
        circuit={'schema_version':1,'name':'ambiguous repeated X','n_qubits':2,
                 'input':{'kind':'computational_basis','bitstring':'00'},'gates':[g('x',0),g('x',0)]}
        base={'circuit':circuit,'contract':{'kind':'measurement_distribution','expected_probabilities':{'01':1.},'tolerance':.15},'seed':seed}
        yield {'case_id':f'ambiguous-{seed}','family':'product','variant':'ambiguous','truth_locus':1,'request':base}
        yield {'case_id':f'budget-{seed}','family':'product','variant':'budget','truth_locus':1,'request':{**base,'max_shots':128}}

