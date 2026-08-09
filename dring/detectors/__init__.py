"""Detector package. One module per detector.

Contract — a detector module defines:

    NAME = "mytype"                      # matches its fixture dir name
    def detect(text: str) -> dict | list[dict] | None:
        # return None if not a match, else candidate(s):
        # {"type": NAME, "confidence": 0.0-1.0, "summary": str, "details": dict}

Detectors must be stdlib-only, offline, and never raise on weird input
(the registry swallows exceptions, but be polite).
"""
