from typing import TYPE_CHECKING

from jkUnicode.uniBlock import uniNameToBlock
from jkUnicode.uniName import uniName

if TYPE_CHECKING:
    from collections.abc import Iterable


def block_completeness(block: str, unicodes: "Iterable[int]") -> str:
    """
    Return the Unicode block completeness indicator for the block name and an iterable
    of Unicode codepoints.

    Args:
        block (str): The name of the Unicode block to check.
        unicodes (Iterable[int]): The codepoints, usually taken from a font's cmap.

    Returns:
        str: The indicator; an empty, half-filled, or filled circle.
    """
    low, high = uniNameToBlock[block]
    block_codepoints = {c for c in range(low, high + 1) if c in uniName}
    test_codepoints = {c for c in unicodes if c in uniName}
    intersection = block_codepoints.intersection(test_codepoints)
    if intersection == block_codepoints:
        return "●"
    if len(intersection) == 0:
        return "○"
    return "◑"


def get_extension_map(glyph_names: "Iterable[str]") -> dict[str, set[str]]:
    """
    Return a map of base glyph names to glyph names with extensions for the font.
    """
    d: dict[str, set[str]] = {}
    for glyph_name in glyph_names:
        if "." in glyph_name and not glyph_name.startswith("."):
            base_name, _ = glyph_name.split(".", 1)
            if base_name not in d:
                d[base_name] = {glyph_name}
            else:
                d[base_name].add(glyph_name)
        else:
            if glyph_name not in d:
                d[glyph_name] = set()
    return d


def get_extra_names(
    glyph_names: "Iterable[str]", uni_name_tuples: "Iterable[tuple[int | None, str]]"
) -> set[tuple[int | None, str]]:
    """
    Return a set of glyph names based on `uni_name_tuples` and the glyph names from a
    font, augmented by glyph variants.

    Args:
        glyph_names (Iterable[str]): The glyph names of a font
        uni_name_tuples (Iterable[tuple[int | None, str]]): Tuples of Unicode codepoint
            and glyph name that will be used to determine the additional glyph names

    Returns:
        set[tuple[int | None, str]]: _description_
    """
    ext_map = get_extension_map(glyph_names)
    additions = set(uni_name_tuples)
    for uni, name in uni_name_tuples:
        additions |= {(uni, e) for e in ext_map.get(name, set())}
    return set(additions)
