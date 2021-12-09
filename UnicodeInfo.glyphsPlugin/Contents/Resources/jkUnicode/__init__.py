#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jkUnicode.uniBlock import get_block
from jkUnicode.uniName import uniName
from jkUnicode.uniNiceName import nice_name_rules
from jkUnicode.uniCat import uniCat
from jkUnicode.uniCase import uniUpperCaseMapping, uniLowerCaseMapping
from jkUnicode.uniDecomposition import uniDecompositionMapping
from jkUnicode.uniScript import get_script

categoryName = {
    'Lu':   'Letter, Uppercase',
    'Ll':   'Letter, Lowercase',
    'Lt':   'Letter, Titlecase',
    'Lm':   'Letter, Modifier',
    'Lo':   'Letter, Other',
    'Mn':   'Mark, Nonspacing',
    'Mc':   'Mark, Spacing Combining',
    'Me':   'Mark, Enclosing',
    'Nd':   'Number, Decimal Digit',
    'Nl':   'Number, Letter',
    'No':   'Number, Other',
    'Pc':   'Punctuation, Connector',
    'Pd':   'Punctuation, Dash',
    'Ps':   'Punctuation, Open',
    'Pe':   'Punctuation, Close',
    'Pi':   'Punctuation, Initial quote (may behave like Ps or Pe depending on usage)',
    'Pf':   'Punctuation, Final quote (may behave like Ps or Pe depending on usage)',
    'Po':   'Punctuation, Other',
    'Sm':   'Symbol, Math',
    'Sc':   'Symbol, Currency',
    'Sk':   'Symbol, Modifier',
    'So':   'Symbol, Other',
    'Zs':   'Separator, Space',
    'Zl':   'Separator, Line',
    'Zp':   'Separator, Paragraph',
    'Cc':   'Other, Control',
    'Cf':   'Other, Format',
    'Cs':   'Other, Surrogate',
    'Co':   'Other, Private Use',
    'Cn':   'Other, Not Assigned',
}


def get_expanded_glyph_list(unicodes, ui=None):
    """"Expand" or annotate a list of unicodes.
    For unicodes that have a case mapping (UC or LC), the target unicode of the
    case mapping will be added to the list. AGLFN glyph names are added to the
    list too, so the returned list contains tuples of (unicode, glyphname),
    sorted by unicode value.

    :param unicodes: A list of unicodes (int)
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


def getUnicodeChar(code):
    """Return the Unicode character for a Unicode number. This supports "high"
    unicodes (> 0xffff) even on 32-bit builds.

    :param code: The codepoint
    :type code: int"""
    from sys import version as sys_version
    if sys_version[0] == '2':
        from jkUnicode.tools.py2 import getUnicodeCharPy2
        return getUnicodeCharPy2(code)
    return chr(code)


class UniInfo(object):
    """The main Unicode Info object. It gets its Unicode information from the
    submodules aglfn, uniCase, uniCat, uniDecomposition, uniName, and
    uniRangesBits which are generated from the official Unicode data. You can
    find tools to download and regenerate the data in the `tools` subfolder.
    """
    def __init__(self, uni=None):
        """The Unicode Info object is meant to be instantiated once and then
        reused to get information about different codepoints. Avoid to
        instantiate it often, because it is expensive on disk access.

        Initialize the Info object with a dummy codepoint or None e.g. before a
        loop and then in the loop assign the actual codepoints that you want
        information about by setting the `unicode` instance variable. This will
        automatically update the other instance variables with the correct
        information from the Unicode standard.

        :param uni: The codepoint.
        :type uni: int"""
        self.unicode = uni
        self._load_uni_name()

    def _load_uni_name(self, file_name="uni_names"):
        """
        Import uniName from JSON or from Python
        """
        from jkUnicode.tools.jsonhelpers import (
            dict_from_file,
            json_path,
            json_to_file
        )
        from time import time
        try:
            start = time()
            self.uniName = {
                int(k): v
                for k, v in dict_from_file(json_path, file_name).items()
            }
            stop = time()
            print(f"Loaded Unicode Name data from JSON in {stop - start} s.")
        except FileNotFoundError:
            start = time()
            from jkUnicode.uniName import uniName
            self.uniName = uniName
            json_to_file(json_path, file_name, self.uniName)
            stop = time()
            print(f"Converted Unicode Name data to JSON in {stop - start} s.")

    @property
    def unicode(self):
        """The Unicode value as integer. Setting this value will look up and
        fill the other pieces of information, like category, range,
        decomposition mapping, and case mapping."""
        return self._unicode

    @unicode.setter
    def unicode(self, value):
        self._unicode = value
        if self._unicode is None:
            self._block = None
            self._name = None
            self._categoryShort = "<undefined>"
            self._category = "<undefined>"
            self._script = None
            self._uc_mapping = None
            self._lc_mapping = None
            self._dc_mapping = []
        else:
            self._block = get_block(self._unicode)
            self._script = get_script(self._unicode)
            self._name = uniName.get(self._unicode, None)
            # TODO: Add nicer names based on original Unicode names?
            if self._name is None:
                if 0xE000 <= self._unicode < 0xF8FF:
                    self._name = "<Private Use>"
                elif 0xD800 <= self._unicode < 0xDB7F:
                    self._name = "<Non Private Use High Surrogate #%i>" % (
                        self._unicode - 0xd8000
                    )
                elif 0xDB80 <= self._unicode < 0xDBFF:
                    self._name = "<Private Use High Surrogate #%i>" % (
                        self._unicode - 0xdb80
                    )
                elif 0xDC00 <= self._unicode < 0xDFFF:
                    self._name = "<Low Surrogate #%i>" % (
                        self._unicode - 0xdc00
                    )
                else:
                    self._name = "<undefined>"
            self._categoryShort = uniCat.get(self._unicode, "<undefined>")
            self._category = categoryName.get(
                self._categoryShort,
                "<undefined>"
            )
            self._uc_mapping = uniUpperCaseMapping.get(self._unicode, None)
            self._lc_mapping = uniLowerCaseMapping.get(self._unicode, None)
            self._dc_mapping = uniDecompositionMapping.get(self._unicode, [])

    def __repr__(self):
        if self.unicode is None:
            s =    "      Unicode: None"
        else:
            s =    "      Unicode: 0x%04X (dec. %s)" % (self.unicode, self.unicode)
        s += "\n         Name: %s" % self.name
        s += "\n     Category: %s (%s)" % (self._categoryShort, self.category)
        if self._uc_mapping:
            s += "\n    Uppercase: 0x%04X" % self._uc_mapping
        if self._lc_mapping:
            s += "\n    Lowercase: 0x%04X" % self._lc_mapping
        if self._dc_mapping:
            s += "\nDecomposition: %s" % (" ".join(["0x%04X" % m for m in self._dc_mapping]))
        return s

    @property
    def block(self):
        return self._block

    @property
    def category(self):
        """The name of the category for the current Unicode value as string."""
        return self._category

    @property
    def category_short(self):
        """The short name of the category for the current Unicode value as
        string."""
        return self._categoryShort

    @property
    def char(self):
        """The character for the current Unicode value."""
        return getUnicodeChar(self.unicode)

    @property
    def glyphname(self):
        """The AGLFN glyph name for the current Unicode value as string."""
        from jkUnicode.aglfn import getGlyphnameForUnicode
        return getGlyphnameForUnicode(self.unicode)

    @property
    def name(self):
        """The Unicode name for the current Unicode value as string."""
        return self._name

    @property
    def nice_name(self):
        """The Unicode name for the current Unicode value as string."""
        for transform_function in nice_name_rules:
            result = transform_function(self._name)
            if result:
                return result
        return self._name.capitalize()

    @property
    def decomposition_mapping(self):
        """The decomposition mapping for the current Unicode value as a list of
        integer codepoints."""
        return self._dc_mapping

    @property
    def lc_mapping(self):
        """The lowercase mapping for the current Unicode value as integer or
        None."""
        return self._lc_mapping

    @property
    def uc_mapping(self):
        """The uppercase mapping for the current Unicode value as integer or
        None."""
        return self._uc_mapping

    @property
    def script(self):
        return self._script


if __name__ == '__main__':
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
        print("    Decomposition:", " ".join(
            [
                hex(n)
                for n in j.decomposition_mapping
            ]
        ))
        print("        Character:", j.char)
        lc = j.lc_mapping
        print("Lowercase Mapping:", lc)
        if lc is not None:
            j.unicode = lc
            print(j)
        print("-" * 40)
