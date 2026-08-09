"""Stack trace — identifies the language and pulls out the error line."""

import re

NAME = "stacktrace"

# (language, signature, frame pattern) — order matters, most specific first
_SIGS = [
    ("Python", re.compile(r"Traceback \(most recent call last\)"),
     re.compile(r'^\s+File "', re.M)),
    ("Go", re.compile(r"^goroutine \d+ \[", re.M),
     re.compile(r"^\S+\(.*\)$", re.M)),
    ("Rust", re.compile(r"thread '[^']*' panicked at"),
     re.compile(r"^\s+\d+: ", re.M)),
    ("Java", re.compile(r"^\s+at [\w.$<>]+\([\w$]+\.(java|kt):\d+\)", re.M),
     re.compile(r"^\s+at ", re.M)),
    ("JavaScript", re.compile(r"^\s+at .+:\d+:\d+\)?$", re.M),
     re.compile(r"^\s+at ", re.M)),
]


def detect(s):
    s = s.strip()
    if "\n" not in s:
        return None
    lines = [ln for ln in s.splitlines() if ln.strip()]
    for lang, sig, frame in _SIGS:
        if not sig.search(s):
            continue
        error = lines[-1].strip() if lang == "Python" else lines[0].strip()
        return {
            "type": NAME,
            "confidence": 0.9,
            "summary": f"{lang} stack trace: {error[:100]}",
            "details": {
                "language": lang,
                "frames": len(frame.findall(s)),
                "error": error[:200],
            },
        }
    return None
