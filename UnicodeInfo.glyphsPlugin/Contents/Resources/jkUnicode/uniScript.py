import jkUnicode.tools.helpers
from jkUnicode.uniScriptData import uniScripts

uniScriptToName = jkUnicode.tools.helpers.RangeDict(uniScripts)


def get_script(codepoint):
    try:
        return uniScriptToName[codepoint]
    except KeyError:
        return None


if __name__ == "__main__":
    print(get_script(0x4ff))
    print(get_script(0x500))
