"""Vercel ASGI entrypoint; local qfault serve keeps its original boundary."""
import os
import tempfile

# Importing the legacy API constructs its unused local app. Keep that bootstrap
# inside scratch storage; actual hosted requests always restore their own snapshot.
_bootstrap=tempfile.TemporaryDirectory(prefix='qfault-import-')
os.environ['QFAULT_ARTIFACTS']=_bootstrap.name
from qfault.api import RequestBodyLimit
from qfault.hosting import HostedApp

_boundary=RequestBodyLimit(HostedApp())


async def app(scope,receive,send):
    await _boundary(scope,receive,send)
