"""Optional Aer adapter. Requested Aer failures never become reference successes."""
def aer_simulator(circuit,noise):
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel,depolarizing_error,ReadoutError
    model=NoiseModel()
    if noise.depolarizing:
        for name,arity in sorted({(g.name,len(g.qubits)) for g in circuit.gates}):
            model.add_all_qubit_quantum_error(depolarizing_error(noise.depolarizing,arity),name)
    if noise.readout:
        p=noise.readout
        model.add_all_qubit_readout_error(ReadoutError([[1-p,p],[p,1-p]]))
    # Explicit logical gates: no transpilation changes the per-gate channel count.
    return AerSimulator(method='density_matrix',noise_model=model,max_parallel_threads=1)


def aer_counts(circuit,noise,shots,seed):
    import qiskit_aer
    q=circuit.native();q.measure_all()
    result=aer_simulator(circuit,noise).run(q,shots=shots,seed_simulator=seed).result()
    if not result.success:
        raise RuntimeError(str(result.status))
    return {str(k):int(v) for k,v in result.get_counts().items()},qiskit_aer.__version__
