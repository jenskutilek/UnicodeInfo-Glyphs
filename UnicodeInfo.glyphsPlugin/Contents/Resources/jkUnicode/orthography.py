#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import weakref
from pickle import dump, load
from time import time
from jkUnicode import UniInfo
from jkUnicode.tools.jsonhelpers import dict_from_file


# These unicode points are ignored when scanning for orthography support
IGNORED_UNICODES = [
    # Minute and second appear in lots of language definitions in CLDR, but are
    # not in very many fonts.
    0x2032,  # minute
    0x2033,  # second
]


ui = UniInfo(0)


def cased(codepoint_list):
    """
    Return a list with its Unicode case mapping toggled. If a codepoint has
    no lowercase or uppercase mapping, it is dropped from the list.

    :param codepoint_list: The list of integer codepoints.
    :type codepoint_list: list
    """
    result = []
    for c in codepoint_list:
        ui.unicode = c
        if ui.lc_mapping:
            result.append(ui.lc_mapping)
        elif ui.uc_mapping:
            result.append(ui.uc_mapping)
    return list(set(result))


class Orthography(object):
    """
    The Orthography object represents an orthography. You usually don't deal
    with this object directly, it is used internally by the
    :py:class:`jkUnicode.orthography.OrthographyInfo` object.

    :param info_obj: The parent info object.
    :type info_obj: :py:class:`jkUnicode.orthography.OrthographyInfo`

    :param code: The orthography code.
    :type code: str

    :param script: The script code of the orthography.
    :type script: str

    :param territory: The territory code of the orthography.
    :type territory: str

    :param info_dict: The dictionary which contains the rest of the information
                      about the orthography.
    :type info_dict: dict
    """

    def __init__(self, info_obj, code, script, territory, info_dict):
        self._info = weakref.ref(info_obj)
        self.code = code
        self.script = script
        self.territory = territory
        self.from_dict(info_dict)
        self.forget_cmap()

    def from_dict(self, info_dict):
        """
        Read information for the current orthography from a dictionary. This
        method is called during initialization of the object and fills in a
        number of instance attributes:

name
   The orthography name.

unicodes_base
   The set of base characters for the orthography.

unicodes_optional
   The set of optional characters for the orthography.

unicodes_punctuation
   The set of punctuation characters for the orthography.

unicodes_any
   The previous three sets combined.
        """
        self.name = info_dict.get("name", None)
        uni_info = info_dict.get("unicodes", {})

        # Add the unicode points, and also the cased variants of the unicode
        # points of each category.
        u_list = uni_info.get("base", [])
        self.unicodes_base = (
            set(u_list + cased(u_list)) - self.info.ignored_unicodes
        )

        u_list = uni_info.get("optional", [])
        self.unicodes_optional = (
            set(u_list + cased(u_list))
            - self.unicodes_base
            - self.info.ignored_unicodes
        )

        u_list = uni_info.get("punctuation", [])
        self.unicodes_punctuation = (
            set(u_list + cased(u_list)) - self.info.ignored_unicodes
        )

        # Additional sets to speed up later calculations
        self.unicodes_base_punctuation = (
            self.unicodes_base | self.unicodes_punctuation
        )
        self.unicodes_any = (
            self.unicodes_base
            | self.unicodes_optional
            | self.unicodes_punctuation
        )

        self.scan_ok = False

    def fill_from_default_orthography(self):
        """
        Sometimes the base unicodes are empty for a variant of an orthography.
        Try to fill them in from the default variant.

        Call this only after the whole list of orthographies is present, or it
        will fail, because the default orthography may not be present until the
        whole list has been built.
        """
        if self.territory != "dflt":
            # print(self.code, self.script, self.territory)
            parent = self.info.orthography(self.code, self.script)
            if parent is None:
                print(
                    "WARNING: No parent orthography found for %s/%s/%s"
                    % (self.code, self.script, self.territory)
                )
            else:
                # print("    Parent:", parent.code, parent.script, parent.territory)
                # Set attributes from parent (there may be empty attributes
                # remaining ...?)
                for attr in [
                    "unicodes_base",
                    "unicodes_optional",
                    "unicodes_punctuation",
                ]:
                    if getattr(self, attr) == set():
                        parent_set = getattr(parent, attr)
                        if parent_set:
                            # print("    Filled from parent:", attr)
                            setattr(self, attr, parent_set)

    @property
    def support_full(self):
        """
        Is the orthography supported (base, optional and punctuation
        characters) for the current parent cmap?
        """
        if (
            self.num_missing_base == 0
            and self.num_missing_optional == 0
            and self.num_missing_punctuation == 0
        ):
            return True
        return False

    @property
    def support_basic(self):
        """
        Is the orthography supported (base and punctuation characters) for the
        current parent cmap?
        """
        if self.num_missing_base == 0 and self.num_missing_punctuation == 0:
            return True
        return False

    @property
    def support_minimal(self):
        """
        Is the orthography supported (base characters) for the current parent
        cmap?
        """
        if (
            self.num_missing_base == 0
            and self.num_missing_optional != 0
            and self.num_missing_punctuation != 0
        ):
            return True
        return False

    @property
    def support_minimal_inclusive(self):
        """
        Is the orthography supported (base characters only) for the current
        parent cmap?
        """
        if self.num_missing_base == 0:
            return True
        return False

    def almost_supported_full(self, max_missing=5):
        """
        Is the orthography supported with a maximum of max_missing characters
        (base, optional and punctuation characters) for the current parent
        cmap?
        """
        if 0 < self.num_missing_all <= max_missing:
            return True
        return False

    def almost_supported_basic(self, max_missing=5):
        """
        Is the orthography supported with a maximum of max_missing base
        characters for the current parent cmap?
        """
        if 0 < self.num_missing_base <= max_missing:
            return True
        return False

    def almost_supported_punctuation(self, max_missing=5):
        """
        Is the orthography supported with a maximum of max_missing punctuation
        characters for the current parent cmap?
        """
        if (
            self.num_missing_base == 0
            and 0 < self.num_missing_punctuation <= max_missing
        ):
            return True
        return False

    def uses_unicode_base(self, u):
        """
        Is the unicode used by this orthography in the base set? This is
        relatively slow. Use
        :py:func:`jkUnicode.orthography.OrthographyInfo.build_reverse_cmap` if
        you need to access this information more often.

        :param u: The codepoint.
        :type u: int
        """
        if u in self.unicodes_base_punctuation:
            return True
        return False

    def uses_unicode_any(self, u):
        """
        Is the unicode used by this orthography in any set? This is relatively
        slow. Use
        :py:func:`jkUnicode.orthography.OrthographyInfo.build_reverse_cmap` if
        you need to access this information more often.

        :param u: The codepoint.
        :type u: int
        """
        if u in self.unicodes_any:
            return True
        return False

    def scan_cmap(self):
        """
        Scan the orthography against the current parent cmap. This fills in a
        number of instance attributes:

        missing_base
           A set of unicode values that are missing from the basic characters
           of the orthography.

        missing_optional
           A set of unicode values that are missing from the optional
           characters of the orthography.

        missing_punctuation
           A set of unicode values that are missing from the punctuation
           characters of the orthography.

        missing_all
           A set of all the previous combined.

        num_missing_base, num_missing_optional, num_missing_punctuation,
        num_missing_all
           The number of missing characters for the previous attributes

        base_pc, optional_pc, punctuation_pc
           The percentage values of support for the categories basic, optional,
           and punctuation characters.

        The names of these attributes can be used in
        :py:class:`jkUnicode.orthography.OrthographyInfo.print_report`.
        """
        cmap_set = set(self.info.cmap)
        # Check for missing chars
        self.missing_base = self.unicodes_base - cmap_set
        self.missing_optional = self.unicodes_optional - cmap_set
        self.missing_punctuation = self.unicodes_punctuation - cmap_set
        self.missing_all = (
            self.missing_base
            | self.missing_optional
            | self.missing_punctuation
        )

        self.num_missing_base = len(self.missing_base)
        self.num_missing_optional = len(self.missing_optional)
        self.num_missing_punctuation = len(self.missing_punctuation)
        self.num_missing_all = len(self.missing_all)

        # Calculate percentage
        self.base_pc = (
            1 - self.num_missing_base / len(self.unicodes_base)
            if self.unicodes_base
            else 0
        )
        self.optional_pc = (
            1 - self.num_missing_optional / len(self.unicodes_optional)
            if self.unicodes_optional
            else 0
        )
        self.punctuation_pc = (
            1 - self.num_missing_punctuation / len(self.unicodes_punctuation)
            if self.unicodes_punctuation
            else 0
        )

        self.scan_ok = True

    def forget_cmap(self):
        """
        Forget the results of the last cmap scan.
        """
        self.missing_base = {}
        self.missing_optional = {}
        self.missing_punctuation = {}
        self.missing_all = {}

        self.num_missing_base = 0
        self.num_missing_optional = 0
        self.num_missing_punctuation = 0
        self.num_missing_all = 0

        # Calculate percentage
        self.base_pc = 0
        self.optional_pc = 0
        self.punctuation_pc = 0
        self.scan_ok = False

    @property
    def info(self):
        """
        The parent OrthographyInfo object (read-only).
        """
        # self._info is a weakref, call it to return its object
        return self._info()

    @property
    def id(self):
        _id = self.code
        if self.script != "DFLT":
            _id += "_%s" % self.script
        if self.territory != "dflt":
            _id += "_%s" % self.territory
        return _id

    @property
    def name(self):
        """
        The name of the orthography (read-only).
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __gt__(self, other):
        if self.name > other.name:
            return True
        return False

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __lt__(self, other):
        if self.name < other.name:
            return True
        return False

    def __ne__(self, other):
        if self.name == other.name:
            return False
        return True

    def __repr__(self):
        return '<Orthography "%s">' % self.name.encode(
            "ascii", errors="ignore"
        )


class OrthographyInfo(object):
    """
    The main Orthography Info object. It reads the information for each
    orthography from the files in the `json` subfolder. The JSON data is
    generated from the Unicode CLDR data via included Python scripts.

    This object is expensive to instantiate due to disk access, so it is
    recommended to instantiate it once and then reuse it.
    """

    def __init__(self):
        data_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "json"
        )
        pickled_path = os.path.join(data_path, "language_characters.pickle")
        if os.path.exists(pickled_path):
            print("Unpickling language data...")
            start = time()
            with open(pickled_path, "rb") as f:
                master = load(f)
            stop = time()
            print(f"...done in {stop - start}s.")
        else:
            print("Loading JSON language data...")
            start = time()
            master = dict_from_file(data_path, "language_characters")
            stop = time()
            print(f"...done in {stop - start}s.")
            with open(pickled_path, "wb") as f:
                dump(master, f)

        self.ignored_unicodes = set(IGNORED_UNICODES)
        self.orthographies = []
        self._index = {}
        i = 0
        for code, script_dict in master.items():
            # print(code, script_dict)
            for script, territory_dict in script_dict.items():
                # print(script, territory_dict)
                for territory, info in territory_dict.items():
                    # print(territory, info)
                    self.orthographies.append(
                        Orthography(self, code, script, territory, info)
                    )
                    self._index[(code, script, territory)] = i
                    i += 1
        for o in self.orthographies:
            o.fill_from_default_orthography()

        self._language_names = dict_from_file(data_path, "languages")
        self._script_names = dict_from_file(data_path, "scripts")
        self._territory_names = dict_from_file(data_path, "territories")

        self._cmap = None
        self._reverse_cmap = None

    @property
    def cmap(self):
        """
        The unicode to glyph name mapping, a dictionary. When you set the cmap,
        it is scanned against all orthographies belonging to the Orthography
        Info object.
        """
        if self._cmap is None:
            return {}
        return self._cmap

    @cmap.setter
    def cmap(self, value=None):
        if value is None:
            self._cmap = None
            for o in self.orthographies:
                o.forget_cmap()
        else:
            self._cmap = value
            for o in self.orthographies:
                o.scan_cmap()

    def build_reverse_cmap(self):
        """
        Build a map from each unicode to a list of indices into the
        orthographies list for all orthographies that are using it as base or
        punctuation character.
        """
        self._reverse_cmap = {}
        for i, o in enumerate(self.orthographies):
            for u in o.unicodes_base_punctuation:
                if u in self._reverse_cmap:
                    self._reverse_cmap[u].append(i)
                else:
                    self._reverse_cmap[u] = [i]

    def orthography(self, code, script="DFLT", territory="dflt"):
        """
        Access a particular orthography by its language, script and territory
        code.

        :param code: The language code.
        :type code: str
        :param script: The script code.
        :type script: str
        :param territory: The territory code.
        :type territory: str
        """
        i = self._index.get((code, script, territory), None)
        if i is None:
            return None
        return self.orthographies[i]

    def get_orthographies_for_char(self, char):
        """
        Get a list of orthographies which use a supplied character at base
        level.

        :param char: The character.
        :type char: char
        """
        if not self._reverse_cmap:
            self.build_reverse_cmap()
        ol = self._reverse_cmap.get(ord(char), [])
        return [self.orthographies[i] for i in ol]

    def get_orthographies_for_unicode(self, u):
        """
        Get a list of orthographies which use a supplied codepoint at base
        level.

        :param u: The codepoint.
        :type u: int
        """
        if not self._reverse_cmap:
            self.build_reverse_cmap()
        ol = self._reverse_cmap.get(u, [])
        return [self.orthographies[i] for i in ol]

    def get_orthographies_for_unicode_any(self, u):
        """
        Get a list of orthographies which use a supplied codepoint at any
        level.

        :param u: The codepoint.
        :type u: int
        """
        return [o for o in self.orthographies if o.uses_unicode_any(u)]

    # Nice names for language, script, territory

    def get_language_name(self, code):
        """
        Return the nice name for a language by its code.

        :param code: The language code.
        :type code: str
        """
        return self._language_names.get(code, code)

    def get_script_name(self, code="DFLT"):
        """
        Return the nice name for a script by its code.

        :param code: The script code.
        :type code: str
        """
        if code == "DFLT":
            return "Default"
        else:
            return self._script_names.get(code, code)

    def get_territory_name(self, code="dflt"):
        """
        Return the nice name for a territory by its code.

        :param code: The territory code.
        :type code: str
        """
        if code == "dflt":
            return "Default"
        else:
            return self._territory_names.get(code, code)

    # Convenience functions

    def get_supported_orthographies(self, full_only=False):
        """
        Get a list of supported orthographies for a character list.

        :param full_only: Return only orthographies which have both basic and
                          optional characters present for the current cmap.
        :type full_only: bool
        """
        if full_only:
            return [o for o in self.orthographies if o.support_full()]
        return [o for o in self.orthographies if o.support_basic()]

    def get_supported_orthographies_minimum_inclusive(self):
        """
        Get a list of orthographies with minimal or better support for the
        current cmap.
        """
        return [o for o in self.orthographies if o.support_minimal_inclusive()]

    def get_supported_orthographies_minimum(self):
        """
        Get a list of orthographies with minimal support for the current cmap
        only.
        """
        return [o for o in self.orthographies if o.support_minimal()]

    def get_almost_supported(self, max_missing=5):
        """
        Return a list of almost supported orthographies for the current cmap.

        :param max_missing: The maximum allowed number of missing characters.
        :type max_missing: int
        """
        return [
            o
            for o in self.orthographies
            if o.almost_supported_basic(max_missing)
        ]

    def get_almost_supported_punctuation(self):
        return [
            o for o in self.orthographies if o.almost_supported_punctuation()
        ]

    def __len__(self):
        """
        Return the number of known orthographies.
        """
        return len(self.orthographies)

    def __repr__(self):
        return "<OrthographyInfo with %i orthographies>" % len(self)

    # Very convenient convenience functions

    def print_report(self, otlist, attr):
        """
        Print a formatted report for a given list of orthographies.

        :param otlist: The list of orthographies.
        :type otlist: list

        :param attr: The name of the attribute of the orthography object that
                     will be shown in the report (missing_base,
                     missing_optional, missing_punctuation, missing_all,
                     num_missing_base, num_missing_optional,
                     num_missing_punctuation, base_pc, optional_pc,
                     punctuation_pc, unicodes_base, unicodes_optional,
                     unicodes_punctuation).
        :type attr: str
        """
        otlist.sort()
        for ot in otlist:
            print("\n%s" % ot.name)
            for u in sorted(list(getattr(ot, attr))):
                ui.unicode = u
                print(
                    "    0x%04X\t%s\t%s" % (u, ui.glyphname, ui.name.title())
                )

    def report_supported_minimum_inclusive(self):
        """
        Print a report of minimally supported orthographies for the current
        cmap (no punctuation, no optional characters required).
        """
        m = self.get_supported_orthographies_minimum_inclusive()
        print(
            "The font has minimal or better support for %i orthographies:"
            % len(m)
        )
        m.sort()
        for ot in m:
            print(ot.name)

    def report_supported_minimum(self):
        """
        Print a report of minimally supported orthographies for the current
        cmap (no punctuation, no optional characters present).
        """
        m = self.get_supported_orthographies_minimum()
        print("The font has minimal support for %i orthographies:" % len(m))
        m.sort()
        for ot in m:
            print(ot.name)

    def report_supported(self, full_only=False):
        """
        Print a report of supported orthographies for the current cmap.

        :param full_only: Only report orthographies which have both basic and
            optional characters present
        :type full_only: bool
        """
        m = self.get_supported_orthographies(full_only)
        print("The font supports %i orthographies:" % len(m))
        m.sort()
        for ot in m:
            print(ot.name)

    def report_missing_punctuation(self):
        """
        Print a report of orthographies which have all basic letters present,
        but are missing puncuation characters.
        """
        m = self.get_almost_supported_punctuation()
        print(
            "Orthographies which can be supported by adding punctuation characters:"
        )
        self.print_report(m, "missing_punctuation")

    def report_near_misses(self, n=5):
        """
        Print a report of orthographies which a maximum number of n characters
        missing.
        """
        m = self.get_almost_supported(n)
        print(
            "Orthographies which can be supported with max. %i additional %s:"
            % (n, "character" if n == 1 else "characters")
        )
        self.print_report(m, "missing_base")

    def report_kill_list(self):
        """
        Print a list of character pairs that do not appear in any supported
        orthography for the current cmap.
        """
        import itertools

        m = self.get_supported_orthographies_minimum_inclusive()
        possible_pairs = set()
        for ot in m:
            unicodes = ot.unicodes_base  # | ot.unicodes_optional
            ot_pairs = set(
                itertools.combinations_with_replacement(unicodes, 2)
            )
            print(
                f"{ot.name}: {len(unicodes)} characters, "
                f"{len(ot_pairs)} possible combinations"
            )
            possible_pairs |= ot_pairs
        # for L, R in sorted(list(possible_pairs)):
        #     print("%s%s" % (chr(L), chr(R)))
        print(possible_pairs)


# Test functions

def test_scan():
    from time import time
    from fontTools.ttLib import TTFont

    font_path = "/Users/jens/Documents/Schriften/Hertz/Hertz-Book.ttf"

    print("Scanning font for orthographic support:")
    print(font_path)

    # Get a character map from a font to scan.
    cmap = TTFont(font_path).getBestCmap()
    start = time()
    o = OrthographyInfo()
    print(o)

    # List known orthographies
    for ot in sorted(o.orthographies):
        print(ot.name, ot.code)

    o.cmap = cmap

    # Scan for full, base and minimal support of the font's cmap
    full = o.get_supported_orthographies(full_only=True)
    base = o.get_supported_orthographies(full_only=False)
    mini = o.get_supported_orthographies_minimum()
    stop = time()

    print(
        "\nFull support:",
        len(full),
        "orthography" if len(base) == 1 else "orthographies",
    )
    print(", ".join([x.name for x in full]))

    base = [r for r in base if r not in full]
    print(
        "\nBasic support:",
        len(base),
        "orthography" if len(base) == 1 else "orthographies",
    )
    print(", ".join([x.name for x in base]))

    mini = [r for r in mini if r not in full]
    print(
        "\nMinimal support (no punctuation):",
        len(mini),
        "orthography" if len(mini) == 1 else "orthographies",
    )
    print(", ".join([x.name for x in mini]))

    # Timing information
    print(stop - start)

    # Output info about one orthography
    ot = o.orthography("en", "DFLT", "ZA")
    print("\nOrthography:", ot.name)
    print(list(ot.unicodes_base))

    # Scan the font again, but allow for a number of missing characters
    print
    n = 3
    o.report_near_misses(n)


def test_reverse():
    from time import time

    print("\nTest of the Reverse CMAP functions")

    c = "ö"
    o = OrthographyInfo()

    print("\nBuild reverse CMAP:",)
    start = time()
    o.build_reverse_cmap()
    stop = time()
    d = (stop - start) * 1000
    print("%0.2f ms" % d)

    u = ord(c)

    start = time()
    result1 = o.get_orthographies_for_unicode(u)
    stop = time()
    d = (stop - start) * 1000
    print("Use cached lookup:  %0.2f ms" % d)

    start = time()
    result2 = o.get_orthographies_for_unicode_any(u)
    stop = time()
    d = (stop - start) * 1000
    print("Use uncached lookup: %0.2f ms" % d)

    print("'%s' is used in:" % c)
    for ot in sorted(result1):
        print("   ", ot.name)


if __name__ == "__main__":
    test_scan()
    test_reverse()
