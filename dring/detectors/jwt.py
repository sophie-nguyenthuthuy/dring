"""JSON Web Token — decodes header + claims, humanizes exp/iat/nbf."""

import json
import re

from ..util import b64url_decode, iso_from_s

NAME = "jwt"
_RE = re.compile(r"^[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*$")


def detect(s):
    s = s.strip()
    if not _RE.match(s):
        return None
    h, p, sig = s.split(".")
    try:
        header = json.loads(b64url_decode(h))
        claims = json.loads(b64url_decode(p))
    except Exception:
        return None
    if not isinstance(header, dict) or "alg" not in header:
        return None
    details = {"alg": header["alg"]}
    if header.get("typ"):
        details["typ"] = header["typ"]
    if header.get("kid"):
        details["kid"] = header["kid"]
    details["claims"] = claims
    if isinstance(claims, dict):
        for k in ("iat", "nbf", "exp"):
            if isinstance(claims.get(k), (int, float)):
                details[f"{k}_human"] = iso_from_s(claims[k])
    summary = f"JWT signed with {header['alg']}"
    if isinstance(claims, dict) and claims.get("sub"):
        summary += f", sub={claims['sub']}"
    conf = 0.98 if sig else 0.9  # unsigned (alg=none style) is a bit fishier
    return {"type": NAME, "confidence": conf, "summary": summary, "details": details}
