"""Snowflake ID (Discord/Twitter) — extracts timestamp, worker, sequence."""

import re

from ..util import iso_from_ms

NAME = "snowflake"
_RE = re.compile(r"^\d{17,19}$")
_EPOCHS = [("Discord", 1420070400000), ("Twitter", 1288834974657)]


def detect(s):
    s = s.strip()
    if not _RE.match(s):
        return None
    n = int(s)
    out = []
    for origin, epoch in _EPOCHS:
        ms = (n >> 22) + epoch
        iso = iso_from_ms(ms)
        if iso is None or not (2010 <= int(iso[:4]) <= 2035):
            continue
        out.append(
            {
                "type": NAME,
                "confidence": 0.6,
                "summary": f"possible snowflake ID ({origin} epoch): {iso}",
                "details": {
                    "epoch": origin,
                    "timestamp_iso": iso,
                    "worker": (n >> 17) & 0x1F,
                    "process": (n >> 12) & 0x1F,
                    "sequence": n & 0xFFF,
                },
            }
        )
    return out or None
