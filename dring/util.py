"""Shared helpers for detectors."""

import base64
import datetime
import re

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def b64url_decode(s: str) -> bytes:
    """Decode base64url with or without padding."""
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def iso_from_s(seconds: float) -> str | None:
    """Epoch seconds -> ISO-8601 UTC string (ms precision when non-zero)."""
    try:
        dt = datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    out = dt.strftime("%Y-%m-%dT%H:%M:%S")
    if dt.microsecond:
        out += f".{dt.microsecond // 1000:03d}"
    return out + "Z"


def iso_from_ms(ms: float) -> str | None:
    return iso_from_s(ms / 1000)


def hex_to_bytes(s: str) -> bytes | None:
    """Parse a hex dump ("89504E47", "0x1f 8b", "de:ad:be:ef") into bytes.

    Dashes are deliberately NOT stripped so UUIDs never look like hex dumps.
    """
    t = re.sub(r"[\s:,]", "", s.strip())
    if t.lower().startswith("0x"):
        t = t[2:]
    if len(t) < 2 or len(t) % 2:
        return None
    if not re.fullmatch(r"[0-9a-fA-F]+", t):
        return None
    return bytes.fromhex(t)


def plausible_epoch(seconds: float, lo_year=1980, hi_year=2100) -> bool:
    iso = iso_from_s(seconds)
    return iso is not None and lo_year <= int(iso[:4]) <= hi_year
