from __future__ import annotations

from re import compile
from .aglfnData import nameToUnicode

# Build reverse dictionary
unicodeToName = {value: key for key, value in nameToUnicode.items()}


def getUnicodeForGlyphname(name: str) -> int | None:
    """Return the Unicode value as integer or None that is assigned to the
    specified glyph name. It handles AGLFN names, uniXXXX names, uXXXXX names,
    ligature names, variant names, and PUA-encoded ornament names (orn001 -
    orn999, starting at 0xEA01).

    :param name: The glyph name.
    :type name: str"""
    ornName = compile("^orn[0-9]{3}$")
    length = len(name)
    if "_" in name:
        return None
    elif "." in name[1:]:
        return None
    elif name in nameToUnicode.keys():
        return nameToUnicode[name]
    elif length == 7 and name.startswith("uni"):
        return int(name[3:], 16)
    elif length == 6 and name.startswith("u"):
        try:
            return int(name[1:], 16)
        except ValueError:
            return None
    elif ornName.match(name):
        return 0xEA00 + int(name[3:6])
    else:
        return None


def getGlyphnameForUnicode(code: int | None) -> str | None:
    """Return the name as string or None that is assigned to the specified
    Unicode value.

    :param code: The codepoint.
    :type code: int"""
    if code is None:
        return None
    elif code in unicodeToName.keys():
        return unicodeToName[code]
    elif code < 0xFFFF:
        return "uni%04X" % code
    else:
        return "u%05X" % code
