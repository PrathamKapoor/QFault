"""Independent backend conformance evidence, separate from policy holdout."""
import argparse,json,platform,sys
from pathlib import Path
import numpy as np,qiskit,qiskit_aer
from qfault.quantum import benchmark,contract,Noise,execute,noisy_density
from qfault.backends import aer_simulator
from qfault.evidence import canonical,digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(a.out);root.mkdir(parents=True,exist_ok=False);rows=[]
    for family,n in [('bell',2),('ghz',3),('qft',3)]:
        c=benchmark(family,n)
        for label,noise in [('ideal',Noise()),('readout',Noise(readout=.18)),('depolarizing',Noise(depolarizing=.2))]:
            records={b:execute(c,noise,4096,317,backend=b) for b in ['reference','aer']}
            path=root/(family+'-'+label+'.json');path.write_bytes(canonical(records))
            expected=noisy_density(c,noise).probabilities_dict()
            if noise.readout:
                corrected={k:0. for k in expected}
                for src,pv in expected.items():
                    for dst in expected:
                        d=sum(x!=y for x,y in zip(src,dst));corrected[dst]+=pv*noise.readout**d*(1-noise.readout)**(n-d)
                expected=corrected
            q=c.native();q.save_density_matrix();rho=aer_simulator(c,noise).run(q).result().data(0)['density_matrix'].data
            density_error=float(np.max(np.abs(rho-noisy_density(c,noise).data)))
            tv={b:.5*sum(abs(r['output_counts'].get(k,0)/4096-v) for k,v in expected.items()) for b,r in records.items()}
            assert density_error<1e-12 and all(v<.08 for v in tv.values())
            rows.append({'family':family,'noise':label,'shots_per_backend':4096,'TV_from_analytic_noisy_distribution':tv,'maximum_density_element_error':density_error,'artifact':str(path),'sha256':digest(records)})
    summary={'python':sys.version,'architecture':platform.machine(),'qiskit':qiskit.__version__,'aer':qiskit_aer.__version__,'aer_package':qiskit_aer.__file__,'rows':rows,'limitations':['Conformance of these small simulated circuits, not hardware validation','Backend seeds reproduce within backend, not identical draws across backends','No transpilation; same per-logical-gate depolarizing channel']}
    (root/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
