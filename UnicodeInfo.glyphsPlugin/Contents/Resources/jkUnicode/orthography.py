import os

from jkUnicode import UniInfo
from jkUnicode.tools.jsonhelpers import dict_from_file

from typing import Any, Dict, List, Optional, Set


# These codepoints are ignored when scanning for orthography support
IGNORED_UNICODES = [
    # Minute and second appear in lots of language definitions in CLDR, but are
    # not in very many fonts.
    0x2011,  # non-breaking hyphen
    0x2032,  # minute
    0x2033,  # second
]


class Orthography:
    """
    The Orthography object represents an orthography. You usually don't deal
    with this object directly, it is used internally by the
    :py:class:`jkUnicode.orthography.OrthographyInfo` object.

    :param info_obj: The parent info object.
    :type info_obj: :py:class:`jkUnicode.orthography.OrthographyInfo`

    :param code: The ISO-639-1 code for the orthography.
    :type code: str

    :param script: The script code of the orthography.
    :type script: str

    :param territory: The territory code of the orthography.
    :type territory: str

    :param info_dict: The dictionary which contains the rest of the information
                      about the orthography.
    :type info_dict: dict
    """

    def __init__(
        self,
        info_obj: Optional[Any],
        code: str,
        script: str,
        territory: str,
        info_dict: Dict[str, Any],
    ) -> None:
        self._info = info_obj
        if self._info is None:
            self._ui = UniInfo()
        else:
            self._ui = self._info.ui
        self.code = code
        self.script = script
        self.territory = territory
        self._name = "<Unknown>"
        self.unicodes_any: Set[int] = set()
        self.unicodes_base: Set[int] = set()
        self.unicodes_optional: Set[int] = set()
        self.unicodes_punctuation: Set[int] = set()
        self.unicodes_base_punctuation: Set[int] = set()
        self.scan_ok = False
        self.from_dict(info_dict)
        self.forget_cmap()

    def from_dict(self, info_dict: Dict[str, Any]) -> None:
        """
        Read information for the current orthography from a dictionary. This
        method is called during initialization of the object and fills in a
        number of instance attributes:

        `name`: The orthography name.

        `unicodes_base`: The set of base characters for the orthography.

        `unicodes_optional`: The set of optional characters for the orthography.

        `unicodes_punctuation`: The set of punctuation characters for the
        orthography.

        `unicodes_any`: The previous three sets combined.
        """
        self.scan_ok = False

        try:
            self.name = info_dict["name"]
        except KeyError:
            pass

        try:
            uni_info: Dict[str, List] = info_dict["unicodes"]
        except KeyError:
            print(f"WARNING: No Unicode info found for language {self.name}")
            return

        # Add the unicode points, and also the cased variants of the unicode
        # points of each category.
        try:
            u_list: List[int] = uni_info["base"]
        except KeyError:
            u_list = []
        self.unicodes_base = (
            set(u_list + self.cased(u_list)) - self.ignored_unicodes
        )

        try:
            u_list = uni_info["optional"]
        except KeyError:
            u_list = []
        self.unicodes_optional = (
            set(u_list + self.cased(u_list))
            - self.unicodes_base
            - self.ignored_unicodes
        )

        try:
            u_list = uni_info["punctuation"]
        except KeyError:
            u_list = []
        self.unicodes_punctuation = (
            set(u_list + self.cased(u_list)) - self.ignored_unicodes
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

    @property
    def ui(self) -> UniInfo:
        """
        The :py:class:`jkUnicode.UniInfo` object that is queried for Unicode
        information.
        """
        return self._ui
    
    @property
    def ignored_unicodes(self) -> Set[int]:
        """
        The set of ignored codepoints. If a parent
        :py:class:`jkUnicode.orthography.OrthographyInfo` object exists, it is
        taken from there.
        """
        if self.info is None:
            return set()
        return self.info.ignored_unicodes


    def cased(
        self, codepoint_list: List[int]
    ) -> List[int]:
        """
        Return a list with its Unicode case mapping toggled. If a codepoint has
        no lowercase or uppercase mapping, it is dropped from the list.

        :param codepoint_list: The list of codepoints.
        :type codepoint_list: list
        """
        result = set()
        for c in codepoint_list:
            self.ui.unicode = c
            if self.ui.lc_mapping:
                result.add(self.ui.lc_mapping)
            elif self.ui.uc_mapping:
                result.add(self.ui.uc_mapping)
        return sorted(list(result))

    def fill_from_default_orthography(self) -> None:
        """
        Sometimes the base codepoints are empty for a variant of an
        orthography. Try to fill them in from the default variant.

        Call this only after the whole list of orthographies is present, or it
        will fail, because the default orthography may not be present until the
        whole list has been built.
        """
        if self.territory != "dflt":
            if self.info is None:
                print(
                    "WARNING: No parent orthography found for %s/%s/%s"
                    % (self.code, self.script, self.territory)
                )
                return

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
    def support_full(self) -> bool:
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
    def support_basic(self) -> bool:
        """
        Is the orthography supported (base and punctuation characters) for the
        current parent cmap?
        """
        if self.num_missing_base == 0 and self.num_missing_punctuation == 0:
            return True
        return False

    @property
    def support_minimal(self) -> bool:
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
    def support_minimal_inclusive(self) -> bool:
        """
        Is the orthography supported (base characters only) for the current
        parent cmap?
        """
        if self.num_missing_base == 0:
            return True
        return False

    def almost_supported_full(self, max_missing: int = 5) -> bool:
        """
        Is the orthography supported with a maximum of `max_missing` characters
        (base, optional and punctuation characters) for the current parent
        cmap?
        """
        if 0 < self.num_missing_all <= max_missing:
            return True
        return False

    def almost_supported_basic(self, max_missing: int = 5) -> bool:
        """
        Is the orthography supported with a maximum of `max_missing` base
        characters for the current parent cmap?
        """
        if 0 < self.num_missing_base <= max_missing:
            return True
        return False

    def almost_supported_punctuation(self, max_missing: int = 5) -> bool:
        """
        Is the orthography supported with a maximum of `max_missing`
        punctuation characters for the current parent cmap?
        """
        if (
            self.num_missing_base == 0
            and 0 < self.num_missing_punctuation <= max_missing
        ):
            return True
        return False

    def uses_unicode_base(self, u: int) -> bool:
        """
        Is the codepoint used by this orthography in the base set? This is
        relatively slow. Use
        :py:func:`jkUnicode.orthography.OrthographyInfo.build_reverse_cmap` if
        you need to access this information more often.

        :param u: The codepoint.
        :type u: int
        """
        if u in self.unicodes_base_punctuation:
            return True
        return False

    def uses_unicode_any(self, u: int) -> bool:
        """
        Is the codepoint used by this orthography in any set? This is
        relatively slow. Use
        :py:func:`jkUnicode.orthography.OrthographyInfo.build_reverse_cmap` if
        you need to access this information more often.

        :param u: The codepoint.
        :type u: int
        """
        if u in self.unicodes_any:
            return True
        return False

    def scan_cmap(self) -> None:
        """
        Scan the orthography against the current parent cmap. This fills in a
        number of instance attributes:

        `missing_base`: A set of unicode values that are missing from the basic
        characters of the orthography.

        `missing_optional`: A set of unicode values that are missing from the
        optional characters of the orthography.

        `missing_punctuation`: A set of unicode values that are missing from
        the punctuation characters of the orthography.

        `missing_all`: A set of all the previous combined.

        `num_missing_base, num_missing_optional, num_missing_punctuation,
        num_missing_all`: The number of missing characters for the previous
        attributes

        `base_pc, optional_pc, punctuation_pc`: The percentage values of
        support for the categories basic, optional, and punctuation characters.

        The names of these attributes can be used in
        :py:class:`jkUnicode.orthography.OrthographyInfo.print_report`.
        """
        if self.info is None:
            cmap_set = set()
        else:
            cmap_set = self.info.codepoints
        # Check for missing chars
        self.missing_base = self.unicodes_base - cmap_set
        self.missing_optional = self.unicodes_optional - cmap_set
        self.missing_punctuation = self.unicodes_punctuation - cmap_set
        self.missing_all = (
            self.missing_base
            | self.missing_optional
            | self.missing_punctuation
        )

        self.num_missing_base: int = len(self.missing_base)
        self.num_missing_optional: int = len(self.missing_optional)
        self.num_missing_punctuation: int = len(self.missing_punctuation)
        self.num_missing_all: int = len(self.missing_all)

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

    def forget_cmap(self) -> None:
        """
        Forget the results of the last cmap scan.
        """
        self.missing_base = set()
        self.missing_optional = set()
        self.missing_punctuation = set()
        self.missing_all = set()

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
    def info(self) -> Optional["OrthographyInfo"]:
        """
        The parent :py:class:`jkUnicode.orthography.OrthographyInfo` object
        (read-only).
        """
        # self._info is a weakref, call it to return its object
        # return self._info()
        return self._info

    @property
    def identifier(self) -> str:
        """
        Return an identifier for language code/script/territory (read-only).
        """
        _id = self.code
        if self.script != "DFLT":
            _id += "_%s" % self.script
        if self.territory != "dflt":
            _id += "_%s" % self.territory
        return _id

    @property
    def name(self) -> str:
        """
        The name of the orthography.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def __gt__(self, other) -> bool:
        if self.name > other.name:
            return True
        return False

    def __eq__(self, other) -> bool:
        if self.name == other.name:
            return True
        return False

    def __lt__(self, other) -> bool:
        if self.name < other.name:
            return True
        return False

    def __ne__(self, other) -> bool:
        if self.name == other.name:
            return False
        return True

    def __repr__(self) -> str:
        return f'<Orthography "{self.name}">'


class OrthographyInfo:
    """
    The main Orthography Info object. It reads the information for each
    orthography from the files in the `json` subfolder. The JSON data is
    generated from the Unicode CLDR data via included Python scripts.

    This object is expensive to instantiate due to disk access, so it is
    recommended to instantiate it once and then reuse it.
    """

    def __init__(self, ui: Optional[UniInfo] = None) -> None:
        # We need a UniInfo object
        if ui is None:
            self.ui = UniInfo()
        else:
            self.ui = ui

        data_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "json"
        )
        master = dict_from_file(data_path, "language_characters")
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

        self._cmap: Dict[int, str] = {}
        self._codepoints: Set[int] = set()
        self._reverse_cmap: Dict[int, List[int]] = {}

    @property
    def cmap(self) -> Dict[int, str]:
        """
        The codepoint to glyph name mapping. When you set the cmap, it is
        scanned against all orthographies belonging to the OrthographyInfo
        object.

        You set the cmap by passing a dictionary, usually from a font. E.g.:

        TTFont("myfont.ttf")
        o = OrthographyInfo()
        o.cmap = TTFont("myfont.ttf").getBestCmap()
        """
        return self._cmap

    @cmap.setter
    def cmap(self, value: Optional[Dict[int, str]] = None) -> None:
        if value is None:
            self._cmap = dict()
            self._codepoints = set()
            for o in self.orthographies:
                o.forget_cmap()
        else:
            self._cmap = value
            self._codepoints = set(value.keys())
            for o in self.orthographies:
                o.scan_cmap()
    
    @property
    def codepoints(self) -> Set[int]:
        return self._codepoints

    def build_reverse_cmap(self) -> None:
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

    def orthography(self, code: str, script: str = "DFLT", territory: str = "dflt") -> Optional[Orthography]:
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

    def get_orthographies_for_char(self, char: str) -> List[Optional[Orthography]]:
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

    def get_orthographies_for_unicode(self, u: int) -> List[Optional[Orthography]]:
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

    def get_orthographies_for_unicode_any(self, u: int) -> List[Orthography]:
        """
        Get a list of orthographies which use a supplied codepoint at any
        level.

        :param u: The codepoint.
        :type u: int
        """
        return [o for o in self.orthographies if o.uses_unicode_any(u)]

    # Nice names for language, script, territory

    def get_language_name(self, code: str) -> str:
        """
        Return the nice name for a language by its code.

        :param code: The language code.
        :type code: str
        """
        return self._language_names.get(code, code)

    def get_script_name(self, code: str = "DFLT") -> str:
        """
        Return the nice name for a script by its code.

        :param code: The script code.
        :type code: str
        """
        if code == "DFLT":
            return "Default"
        else:
            return self._script_names.get(code, code)

    def get_territory_name(self, code: str = "dflt") -> str:
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

    def get_supported_orthographies(self, full_only: bool = False) -> List[Orthography]:
        """
        Get a list of supported orthographies for a character list.

        :param full_only: Return only orthographies which have both basic and
                          optional characters present for the current cmap.
        :type full_only: bool
        """
        if full_only:
            return [o for o in self.orthographies if o.support_full]
        return [o for o in self.orthographies if o.support_basic]

    def get_supported_orthographies_minimum_inclusive(self) -> List[Orthography]:
        """
        Get a list of orthographies with minimal or better support for the
        current cmap.
        """
        return [o for o in self.orthographies if o.support_minimal_inclusive]

    def get_supported_orthographies_minimum(self) -> List[Orthography]:
        """
        Get a list of orthographies with minimal support for the current cmap
        only.
        """
        return [o for o in self.orthographies if o.support_minimal]

    def get_almost_supported(self, max_missing: int = 5) -> List[Orthography]:
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

    def get_almost_supported_punctuation(self) -> List[Orthography]:
        return [
            o for o in self.orthographies if o.almost_supported_punctuation()
        ]

    def __len__(self) -> int:
        """
        Return the number of known orthographies.
        """
        return len(self.orthographies)

    def __repr__(self) -> str:
        return "<OrthographyInfo with %i orthographies>" % len(self)

    # Very convenient convenience functions

    def print_report(self, otlist: List[Orthography], attr: str) -> None:
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
                self.ui.unicode = u
                print(
                    "    0x%04X\t%s\t%s" % (
                        u, self.ui.glyphname, self.ui.nice_name
                    )
                )

    def report_supported_minimum_inclusive(self) -> None:
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

    def report_supported_minimum(self) -> None:
        """
        Print a report of minimally supported orthographies for the current
        cmap (no punctuation, no optional characters present).
        """
        m = self.get_supported_orthographies_minimum()
        print("The font has minimal support for %i orthographies:" % len(m))
        m.sort()
        for ot in m:
            print(ot.name)

    def report_supported(self, full_only: bool = False) -> None:
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

    def report_missing_punctuation(self) -> None:
        """
        Print a report of orthographies which have all basic letters present,
        but are missing puncuation characters.
        """
        m = self.get_almost_supported_punctuation()
        print(
            "Orthographies which can be supported by adding punctuation characters:"
        )
        self.print_report(m, "missing_punctuation")

    def report_near_misses(self, n: int = 5) -> None:
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

    def report_kill_list(self) -> None:
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


# o = Orthography(
#     info_obj=None,
#     code="COD",
#     script="dflt",
#     territory="DE",
#     info_dict={"name": "MyName"},
# )
# print(o)
