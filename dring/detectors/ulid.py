"""ULID — 26 Crockford-base32 chars; extracts the 48-bit ms timestamp."""

import re

from ..util import CROCKFORD, iso_from_ms

NAME = "ulid"
# First char <= 7 keeps the timestamp within 48 bits (spec requirement).
_RE = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")


def detect(s):
    s = s.strip()
    if not _RE.match(s):
        return None
    ms = 0
    for ch in s[:10]:
        ms = ms * 32 + CROCKFORD.index(ch)
    iso = iso_from_ms(ms)
    return {
        "type": NAME,
        "confidence": 0.9,
        "summary": f"ULID created {iso}",
        "details": {"timestamp_ms": ms, "timestamp_iso": iso, "randomness": s[10:]},
    }
