"""Machine-specific read-only Playwright bridge; separate from quantum runtime."""
import runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),'C:/Users/LENOVO/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/site-packages']
module=sys.argv.pop(1);runpy.run_module(module,run_name='__main__',alter_sys=True)
