"""Protobuf wire format — walks varint/fixed/length-delimited fields in a hex dump."""

from ..util import hex_to_bytes

NAME = "protobuf"
_MAX_FIELDS = 200


def _varint(b, i):
    shift = v = 0
    for _ in range(10):
        if i >= len(b):
            return None, i
        byte = b[i]
        i += 1
        v |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return v, i
        shift += 7
    return None, i


def parse_wire(b):
    """Parse *b* as protobuf wire format; return field list or None."""
    i = 0
    fields = []
    while i < len(b):
        if len(fields) > _MAX_FIELDS:
            return None
        key, i = _varint(b, i)
        if key is None:
            return None
        fn, wt = key >> 3, key & 7
        if fn == 0 or fn > 536870911:
            return None
        if wt == 0:  # varint
            v, i = _varint(b, i)
            if v is None:
                return None
            fields.append((fn, "varint", v))
        elif wt == 1:  # 64-bit
            if i + 8 > len(b):
                return None
            fields.append((fn, "fixed64", int.from_bytes(b[i : i + 8], "little")))
            i += 8
        elif wt == 2:  # length-delimited
            ln, i = _varint(b, i)
            if ln is None or i + ln > len(b):
                return None
            fields.append((fn, "len", bytes(b[i : i + ln])))
            i += ln
        elif wt == 5:  # 32-bit
            if i + 4 > len(b):
                return None
            fields.append((fn, "fixed32", int.from_bytes(b[i : i + 4], "little")))
            i += 4
        else:
            return None
    return fields or None


def render(fields):
    out = []
    for fn, wt, v in fields:
        if wt == "len":
            try:
                text = v.decode("utf-8")
                if all(ch.isprintable() for ch in text):
                    out.append(f'field {fn} (len {len(v)}) = "{text[:60]}"')
                    continue
            except UnicodeDecodeError:
                pass
            out.append(f"field {fn} (len {len(v)}) = 0x{v[:24].hex()}")
        else:
            out.append(f"field {fn} ({wt}) = {v}")
    return out


def detect(s):
    data = hex_to_bytes(s)
    if data is None or len(data) < 2:
        return None
    fields = parse_wire(data)
    if not fields:
        return None
    return {
        "type": NAME,
        "confidence": 0.65,
        "summary": f"protobuf wire format ({len(fields)} field{'s' if len(fields) != 1 else ''})",
        "details": {"fields": render(fields)},
    }
