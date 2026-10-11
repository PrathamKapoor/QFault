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
module = sys.argv.pop(1)
runpy.run_module(module, run_name="__main__", alter_sys=True)
