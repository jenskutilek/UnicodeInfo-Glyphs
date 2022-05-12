import jkUnicode.tools.helpers
from jkUnicode.uniBlockData import uniBlocks

uniBlockToName = jkUnicode.tools.helpers.RangeDict(uniBlocks)

# The reverse mapping of names to blocks
uniNameToBlock = {}
for k, v in uniBlockToName.items():
    if v not in uniNameToBlock:
        uniNameToBlock[v] = k
    else:
        print("ERROR: Duplicate block name: %s" % v)


def get_block(codepoint):
    try:
        return uniBlockToName[codepoint]
    except KeyError:
        return None


def get_codepoints_min_max(block_name):
    try:
        return uniNameToBlock[block_name]
    except KeyError:
        return None


def get_codepoints(block_name):
    try:
        low, high = uniNameToBlock[block_name]
        return range(low, high + 1)
    except KeyError:
        return []


if __name__ == "__main__":
    print(get_block(0x4ff))
    print(get_block(0x500))
    print(get_codepoints_min_max("Cyrillic Supplement"))
    print(get_codepoints("Cyrillic Supplement"))
