"""Small deterministic real-Aer check, suitable for independent CI installs."""
from qfault.quantum import Noise,benchmark,execute


def main():
    circuit=benchmark('bell',2)
    first=execute(circuit,Noise(),1024,731,backend='aer')
    second=execute(circuit,Noise(),1024,731,backend='aer')
    assert first['output_counts']==second['output_counts']
    assert sum(first['output_counts'].values())==1024
    assert set(first['output_counts'])<={'00','11'}
    assert first['backend_name']=='qiskit_aer.AerSimulator/density_matrix'
    print('Deterministic Qiskit Aer Bell smoke passed:',first['output_counts'])


if __name__=='__main__':main()
