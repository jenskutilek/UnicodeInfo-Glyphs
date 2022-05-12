from re import compile
from .aglfnData import nameToUnicode

# Build reverse dictionary
unicodeToName = {value: key for key, value in nameToUnicode.items()}


def getUnicodeForGlyphname(name):
    """Return the Unicode value as integer or None that is assigned to the
    specified glyph name. It handles AGLFN names, uniXXXX names, uXXXXX names,
    ligature names, variant names, and PUA-encoded ornament names (orn001 -
    orn999, starting at 0xEA01).

    :param name: The glyph name.
    :type name: str"""
    ornName = compile("^orn[0-9]{3}$")
    if "_" in name:
        return None
    elif "." in name[1:]:
        return None
    elif name in nameToUnicode.keys():
        return nameToUnicode[name]
    elif name[0:3] == "uni" and len(name) == 7:
        return int(name[3:], 16)
    elif name[0] == "u" and len(name) == 6:
        try:
            return int(name[1:], 16)
        except:
            return None
    elif ornName.match(name):
        return 0xea00 + int(name[3:6])
    else:
        return None


def getGlyphnameForUnicode(code):
    """Return the name as string or None that is assigned to the specified
    Unicode value.

    :param code: The codepoint.
    :type code: int"""
    if code is None:
        return None
    elif code in unicodeToName.keys():
        return unicodeToName[code]
    elif code < 0xffff:
        return "uni%04X" % code
    else:
        return "u%05X" % code
