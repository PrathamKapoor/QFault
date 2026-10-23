"""Vercel ASGI entrypoint; local qfault serve keeps its original boundary."""
from qfault.api import RequestBodyLimit
from qfault.hosting import HostedApp

app=RequestBodyLimit(HostedApp())
