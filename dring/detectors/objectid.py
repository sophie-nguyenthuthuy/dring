"""MongoDB ObjectId — 24 hex chars; extracts the embedded creation time."""

import re

from ..util import iso_from_s

NAME = "objectid"
_RE = re.compile(r"^[0-9a-fA-F]{24}$")


def detect(s):
    s = s.strip().lower()
    if not _RE.match(s):
        return None
    ts = int(s[:8], 16)
    iso = iso_from_s(ts)
    plausible = iso is not None and 2000 <= int(iso[:4]) <= 2035
    return {
        "type": NAME,
        "confidence": 0.75 if plausible else 0.35,
        "summary": f"MongoDB ObjectId created {iso}" if plausible else "24 hex chars (ObjectId shape, timestamp implausible)",
        "details": {"timestamp_iso": iso, "machine_pid": s[8:18], "counter": s[18:]},
    }
