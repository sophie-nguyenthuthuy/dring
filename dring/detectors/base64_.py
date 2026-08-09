"""Base64 — decodes, then classifies the payload (JSON, text, gzip, protobuf...)."""

import json
import re

from ..util import b64url_decode

NAME = "base64"
_STD = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_URL = re.compile(r"^[A-Za-z0-9_-]+={0,2}$")
_HEXISH = re.compile(r"^[0-9a-fA-F]+$")

_MAGICS = [
    (b"\x1f\x8b", "gzip data"),
    (b"\x89PNG", "PNG image"),
    (b"%PDF", "PDF document"),
    (b"PK\x03\x04", "ZIP archive"),
]


def _classify(data):
    from . import protobuf as _pb  # late import: sibling detector, reuse its walker

    for magic, name in _MAGICS:
        if data.startswith(magic):
            return f"base64-encoded {name}", data[:8].hex(), 0.85
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = None
    if text is not None and all(ch.isprintable() or ch in "\n\r\t" for ch in text):
        t = text.strip()
        if t[:1] in "{[":
            try:
                json.loads(t)
                return "base64-encoded JSON", t[:120], 0.85
            except ValueError:
                pass
        return "base64-encoded text", t[:120], 0.75
    fields = _pb.parse_wire(data)
    if fields and len(data) >= 4:
        preview = "; ".join(_pb.render(fields)[:5])
        return f"base64-encoded, decodes as protobuf ({len(fields)} fields)", preview, 0.6
    return f"base64 of {len(data)} bytes of binary", data[:24].hex(), 0.3


def detect(s):
    s = s.strip()
    if len(s) < 8 or any(c in s for c in " \t\n"):
        return None
    is_std = bool(_STD.fullmatch(s)) and len(s) % 4 == 0
    is_url = bool(_URL.fullmatch(s)) and len(s) % 4 != 1
    if not (is_std or is_url):
        return None
    try:
        data = b64url_decode(s.replace("+", "-").replace("/", "_"))
    except Exception:
        return None
    if not data:
        return None
    summary, preview, conf = _classify(data)
    if _HEXISH.fullmatch(s):
        conf *= 0.4  # pure-hex input is far more likely a digest/id than base64
    return {
        "type": NAME,
        "confidence": round(conf, 2),
        "summary": summary,
        "details": {"bytes": len(data), "decoded": preview},
    }
