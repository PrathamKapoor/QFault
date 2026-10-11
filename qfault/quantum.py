"""Validated small circuits, analytic contracts and explicit local simulation."""
from itertools import product
from math import pi
from time import perf_counter
from typing import Literal
import importlib.metadata as metadata
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Kraus, Operator, Pauli, Statevector
from qiskit.providers.basic_provider import BasicSimulator
from .evidence import digest, identifier


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class Gate(Strict):
    name: Literal["h", "x", "z", "s", "rx", "ry", "rz", "cx", "cz", "cp", "swap"]
    qubits: tuple[int, ...]
    angle: float | None = None

    @model_validator(mode="after")
    def valid(self):
        arity = 2 if self.name in {"cx", "cz", "cp", "swap"} else 1
        if len(self.qubits) != arity or len(set(self.qubits)) != arity or min(self.qubits)<0:
            raise ValueError("invalid gate qubit assignment")
        rotation = self.name in {"rx", "ry", "rz", "cp"}
        if rotation != (self.angle is not None):
            raise ValueError("rotation gates require an angle; other gates forbid one")
        if self.angle is not None and abs(self.angle)>8*pi:
            raise ValueError("angle must lie within +/-8 pi radians")
        return self


class Circuit(Strict):
    n_qubits: int = Field(ge=2, le=5, strict=True)
    gates: tuple[Gate, ...] = Field(max_length=32)

    @model_validator(mode="after")
    def valid(self):
        if any(max(g.qubits)>=self.n_qubits for g in self.gates):
            raise ValueError("qubit index outside circuit")
        return self

    def native(self):
        q=QuantumCircuit(self.n_qubits)
        for gate in self.gates:
            args=gate.qubits if gate.angle is None else (gate.angle, *gate.qubits)
            getattr(q,gate.name)(*args)
        return q

    @property
    def circuit_id(self):
        return "circuit_"+digest(self.model_dump(mode="json"))[:20]


class Noise(Strict):
    readout: float = Field(default=0,ge=0,le=.5)
    depolarizing: float = Field(default=0,ge=0,le=1)


class Contract(Strict):
    family: Literal["bell","ghz","qft"]
    n_qubits: int = Field(ge=2,le=5,strict=True)
    input_basis: int = 0
    distribution_tolerance: float = .10
    state_infidelity_tolerance: float = 1e-8

    @model_validator(mode="after")
    def valid(self):
        if self.family=="bell" and self.n_qubits!=2:
            raise ValueError("Bell preparation uses exactly two qubits")
        if not 0<=self.input_basis<2**self.n_qubits:
            raise ValueError("basis input out of range")
        if self.family!="qft" and self.input_basis!=0:
            raise ValueError("state preparation assumes all-zero input")
        return self

    @property
    def contract_id(self):
        return "contract_"+digest(self.model_dump(mode="json"))[:20]

    def state(self):
        size=2**self.n_qubits
        if self.family=="qft":
            return np.exp(2j*pi*self.input_basis*np.arange(size)/size)/np.sqrt(size)
        out=np.zeros(size,dtype=complex)
        out[0]=out[-1]=1/np.sqrt(2)
        return out

    def describe(self):
        return {**self.model_dump(),"contract_id":self.contract_id,
                "category":"fixed_input_state", "input_assumptions":"Circuit starts in |0...0>; QFT template includes basis preparation",
                "expected_probabilities":probabilities(self.state()),
                "expected_state":[[float(z.real),float(z.imag)] for z in self.state()],
                "comparison":"state fidelity and measurement total variation; finite-shot concentration bound",
                "verification":"independent Qiskit state evolution against analytic state and fresh sampled counts",
                "limitations":["One input state does not establish unitary equivalence", "Computational-basis counts cannot detect every phase fault", "Simulation only"]}


def contract(family,n):
    return Contract(family=family,n_qubits=n,input_basis=1 if family=="qft" else 0)


def benchmark(family,n):
    spec=contract(family,n)
    gates=[]
    def add(name,*qubits,angle=None):
        gates.append(Gate(name=name,qubits=qubits,angle=angle))
    if family in {"bell","ghz"}:
        add("h",0)
        for j in range(1,n): add("cx",0,j)
    else:
        add("x",0)  # declared basis input 1
        for j in reversed(range(n)):
            add("h",j)
            for k in reversed(range(j)):
                add("cp",j,k,angle=pi/2**(j-k))
        for j in range(n//2): add("swap",j,n-1-j)
    return Circuit(n_qubits=n,gates=tuple(gates))


def ideal_state(circuit):
    return np.asarray(Statevector.from_instruction(circuit.native()).data)


def probabilities(state):
    n=int(np.log2(len(state)))
    return {format(i,f"0{n}b"):float(abs(v)**2) for i,v in enumerate(state)}


def resources(circuit):
    q=circuit.native()
    return {"depth":q.depth(),"gates":len(circuit.gates),
            "two_qubit_gates":sum(len(g.qubits)==2 for g in circuit.gates),"qubits":circuit.n_qubits}


def noisy_density(circuit,noise):
    rho=DensityMatrix.from_label("0"*circuit.n_qubits)
    channels={}
    for gate in circuit.gates:
        local=QuantumCircuit(len(gate.qubits))
        args=tuple(range(len(gate.qubits)))
        if gate.angle is not None: args=(gate.angle,*args)
        getattr(local,gate.name)(*args)
        rho=rho.evolve(Operator(local),qargs=list(gate.qubits))
        if noise.depolarizing:
            k=len(gate.qubits)
            if k not in channels:
                p=noise.depolarizing
                ops=[np.sqrt(1-p)*np.eye(2**k)]
                ops += [np.sqrt(p/4**k)*Pauli("".join(s)).to_matrix() for s in product("IXYZ",repeat=k)]
                channels[k]=Kraus(ops)
            rho=rho.evolve(channels[k],qargs=list(gate.qubits))
    return rho


def execute(circuit,noise,shots,seed,experiment_id="standalone",contract_id=None):
    if type(shots) is not int or not 1<=shots<=100000:
        raise ValueError("shots must be an integer in [1,100000]")
    if type(seed) is not int or not 0<=seed<2**32:
        raise ValueError("seed must be a uint32")
    start=perf_counter()
    q=circuit.native()
    if noise.depolarizing:
        rho=noisy_density(circuit,noise)
        rho.seed(seed)
        counts={str(k):int(v) for k,v in rho.sample_counts(shots).items()}
        backend="qiskit.quantum_info.DensityMatrix/Kraus"
    else:
        q.measure_all()
        result=BasicSimulator().run(q,shots=shots,seed_simulator=seed).result()
        if not result.success: raise RuntimeError(str(result.status))
        counts={str(k):int(v) for k,v in result.get_counts().items()}
        backend="basic_simulator"
    if noise.readout:
        rng=np.random.default_rng(seed ^ 0x5A17)
        changed={}
        for bits,count in sorted(counts.items()):
            samples=np.tile(np.array([int(b) for b in bits]),(count,1))
            samples ^= (rng.random(samples.shape)<noise.readout).astype(int)
            for sample in samples:
                key="".join(str(x) for x in sample)
                changed[key]=changed.get(key,0)+1
        counts=changed
    if sum(counts.values())!=shots: raise RuntimeError("shot accounting mismatch")
    return {"execution_id":identifier("exec"),"experiment_id":experiment_id,
            "circuit_id":circuit.circuit_id,"contract_id":contract_id,
            "backend_name":backend,"backend_type":"local_simulator",
            "transpilation_settings":{"method":"none; explicit supported gates"},
            "noise_configuration":noise.model_dump(),"requested_shots":shots,"executed_shots":sum(counts.values()),
            "seed":seed,"input_digest":digest(circuit.model_dump(mode="json")),"output_counts":counts,
            "observable_results":{},"execution_status":"SUCCEEDED","failure_reason":None,
            "software_versions":{p:metadata.version(p) for p in ["qiskit","numpy","scipy","pydantic"]},
            "resources":resources(circuit),"runtime_seconds":perf_counter()-start}


def mutate(circuit,operator,index,seed):
    if not 0<=index<len(circuit.gates): raise ValueError("mutation location outside gate list")
    rng=np.random.default_rng(seed)
    gates=list(circuit.gates)
    gate=gates[index]
    if operator=="remove": del gates[index]
    elif operator=="replace":
        options=[s for s in (["h","x","z"] if len(gate.qubits)==1 else ["cx","cz","swap"]) if s!=gate.name]
        gates[index]=Gate(name=str(rng.choice(options)),qubits=gate.qubits)
    elif operator=="angle":
        if gate.angle is None: raise ValueError("target is not a rotation")
        gates[index]=Gate(name=gate.name,qubits=gate.qubits,angle=gate.angle+pi/4)
    elif operator=="rewire":
        assignments=[a for a in product(range(circuit.n_qubits),repeat=len(gate.qubits)) if len(set(a))==len(a) and a!=gate.qubits]
        if not assignments: raise ValueError("no admissible qubit assignment")
        gates[index]=Gate(name=gate.name,qubits=assignments[int(rng.integers(len(assignments)))],angle=gate.angle)
    else: raise ValueError("unsupported mutation operator")
    changed=Circuit(n_qubits=circuit.n_qubits,gates=tuple(gates))
    truth={"mutation_id":identifier("mutation"),"operator":operator,"index":index,"seed":seed,
           "original_circuit_id":circuit.circuit_id,"result_digest":digest(changed.model_dump(mode="json")),
           "original_gate":gate.model_dump(mode="json")}
    return changed,truth


def measurement_rotation(spec):
    """Contract-defined local analysis basis; never depends on injected truth.

    Bell/GHZ: measure X on every qubit (even parity for positive GHZ).
    QFT basis input k: cancel each analytic product phase, then measure X.
    Global phase cancels in every probability.
    """
    gates=[]
    for j in range(spec.n_qubits):
        if spec.family=='qft':
            angle=-2*pi*spec.input_basis*2**j/2**spec.n_qubits
            gates.append(Gate(name='rz',qubits=(j,),angle=angle))
        gates.append(Gate(name='h',qubits=(j,)))
    return Circuit(n_qubits=spec.n_qubits,gates=tuple(gates))


def measurement_probabilities(spec,state=None):
    target=spec.state() if state is None else state
    return probabilities(Statevector(target).evolve(measurement_rotation(spec).native()).data)


def measured_circuit(candidate,spec):
    return Circuit(n_qubits=candidate.n_qubits,gates=candidate.gates+measurement_rotation(spec).gates)
