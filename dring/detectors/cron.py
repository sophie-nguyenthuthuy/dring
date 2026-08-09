"""Cron expression — validates 5/6 fields (+@aliases), renders a description."""

import re

NAME = "cron"

_FIELDS5 = [
    ("minute", 0, 59, None),
    ("hour", 0, 23, None),
    ("day-of-month", 1, 31, None),
    ("month", 1, 12, {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}),
    ("day-of-week", 0, 7, {"SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4,
                           "FRI": 5, "SAT": 6}),
]
_ALIASES = {
    "@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *", "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0", "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}
_PART = re.compile(r"(\*|\d+|\d+-\d+)(?:/(\d+))?$")


def _part_ok(part, lo, hi, names):
    part = part.upper()
    for nm, val in (names or {}).items():
        part = part.replace(nm, str(val))
    m = _PART.match(part)
    if not m:
        return False
    rng, step = m.groups()
    if step is not None and int(step) == 0:
        return False
    if rng == "*":
        return True
    if "-" in rng:
        a, b = map(int, rng.split("-"))
        return lo <= a <= b <= hi
    return lo <= int(rng) <= hi


def _desc(expr):
    if expr == "*":
        return "any"
    if expr.startswith("*/"):
        return f"every {expr[2:]}"
    return expr


def detect(s):
    s = s.strip()
    alias = None
    if s.lower() in _ALIASES:
        alias, s = s, _ALIASES[s.lower()]
    parts = s.split()
    if len(parts) == 6:
        fields = [("second", 0, 59, None)] + _FIELDS5
    elif len(parts) == 5:
        fields = _FIELDS5
    else:
        return None
    details = {}
    for expr, (name, lo, hi, names) in zip(parts, fields):
        if not all(p and _part_ok(p, lo, hi, names) for p in expr.split(",")):
            return None
        details[name] = f"{expr} ({_desc(expr)})"
    minute, rest = parts[-5], parts[-4:]
    if rest == ["*"] * 4 and minute.startswith("*/"):
        human = f"every {minute[2:]} minutes"
    elif parts == ["*"] * len(parts):
        human = "every minute"
    else:
        human = "schedule (see fields)"
    summary = f"cron expression: {human}" + (f" (alias {alias})" if alias else "")
    return {"type": NAME, "confidence": 0.85, "summary": summary, "details": details}
