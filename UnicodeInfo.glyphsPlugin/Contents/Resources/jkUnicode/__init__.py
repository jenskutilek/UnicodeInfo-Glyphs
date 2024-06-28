from __future__ import annotations

from functools import cached_property
from jkUnicode.aglfn import getGlyphnameForUnicode
from jkUnicode.uniBlock import get_block
from jkUnicode.uniCase import uniLowerCaseMapping, uniUpperCaseMapping
from jkUnicode.uniCat import uniCat
from jkUnicode.uniDecomposition import uniDecompositionMapping
from jkUnicode.uniName import uniName
from jkUnicode.uniNiceName import nice_name_rules
from jkUnicode.uniScript import get_script

from typing import List, Optional, Tuple


categoryName = {
    "Lu": "Letter, Uppercase",
    "Ll": "Letter, Lowercase",
    "Lt": "Letter, Titlecase",
    "Lm": "Letter, Modifier",
    "Lo": "Letter, Other",
    "Mn": "Mark, Nonspacing",
    "Mc": "Mark, Spacing Combining",
    "Me": "Mark, Enclosing",
    "Nd": "Number, Decimal Digit",
    "Nl": "Number, Letter",
    "No": "Number, Other",
    "Pc": "Punctuation, Connector",
    "Pd": "Punctuation, Dash",
    "Ps": "Punctuation, Open",
    "Pe": "Punctuation, Close",
    "Pi": "Punctuation, Initial quote (may behave like Ps or Pe depending on usage)",
    "Pf": "Punctuation, Final quote (may behave like Ps or Pe depending on usage)",
    "Po": "Punctuation, Other",
    "Sm": "Symbol, Math",
    "Sc": "Symbol, Currency",
    "Sk": "Symbol, Modifier",
    "So": "Symbol, Other",
    "Zs": "Separator, Space",
    "Zl": "Separator, Line",
    "Zp": "Separator, Paragraph",
    "Cc": "Other, Control",
    "Cf": "Other, Format",
    "Cs": "Other, Surrogate",
    "Co": "Other, Private Use",
    "Cn": "Other, Not Assigned",
}


def get_expanded_glyph_list(
    unicodes: List[int], ui: Optional["UniInfo"] = None
) -> List[Tuple[int, Optional[str]]]:
    """ "Expand" or annotate a list of codepoints.

    For codepoints that have a case mapping (UC or LC), the target codepoint of
    the case mapping will be added to the list. AGLFN glyph names are added to
    the list too, so the returned list contains tuples of `(codepoint,
    glyphname)`, sorted by the codepoint value.

    :param unicodes: A list of codepoints
    :type unicodes: list

    :param  ui: The UniInfo instance to use. If None, one will be instantiated.
    :type  ui: UniInfo"""
    glyphs = []
    if ui is None:
        ui = UniInfo(0)
    for ch in unicodes:
        ui.unicode = ch
        glyphs.append((ch, ui.glyphname))
        if ui.lc_mapping is not None:
            ui.unicode = ui.lc_mapping
            glyphs.append((ui.unicode, ui.glyphname))
        elif ui.uc_mapping is not None:
            ui.unicode = ui.uc_mapping
            glyphs.append((ui.unicode, ui.glyphname))
    return sorted(list(set(glyphs)))


def getUnicodeChar(code: int) -> str:
    """Return the Unicode character for a Unicode codepoint.

    :param code: The codepoint
    :type code: int"""
    return chr(code)


class UniInfo:
    """The main Unicode Info object. It gets its Unicode information from the
    submodules aglfn, uniCase, uniCat, uniDecomposition, uniName, and
    uniRangesBits which are generated from the official Unicode data. You can
    find tools to download and regenerate the data in the `tools` subfolder.
    """

    def __init__(self, uni: Optional[int] = None) -> None:
        """The Unicode Info object is meant to be instantiated once and then
        reused to get information about different codepoints. Avoid to
        instantiate it often, because it is rather expensive.

        Initialize the Info object with a None e.g. before a loop and then in
        the loop assign the actual codepoints that you want information about by
        setting the `unicode` instance variable. This will automatically update
        the other instance variables with the correct information from the
        Unicode standard.

        :param uni: The codepoint.
        :type uni: int"""
        self._unicode = None
        if uni is not None:
            self.unicode = uni

    @property
    def unicode(self) -> Optional[int]:
        """The Unicode codepoint. Setting this value will look up and fill the
        other pieces of information, like category, range, decomposition
        mapping, and case mapping."""
        return self._unicode

    @unicode.setter
    def unicode(self, value: Optional[int]):
        if value == self._unicode:
            return

        self._unicode = value

        # Invalidate cached properties
        for attr in (
            "block",
            "category",
            "category_short",
            "decomposition_mapping",
            "glyphname",
            "lc_mapping",
            "name",
            "nice_name",
            "script",
            "uc_mapping",
        ):
            try:
                delattr(self, attr)
            except AttributeError:
                pass

        if self._unicode is None:
            self.category_short = "<undefined>"
            self.category = "<undefined>"
            self.decomposition_mapping = []

    def __repr__(self) -> str:
        if self.unicode is None:
            s = "      Unicode: None"
        else:
            s = "      Unicode: 0x%04X (dec. %s)" % (
                self.unicode,
                self.unicode,
            )
        s += "\n         Name: %s" % self.name
        s += "\n     Category: %s (%s)" % (self.category_short, self.category)
        if self.uc_mapping:
            s += "\n    Uppercase: 0x%04X" % self.uc_mapping
        if self.lc_mapping:
            s += "\n    Lowercase: 0x%04X" % self.lc_mapping
        if self.decomposition_mapping:
            s += "\nDecomposition: %s" % (
                " ".join(["0x%04X" % m for m in self.decomposition_mapping])
            )
        return s

    @cached_property
    def block(self) -> Optional[str]:
        """The name of the block for the current codepoint."""
        return get_block(self._unicode)

    @cached_property
    def category(self) -> Optional[str]:
        """The name of the category for the current codepoint."""
        if self._unicode is None:
            return None

        if self.category_short is None:
            return "<undefined>"

        return categoryName.get(self.category_short, "<undefined>")

    @cached_property
    def category_short(self) -> Optional[str]:
        """The short name of the category for the current codepoint."""
        if self._unicode is None:
            return None

        return uniCat.get(self._unicode, "<undefined>")

    @property
    def char(self) -> Optional[str]:
        """The character for the current codepoint."""
        if self.unicode is None:
            return None

        return getUnicodeChar(self.unicode)

    @char.setter
    def char(self, value: Optional[str]) -> None:
        if value is None:
            self.unicode = None
        else:
            self.unicode = ord(value)

    @cached_property
    def glyphname(self) -> Optional[str]:
        """The AGLFN glyph name for the current codepoint."""

        return getGlyphnameForUnicode(self.unicode)

    @cached_property
    def name(self) -> Optional[str]:
        """The Unicode name for the current codepoint."""
        if self._unicode is None:
            return None

        name = uniName.get(self._unicode, None)
        # TODO: Add nicer names based on original Unicode names?
        if name is None:
            if 0xE000 <= self._unicode < 0xF8FF:
                return "<Private Use>"
            if 0xD800 <= self._unicode < 0xDB7F:
                return "<Non Private Use High Surrogate #%i>" % (
                    self._unicode - 0xD8000
                )
            if 0xDB80 <= self._unicode < 0xDBFF:
                return "<Private Use High Surrogate #%i>" % (
                    self._unicode - 0xDB80
                )
            if 0xDC00 <= self._unicode < 0xDFFF:
                return "<Low Surrogate #%i>" % (self._unicode - 0xDC00)
            return "<undefined>"
        return name

    @cached_property
    def nice_name(self) -> Optional[str]:
        """A more human-readable Unicode name for the current codepoint."""
        if self.name is None:
            return None

        for transform_function in nice_name_rules:
            result = transform_function(self.name)
            if result:
                return result

        return self.name.capitalize()

    @cached_property
    def decomposition_mapping(self) -> List[int]:
        """The decomposition mapping for the current codepoint."""
        if self._unicode is None:
            return []

        try:
            dc = uniDecompositionMapping[self._unicode]
        except KeyError:
            dc = []
        return dc

    @cached_property
    def lc_mapping(self) -> Optional[int]:
        """The lowercase mapping for the current codepoint."""
        if self._unicode is None:
            return None

        return uniLowerCaseMapping.get(self._unicode, None)

    @cached_property
    def uc_mapping(self) -> Optional[int]:
        """The uppercase mapping for the current codepoint."""
        if self._unicode is None:
            return None

        return uniUpperCaseMapping.get(self._unicode, None)

    @cached_property
    def script(self) -> Optional[str]:
        if self._unicode is None:
            return None

        return get_script(self._unicode)
