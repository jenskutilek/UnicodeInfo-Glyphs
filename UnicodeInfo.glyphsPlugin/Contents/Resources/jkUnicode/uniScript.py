import jkUnicode.tools.helpers
from jkUnicode.uniScriptData import uniScripts

uniScriptToName = jkUnicode.tools.helpers.RangeDict(uniScripts)


def get_script(codepoint: int) -> str:
    try:
        return uniScriptToName[codepoint]
    except KeyError:
        return "Unknown"


if __name__ == "__main__":
    print(get_script(0x4FF))
    print(get_script(0x500))
