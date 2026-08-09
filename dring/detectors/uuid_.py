"""UUID — reports version/variant; extracts timestamps from v1 and v7."""

import re

from ..util import iso_from_ms, iso_from_s

NAME = "uuid"
_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_GREGORIAN_OFFSET_S = 12219292800  # 1582-10-15 -> 1970-01-01


def detect(s):
    s = s.strip().lower()
    if not _RE.match(s):
        return None
    version = int(s[14], 16)
    details = {"version": version, "variant_nibble": s[19]}
    summary = f"UUID v{version}"
    if version == 1:
        low, mid, hi = int(s[0:8], 16), int(s[9:13], 16), int(s[14:18], 16) & 0x0FFF
        t100 = (hi << 48) | (mid << 32) | low
        iso = iso_from_s(t100 / 1e7 - _GREGORIAN_OFFSET_S)
        details["timestamp_iso"] = iso
        details["node"] = s[24:]
        summary += f" (time-based), created {iso}"
    elif version == 4:
        summary += " (random)"
    elif version == 7:
        ms = int(s[0:8] + s[9:13], 16)
        iso = iso_from_ms(ms)
        details["timestamp_iso"] = iso
        summary += f" (unix-time-ordered), created {iso}"
    return {"type": NAME, "confidence": 0.95, "summary": summary, "details": details}
