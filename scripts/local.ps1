# Uses existing packages read-only. No source repository is changed.
$ErrorActionPreference = 'Stop'
$runtime = 'C:\Program Files\LibreOffice\program\python.exe'
& $runtime -B -u "$PSScriptRoot\local_bootstrap.py" @args
exit $LASTEXITCODE
