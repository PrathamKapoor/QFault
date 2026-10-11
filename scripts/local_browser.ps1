# Read-only installed Playwright bridge; starts a separate headless test browser.
$ErrorActionPreference = 'Stop'
$runtime = 'C:\Program Files\LibreOffice\program\python.exe'
& $runtime -B -u "$PSScriptRoot\browser_bootstrap.py" @args
exit $LASTEXITCODE
