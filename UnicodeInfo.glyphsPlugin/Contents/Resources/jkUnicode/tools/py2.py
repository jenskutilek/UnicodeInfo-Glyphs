def getUnicodeCharPy2(code):
    if code < 0x10000:
        return unichr(code)
    else:
        return eval("u'\U%08X'" % code)
