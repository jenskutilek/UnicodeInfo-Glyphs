from jkUnicode.uniBlock import get_block
from jkUnicode.uniNiceName import nice_name_rules
from jkUnicode.uniCat import uniCat
from jkUnicode.uniCase import uniUpperCaseMapping, uniLowerCaseMapping
from jkUnicode.uniDecomposition import uniDecompositionMapping
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
        instantiate it often, because it is rather expensive on disk access.

        Initialize the Info object with a dummy codepoint or None e.g. before a
        loop and then in the loop assign the actual codepoints that you want
        information about by setting the `unicode` instance variable. This will
        automatically update the other instance variables with the correct
        information from the Unicode standard.

        :param uni: The codepoint.
        :type uni: int"""
        self._load_uni_name()
        self.unicode: Optional[int] = uni


    def _load_uni_name(self, file_name: str = "uni_names") -> None:
        """Import uniName from JSON or from Python"""
        # Loading the data from JSON is not faster than importing a python
        # module. Skip the optimization.
        from jkUnicode.uniName import uniName

        self.uniName = uniName
        # from jkUnicode.tools.jsonhelpers import (
        #     dict_from_file,
        #     json_path,
        #     json_to_file
        # )
        # from time import time
        # try:
        #     start = time()
        #     self.uniName = {
        #         int(k): v
        #         for k, v in dict_from_file(json_path, file_name).items()
        #     }
        #     stop = time()
        #     print(f"Loaded Unicode Name data from JSON in {stop - start} s.")
        # except FileNotFoundError:
        #     start = time()
        #     from jkUnicode.uniName import uniName
        #     self.uniName = uniName
        #     stop = time()
        #     print(f"Converted Unicode Name data to JSON in {stop - start} s.")
        #     json_to_file(json_path, file_name, self.uniName)

    @property
    def unicode(self) -> Optional[int]:
        """The Unicode codepoint. Setting this value will look up and fill the
        other pieces of information, like category, range, decomposition
        mapping, and case mapping."""
        return self._unicode

    @unicode.setter
    def unicode(self, value: Optional[int]):
        self._unicode = value
        # Set some properties to None
        # Those are expensive to compute, we do it only when asked to.
        self._ublock: Optional[str] = None
        self._script: Optional[str] = None
        self._name: Optional[str] = None
        self._categoryShort: Optional[str] = None
        self._category: Optional[str] = None
        self._uc_mapping: Optional[int] = None
        self._lc_mapping: Optional[int] = None
        self._dc_mapping: Optional[List[int]] = None
    
        if self._unicode is None:
            self._categoryShort = "<undefined>"
            self._category = "<undefined>"
            self._dc_mapping = []

    def __repr__(self) -> str:
        if self.unicode is None:
            s = "      Unicode: None"
        else:
            s = "      Unicode: 0x%04X (dec. %s)" % (
                self.unicode,
                self.unicode,
            )
        s += "\n         Name: %s" % self.name
        s += "\n     Category: %s (%s)" % (self._categoryShort, self.category)
        if self._uc_mapping:
            s += "\n    Uppercase: 0x%04X" % self._uc_mapping
        if self._lc_mapping:
            s += "\n    Lowercase: 0x%04X" % self._lc_mapping
        if self._dc_mapping:
            s += "\nDecomposition: %s" % (
                " ".join(["0x%04X" % m for m in self._dc_mapping])
            )
        return s

    @property
    def block(self) -> Optional[str]:
        """The name of the block for the current codepoint."""
        if self._ublock is None:
            self._ublock = get_block(self._unicode)
        return self._ublock

    @property
    def category(self) -> Optional[str]:
        """The name of the category for the current codepoint."""
        if self._unicode is None:
            return None

        if self._category is None:
            cs = self.category_short
            if cs is None:
                self._category = "<undefined>"
            else:
                self._category = categoryName.get(
                    cs, "<undefined>"
                )
        return self._category

    @property
    def category_short(self) -> Optional[str]:
        """The short name of the category for the current codepoint."""
        if self._unicode is None:
            return None

        if self._categoryShort is None:
            self._categoryShort = uniCat.get(self._unicode, "<undefined>")
        return self._categoryShort

    @property
    def char(self) -> Optional[str]:
        """The character for the current codepoint."""
        if self.unicode is None:
            return None

        return getUnicodeChar(self.unicode)

    @property
    def glyphname(self) -> Optional[str]:
        """The AGLFN glyph name for the current codepoint."""
        from jkUnicode.aglfn import getGlyphnameForUnicode

        return getGlyphnameForUnicode(self.unicode)

    @property
    def name(self) -> Optional[str]:
        """The Unicode name for the current codepoint."""
        if self._unicode is None:
            return None

        if self._name is None:
            self._name = self.uniName.get(self._unicode, None)
            # TODO: Add nicer names based on original Unicode names?
            if self._name is None:
                if 0xE000 <= self._unicode < 0xF8FF:
                    self._name = "<Private Use>"
                elif 0xD800 <= self._unicode < 0xDB7F:
                    self._name = "<Non Private Use High Surrogate #%i>" % (
                        self._unicode - 0xD8000
                    )
                elif 0xDB80 <= self._unicode < 0xDBFF:
                    self._name = "<Private Use High Surrogate #%i>" % (
                        self._unicode - 0xDB80
                    )
                elif 0xDC00 <= self._unicode < 0xDFFF:
                    self._name = "<Low Surrogate #%i>" % (
                        self._unicode - 0xDC00
                    )
                else:
                    self._name = "<undefined>"
        return self._name

    @property
    def nice_name(self) -> Optional[str]:
        """A more human-readable Unicode name for the current codepoint."""
        if self._name is None:
            return None

        for transform_function in nice_name_rules:
            result = transform_function(self._name)
            if result:
                return result

        return self._name.capitalize()

    @property
    def decomposition_mapping(self) -> List[int]:
        """The decomposition mapping for the current codepoint."""
        if self._dc_mapping is None:
            if self._unicode is not None:
                try:
                    if self._unicode is not None:
                        self._dc_mapping = uniDecompositionMapping[self._unicode]
                except KeyError:
                    self._dc_mapping = []
            else:
                self._dc_mapping = []
        return self._dc_mapping

    @property
    def lc_mapping(self) -> Optional[int]:
        """The lowercase mapping for the current codepoint."""
        if self._unicode is None:
            return None

        if self._lc_mapping is None:
            self._lc_mapping = uniLowerCaseMapping.get(self._unicode, None)
        return self._lc_mapping

    @property
    def uc_mapping(self) -> Optional[int]:
        """The uppercase mapping for the current codepoint."""
        if self._unicode is None:
            return None

        if self._uc_mapping is None:
            self._uc_mapping = uniUpperCaseMapping.get(self._unicode, None)
        return self._uc_mapping

    @property
    def script(self) -> Optional[str]:
        if self._script is None:
            self._script = get_script(self._unicode)
        return self._script


if __name__ == "__main__":
    print("\n*** Test of jkUnicode.UniInfo ***")
    for u in [9912, 80, 0x1E40]:
        j = UniInfo(u)
        print("Repr.:")
        print(j)
        print("- " * 20)
        print("             Name:", j.name)
        print("       Glyph Name:", j.glyphname)
        print("         Category:", j.category)
        print("           Script:", j.script)
        print(
            "    Decomposition:",
            " ".join([hex(n) for n in j.decomposition_mapping]),
        )
        print("        Character:", j.char)
        lc = j.lc_mapping
        print("Lowercase Mapping:", lc)
        if lc is not None:
            j.unicode = lc
            print(j)
        print("-" * 40)
