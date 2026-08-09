"""Unix timestamp — seconds/millis/micros/nanos, sanity-checked to 1980-2100."""

import re

from ..util import iso_from_s, plausible_epoch

NAME = "unixtime"
_RE = re.compile(r"^\d{9,19}$")
_SCALES = [("seconds", 1), ("milliseconds", 1e3), ("microseconds", 1e6), ("nanoseconds", 1e9)]


def detect(s):
    s = s.strip()
    if not _RE.match(s):
        return None
    n = int(s)
    out = []
    for unit, div in _SCALES:
        sec = n / div
        if not plausible_epoch(sec):
            continue
        iso = iso_from_s(sec)
        out.append(
            {
                "type": NAME,
                "confidence": 0.65 if unit == "seconds" else 0.6,
                "summary": f"unix timestamp ({unit}): {iso}",
                "details": {"unit": unit, "utc": iso},
            }
        )
    return out or None
