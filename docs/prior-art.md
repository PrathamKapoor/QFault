# Positioning and dependency choices

QFAULT does not claim invention of quantum mutation testing, equivalence checking, noise simulation or error mitigation.

- [Muskit](https://github.com/Simula-COMPLEX/muskit) documents Qiskit gate mutation, selection, execution and test analysis. Its AGPL-3.0 source is not copied.
- [QuMuS](https://github.com/Qcraft-UEx/QuMuS) addresses generation and execution of quantum mutants. Not installed or copied.
- [MQT QCEC](https://github.com/munich-quantum-toolkit/qcec) addresses circuit equivalence. Not installed; QFAULT verifies only a declared fixed-input state and explicitly reports full unitary equivalence as NOT_CHECKED.
- [Qiskit Experiments](https://qiskit-community.github.io/qiskit-experiments/) provides experimental characterization and calibration workflows. Not required for the small local corpus.
- [Mitiq](https://github.com/unitaryfoundation/mitiq) provides error-mitigation techniques. Not installed; measurement mitigation is unavailable in this release.
- [Qiskit Aer](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html) documents noise-model simulation. The available local 0.17.2 binary targets CPython 3.11 and cannot import under the accessible 3.13 runtime. QFAULT does not pretend to execute Aer. Ideal sampling uses Qiskit BasicSimulator; depolarization uses Qiskit DensityMatrix/Kraus.
- [Qiskit API](https://quantum.cloud.ibm.com/docs/en/api/qiskit) supplies actual QuantumCircuit, Statevector, DensityMatrix, Kraus, Operator and BasicSimulator operations. QFAULT executed version 2.3.1.

The intended research question is whether evidence-triggered diagnostic selection improves useful diagnosis per finite execution budget. Current experiments do not establish an advantage: the fixed plan is more accurate, and the simple threshold matches the proposed policy with fewer shots. This is a preliminary negative result on a small fixed corpus.

The reviewed reference documentation is not an exhaustive literature review of published fault-identification methods. Novelty, hardware validity and quantum advantage are unestablished.

## Minimal dependency decision

Qiskit supplies the scientific execution core. NumPy supports state references and explicit sampling channels; SciPy is a Qiskit dependency. Pydantic validates structured input; FastAPI and Uvicorn serve localhost; pytest and httpx run real integration checks. Tested versions and their runtime closure are recorded in requirements-tested.txt. React/TypeScript/Vite provide the interface; no chart, animation, state-management or icon package is added.

Docker, Redis, PostgreSQL, Celery, external models and cloud services are unnecessary. File artifacts are sufficient for this bounded local application. MQT QCEC, Mitiq, Aer integration and ML-DSA signing remain unavailable rather than decorative dependencies.
