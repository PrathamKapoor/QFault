"""Canonical artifact bytes and immutable evidence references."""
import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def identifier(prefix):
    return f"{prefix}_{uuid4().hex}"


def timestamp():
    return datetime.now(timezone.utc).isoformat()
