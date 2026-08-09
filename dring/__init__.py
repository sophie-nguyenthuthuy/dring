"""dring — a decoder ring for opaque strings.

Paste anything, find out what it is. Every detector is one module in
``dring/detectors/`` exposing ``NAME`` and ``detect(text)``; this package
auto-discovers them and ranks their candidates by confidence.
"""

import importlib
import pkgutil

from . import detectors as _dpkg

__version__ = "0.1.0"


def _load():
    mods = []
    for m in pkgutil.iter_modules(_dpkg.__path__):
        mod = importlib.import_module(f"{_dpkg.__name__}.{m.name}")
        if hasattr(mod, "detect") and hasattr(mod, "NAME"):
            mods.append(mod)
    return sorted(mods, key=lambda m: m.NAME)


DETECTORS = _load()


def identify(text):
    """Run every detector against *text*, return candidates sorted by confidence.

    Each candidate is ``{"type", "confidence", "summary", "details"}``.
    """
    text = text.strip()
    if not text:
        return []
    out = []
    for mod in DETECTORS:
        try:
            r = mod.detect(text)
        except Exception:  # a broken detector must never take down the ring
            r = None
        if not r:
            continue
        out.extend(r if isinstance(r, list) else [r])
    out.sort(key=lambda c: -c["confidence"])
    return out
