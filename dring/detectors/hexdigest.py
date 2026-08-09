"""Hash digest — classifies hex strings by length (MD5/SHA-1/SHA-256/SHA-512)."""

import re

NAME = "hexdigest"
_RE = re.compile(r"^[0-9a-fA-F]+$")
_LENGTHS = {
    32: "MD5",
    40: "SHA-1 (or a git object id)",
    56: "SHA-224",
    64: "SHA-256",
    96: "SHA-384",
    128: "SHA-512",
}


def detect(s):
    s = s.strip()
    if not _RE.match(s) or len(s) not in _LENGTHS:
        return None
    algo = _LENGTHS[len(s)]
    return {
        "type": NAME,
        "confidence": 0.5,
        "summary": f"{algo} digest ({len(s) * 4} bits)",
        "details": {"algorithm": algo, "bits": len(s) * 4},
    }
