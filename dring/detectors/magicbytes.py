"""File magic bytes — matches hex dumps and text prefixes (PNG, PDF, PEM, ELF...)."""

from ..util import hex_to_bytes

NAME = "magicbytes"

# (hex prefix, file type) — longest prefix wins
_MAGICS = [
    ("FD377A585A00", "xz compressed data"),
    ("377ABCAF271C", "7-Zip archive"),
    ("89504E47", "PNG image"),
    ("47494638", "GIF image"),
    ("25504446", "PDF document"),
    ("504B0304", "ZIP archive (also docx/xlsx/jar/apk)"),
    ("7F454C46", "ELF executable"),
    ("CFFAEDFE", "Mach-O 64-bit executable (little-endian)"),
    ("FEEDFACF", "Mach-O 64-bit executable"),
    ("CAFEBABE", "Java class file (or Mach-O fat binary)"),
    ("0061736D", "WebAssembly module"),
    ("53514C69", "SQLite database"),
    ("52617221", "RAR archive"),
    ("4F676753", "Ogg container"),
    ("52494646", "RIFF container (WAV/AVI/WebP)"),
    ("FFD8FF", "JPEG image"),
    ("425A68", "bzip2 compressed data"),
    ("494433", "MP3 audio (ID3 tag)"),
    ("1F8B", "gzip compressed data"),
    ("4D5A", "Windows PE executable (MZ)"),
]
_TEXT_MAGICS = [
    ("-----BEGIN ", "PEM block"),
    ("%PDF-", "PDF document"),
    ("SQLite format 3", "SQLite database"),
    ("{\\rtf", "RTF document"),
    ("#!", "script with a shebang"),
]


def detect(s):
    raw = s.strip()
    for prefix, name in _TEXT_MAGICS:
        if raw.startswith(prefix):
            summary = name
            if name == "PEM block":
                label = raw[len(prefix):].split("-----")[0].strip()
                summary = f"PEM block ({label})" if label else "PEM block"
            return {
                "type": NAME,
                "confidence": 0.9,
                "summary": summary,
                "details": {"matched_prefix": prefix.rstrip()},
            }
    data = hex_to_bytes(raw)
    if data is None:
        return None
    hx = data.hex().upper()
    for prefix, name in _MAGICS:
        if hx.startswith(prefix):
            return {
                "type": NAME,
                "confidence": 0.8,
                "summary": f"{name} (magic {prefix})",
                "details": {"magic": prefix, "bytes_shown": len(data)},
            }
    return None
