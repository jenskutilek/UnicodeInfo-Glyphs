#!/usr/bin/env python3

import argparse
from jkUnicode import UniInfo


def get_codepoint_from_str(s):
    """
    Convert different Unicode codepoint representations to int, e.g.
       U+1E9E
       0x1E9E
    """
    sl = s.lower()
    if sl.startswith("0x"):
        return int(sl[2:], 16)
    elif sl.startswith("u+"):
        return int(sl[2:], 16)
    else:
        return int(sl)


def uniinfo():
    parser = argparse.ArgumentParser(
        description="Show information about Unicode codepoints."
    )
    parser.add_argument(
        "codepoint", type=str, nargs="+", help="One or more Unicode codepoints"
    )

    args = parser.parse_args()
    ui = UniInfo()
    for uni in args.codepoint:
        i = get_codepoint_from_str(uni)
        ui.unicode = i
        print(ui)
        print()


if __name__ == "__main__":
    uniinfo()
