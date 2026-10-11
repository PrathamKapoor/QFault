"""Machine-specific, read-only dependency bridge; normal installs do not use this."""
import os
import runpy
import sys
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path[:0] = [str(Path(__file__).resolve().parents[1]),
    "C:/Projects/Quantum_Simulator/.venv/Lib/site-packages",
    "C:/study/projects/quanum_ml/.python_lib"]
# Load only the verified cp313 Aer package, avoiding another environment's
# Qiskit/NumPy versions on sys.path. This remains a machine-specific bridge.
import importlib.util
_aer_path=Path('C:/Users/LENOVO/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/site-packages/qiskit_aer')
if _aer_path.exists():
    _spec=importlib.util.spec_from_file_location('qiskit_aer',_aer_path/'__init__.py',submodule_search_locations=[str(_aer_path)])
    _module=importlib.util.module_from_spec(_spec)
    sys.modules['qiskit_aer']=_module
    _spec.loader.exec_module(_module)
module = sys.argv.pop(1)
runpy.run_module(module, run_name="__main__", alter_sys=True)
