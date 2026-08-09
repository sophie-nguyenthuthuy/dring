"""dring command-line interface."""

import argparse
import json
import sys

from . import DETECTORS, __version__, identify


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="dring",
        description="a decoder ring for opaque strings — paste anything, find out what it is",
    )
    p.add_argument("text", nargs="*", help="the opaque string (reads stdin if omitted or '-')")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--all", action="store_true", help="show every candidate, not just the top 3")
    p.add_argument("--list", action="store_true", help="list registered detectors")
    p.add_argument("--version", action="version", version=f"dring {__version__}")
    a = p.parse_args(argv)

    if a.list:
        for mod in DETECTORS:
            doc = (mod.__doc__ or "").strip().splitlines()
            print(f"{mod.NAME:<12} {doc[0] if doc else ''}")
        return 0

    if a.text and a.text != ["-"]:
        text = " ".join(a.text)
    else:
        text = sys.stdin.read()

    cands = identify(text)

    if a.json:
        print(json.dumps(cands, indent=2, ensure_ascii=False, default=str))
        return 0 if cands else 1

    if not cands:
        print(f"no idea — ran {len(DETECTORS)} detectors, none matched.")
        print("(add one: a detector is one file + one fixture, see README)")
        return 1

    shown = cands if a.all else cands[:3]
    for i, c in enumerate(shown, 1):
        print(f"{i}. {c['type']:<12} {int(c['confidence'] * 100):>3}%  {c['summary']}")
        for k, v in (c.get("details") or {}).items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False, default=str)
            print(f"     {k}: {v}")
    if not a.all and len(cands) > len(shown):
        print(f"(+{len(cands) - len(shown)} more candidates, use --all)")
    return 0
