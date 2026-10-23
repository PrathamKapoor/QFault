import os
from pathlib import Path
import subprocess
import sys


def test_hosted_entrypoint_does_not_initialize_store_in_readonly_project():
    code='''
import os,tempfile
from pathlib import Path
from qfault.storage import ArtifactStore
original=ArtifactStore.__init__
def guarded(self,root):
 assert Path(root).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()), 'read-only project store'
 return original(self,root)
ArtifactStore.__init__=guarded
os.environ.pop('QFAULT_ARTIFACTS',None)
import api.index
'''
    result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_hosted_lock_includes_aer_and_keeps_original_versions_and_hashes():
    import re,tomllib
    root=Path(__file__).resolve().parents[1]
    lock=root/'api/uv.lock'
    assert lock.exists(),'Vercel-native hosted lock is absent'
    original=(root/'requirements.lock').read_text()
    pins={name.lower().replace('_','-'):version for name,version in re.findall(r'^([A-Za-z0-9_.-]+)==([^\s;\\]+)',original,re.M)}
    hashes=set(re.findall(r'sha256:([0-9a-f]{64})',original))
    packages=tomllib.loads(lock.read_text())['package']
    selected={p['name'] for p in packages}
    assert 'qiskit-aer' in selected
    for package in packages:
        if 'registry' not in package['source']:continue
        assert pins[package['name']]==package['version']
        artifacts=package.get('wheels',[])+([package['sdist']] if package.get('sdist') else [])
        assert all(artifact['hash'].removeprefix('sha256:') in hashes for artifact in artifacts)
