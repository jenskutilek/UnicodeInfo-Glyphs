import urllib.parse
import webbrowser
from os import environ
from typing import TYPE_CHECKING

import objc
from AppKit import NSBundle, NSClassFromString, NSImage, NSMenuItem
from GlyphsApp import UPDATEINTERFACE, WINDOW_MENU, Glyphs, GSGlyph
from GlyphsApp.plugins import GeneralPlugin
from jkUnicode import UniInfo, get_expanded_glyph_list
from jkUnicode.aglfn import getGlyphnameForUnicode, getUnicodeForGlyphname
from jkUnicode.orthography import OrthographyInfo
from jkUnicode.uniBlock import get_block, get_codepoints, uniNameToBlock
from jkUnicode.uniName import uniName

from unicodeinfowindow import block_completeness, get_extra_names

if TYPE_CHECKING:
    from GlyphsApp import GSFont
    from jkUnicode.orthography import Orthography


def add_glyphs_to_font(glyph_names: list[str], font: "GSFont") -> None:
    existing = set(font.glyphs.keys())
    glyph_list = [
        n for n in glyph_names if n not in existing and not n.startswith("**")
    ]
    font.disableUpdateInterface()
    glyphs = [GSGlyph(n) for n in glyph_list]
    font.glyphs.extend(glyphs)
    font.enableUpdateInterface()
    set_selection(font, glyph_list, deselect=True)


def set_filter(
    font: "GSFont | None" = None, glyph_names: list[str] | None = None
) -> None:
    if font is None:
        return

    if glyph_names is None:
        glyph_names = []
    # https://forum.glyphsapp.com/t/create-list-filter-via-script/2134/7
    GSSortDescriptorNameList = objc.lookUpClass("GSSortDescriptorNameList")
    glyphsArrayController = font.fontView.glyphsArrayController()
    sortDescriptor = GSSortDescriptorNameList.alloc().initWithKey_ascending_(
        "name", True
    )
    sortDescriptor.setReferenceList_(glyph_names)
    glyphsArrayController.setSortDescriptors_([sortDescriptor])
    # FIXME: Missing glyphs for a Unicode block can't be shown by sorting
    #        the font view.


def set_selection(
    font: "GSFont", glyph_names: list[str], deselect: bool = False
) -> None:
    font.disableUpdateInterface()
    if deselect:
        for g in font.glyphs:
            g.selected = False
    for g in glyph_names:
        font.glyphs[g].selected = True
    font.enableUpdateInterface()


def speakers_as_string(speakers: float) -> str:
    if speakers == 0:
        return ""
    # round to two significant decimal digits
    # (from https://stackoverflow.com/a/48812729)
    speakers = int(float(f"{speakers:.2g}"))
    if speakers >= 1000000:
        return f"{speakers / 1000000:g}\u00a0M\u00a0speakers"
    else:
        return f"{speakers:,}\u00a0speakers"


class UnicodeInfo(GeneralPlugin):
    @objc.python_method
    def settings(self) -> None:
        self.hasNotification = False
        self.name = Glyphs.localize({"en": "Unicode Info", "de": "Unicode-Info"})

    def showWindow_(self, sender=None) -> None:
        self._font = None
        self.glyph = None
        self.glyph_name: str | None = None
        self.filtered: bool = False
        self.in_font_view: bool = False
        self.info = UniInfo(0)
        self.unicode: int | None = None
        self.ortho_cdlr = OrthographyInfo(ui=self.info, source="CLDR")
        self.ortho_hyperglot = OrthographyInfo(ui=self.info, source="Hyperglot")
        self.ortho = self.ortho_hyperglot
        self.ortho_list: list[Orthography] = []
        self.case: int | None = None
        self.view = None
        self.selected_orthography: str | None = None
        self.include_optional: bool = False
        self.all_unicodes_in_font: set[int] = set()
        self.blocks_in_popup = [""] + sorted(uniNameToBlock.keys())
        self.build_window(manual_update=True)
        if not self.hasNotification:
            Glyphs.addCallback(self.updateInfo, UPDATEINTERFACE)
        self.hasNotification = True
        self.w.open()
        self.updateInfo()

    @objc.python_method
    def build_window(self, manual_update=False) -> None:
        from vanilla import (
            Button,
            CheckBox,
            FloatingWindow,
            ImageButton,
            PopUpButton,
            TextBox,
        )

        width = 320
        height = 240

        if manual_update:
            # Make room for an additional button
            height += 22

        ini_height = height - 16
        axis = 50

        self.w = FloatingWindow(
            (width, ini_height),
            "Unicode Info",
            minSize=(width, height),
            maxSize=(530, height),
        )
        self.w.bind("close", self.windowClosed)
        y = 10
        self.w.uni_name_label = TextBox(
            (8, y, axis - 10, 20), "Name", sizeStyle="small"
        )
        self.w.uni_name = TextBox((axis, y, -10, 20), "", sizeStyle="small")
        y += 20
        self.w.code_label = TextBox((8, y, axis - 10, 20), "Code", sizeStyle="small")
        self.w.code = TextBox((axis, y, -10, 20), "", sizeStyle="small")
        if hasattr(self, "__file__"):
            path = self.__file__()
            thisBundle = NSBundle.bundleWithPath_(
                path[: path.rfind("Contents/Resources/")]
            )
        else:
            thisBundle = NSBundle.bundleForClass_(NSClassFromString(self.className()))
        wikipedia_icon = NSImage.alloc().initWithContentsOfFile_(
            thisBundle.pathForImageResource_("wikipedia_icon")
        )
        self.w.wiki_character = ImageButton(
            (-94, y - 1.5, 16, 16),
            imageObject=wikipedia_icon,
            callback=self.showWikiCharacter_,
            bordered=False,
            sizeStyle="small",
        )
        self.w.reassign_unicodes = Button(
            (-72, y - 6, -10, 25),
            "Assign all",
            callback=self.reassignUnicodes_,
            sizeStyle="small",
        )
        y += 20
        self.w.glyph_name_label = TextBox(
            (8, y, axis - 10, 20), "Glyph", sizeStyle="small"
        )
        self.w.glyph_name = TextBox((axis, y, -10, 20), "", sizeStyle="small")
        self.w.case = Button(
            (-72, y - 6, -10, 25),
            "\u2191\u2193 Case",
            callback=self.toggleCase_,
            sizeStyle="small",
        )
        y += 20
        self.w.block_label = TextBox((8, y, axis - 10, 20), "Block", sizeStyle="small")
        self.w.block_list = PopUpButton(
            (axis, y - 4, -101, 20),
            [],
            callback=self.selectBlock_WithName_,
            sizeStyle="small",
        )
        self.w.show_block = Button(
            (-72, y - 6, -10, 25),
            "Show",
            callback=self.showBlock_,
            sizeStyle="small",
        )
        y += 24
        self.w.database_label = TextBox(
            (8, y, axis - 5, 20), "Source", sizeStyle="small"
        )
        self.w.database_list = PopUpButton(
            (axis, y - 4, -101, 20),
            ["Hyperglot", "CLDR"],
            callback=self.selectDatabase_,
            sizeStyle="small",
        )
        y += 16
        self.w.include_optional = CheckBox(
            (axis + 4, y, 200, 20),
            "Include optional characters",
            callback=self.includeOptional_,
            sizeStyle="small",
        )
        y += 28
        self.w.orthography_label = TextBox(
            (8, y, axis - 10, 20), "Usage", sizeStyle="small"
        )
        self.w.orthography_list = PopUpButton(
            (axis, y - 4, -101, 20),
            [],
            callback=self.selectOrthography_Index_,
            sizeStyle="small",
        )
        self.w.wiki_orthography = ImageButton(
            (-94, y - 1.5, 16, 16),
            imageObject=wikipedia_icon,
            callback=self.showWikiOrthography_,
            bordered=False,
            sizeStyle="small",
        )
        self.w.show_orthography = Button(
            (-72, y - 6, -10, 25),
            "Show",
            callback=self.showOrthography_,
            sizeStyle="small",
        )
        y += 20
        self.w.speakers_label = TextBox((axis, y, 220, 20), "", sizeStyle="small")
        y += 24
        self.w.speakers_supported_label = TextBox(
            (axis, y, 220, 32), "", sizeStyle="small"
        )
        y += 12

        if manual_update:
            y += 24
            self.w.block_add_missing = Button(
                (axis, y - 6, 72, 25),
                "Fill Block",
                callback=self.addMissingForBlock_,
                sizeStyle="small",
            )
            self.w.orthography_add_missing = Button(
                (axis + 76, y - 6, 72, 25),
                "Fill Orth.",
                callback=self.addMissingForOrthography_,
                sizeStyle="small",
            )
            self.w.reset_filter = Button(
                (-88, y - 6, -10, 25),
                "Reset Filter",
                callback=self.resetFilter_,
                sizeStyle="small",
            )
            # self.w.manual_update = Button(
            #     (-60, y - 6, -10, 25),
            #     "Query",
            #     callback=self.updateInfo_,
            #     sizeStyle="small",
            # )
        block_list_ui_strings = [""]
        for block in self.blocks_in_popup[1:]:
            block_list_ui_strings.append(
                block_completeness(block, self.ortho.cmap.keys()) + " " + block
            )
        self.w.reassign_unicodes.enable(False)
        self.w.block_list.setItems(block_list_ui_strings)
        self.w.show_block.enable(False)
        self.w.case.enable(False)

        if manual_update:
            self.w.block_add_missing.enable(False)
            self.w.orthography_add_missing.enable(False)
            self.w.reset_filter.enable(False)

        # self.w.orthography_list.enable(False)
        self.w.show_orthography.enable(False)
        # if self.font is None:
        #     self.w.include_optional.enable(False)
        # else:
        #     self.w.include_optional.enable(True)

    @objc.python_method
    def start(self) -> None:
        if "GLYPHS_HEADLESS" in environ:
            return

        newMenuItem = NSMenuItem.alloc().init()
        newMenuItem.setTitle_(self.name)
        newMenuItem.setAction_(self.showWindow_)
        newMenuItem.setTarget_(self)
        Glyphs.menu[WINDOW_MENU].append(newMenuItem)

    @objc.python_method
    def __file__(self) -> str:
        """
        Please leave this method unchanged
        """
        return __file__

    @objc.python_method
    def updateInfo(self, sender=None) -> None:
        font = Glyphs.font
        self.font = font
        uni = None
        prev_glyph = self.glyph_name

        # We’re in the Edit View
        if hasattr(font, "currentTab") and font.currentTab:
            self.in_font_view = False
            # Check whether glyph is being edited
            if len(font.selectedLayers) == 1:
                glyph = font.selectedLayers[0].parent
                self.glyph_name = glyph.name
                self.glyph = glyph
                uni = self.get_unicode_for_glyphname(self.glyph_name)
            else:
                self.glyph_name = None
                self.glyph = None

        # We’re in the Font view
        else:
            self.in_font_view = True
            if font and font.parent.windowController() and len(font.selection) == 1:
                glyph = font.selection[0]
                self.glyph_name = glyph.name
                self.glyph = glyph
                uni = self.get_unicode_for_glyphname(self.glyph_name)
            else:
                self.glyph_name = None
                self.glyph = None

        if self.unicode == uni and self.glyph_name == prev_glyph:
            return

        self.unicode = uni
        self._updateInfo(u=self.unicode, fake=False)

    # Properties

    @property
    def font(self) -> "GSFont | None":
        """
        Return the current glyph's font or, as a fallback, the current font.
        """
        if self._font is None:
            if Glyphs.font is None:
                return None
            else:
                self.font = Glyphs.font

        return self._font

    @font.setter
    def font(self, value: "GSFont | None") -> None:
        if self._font == value:
            return

        self._font = value
        if self._font is None:
            self.ortho.cmap = {}
            return

        cmap = set()
        for g in self._font.glyphs:
            if g.unicodes and g.export:
                cmap |= self.glyph_unicodes(g)
        self.ortho.cmap = {u: ".notdef" for u in cmap}

    @property
    def font_fallback(self) -> "GSFont | None":
        if self._font is not None:
            return self._font
        return Glyphs.font

    @property
    def glyph(self) -> GSGlyph | None:
        return self._glyph

    @glyph.setter
    def glyph(self, value: GSGlyph | None) -> None:
        self._glyph = value
        if self._glyph is None:
            self.font = None
        else:
            self.font = self.glyph_font

    @property
    def glyph_font(self) -> "GSFont | None":
        """
        Return the current glyph's font.
        """
        if self._glyph is None:
            return None

        return self._glyph.parent

    @property
    def glyph_unicode(self) -> "int | None":
        """
        Return the current glyph's Unicode value as int or None.
        """
        if self._glyph is None:
            return None
        if self._glyph.unicode is None:
            return None

        return int(self._glyph.unicode, 16)

    # Methods

    @objc.python_method
    def glyph_unicodes(self, glyph) -> set[int]:
        """
        Return a glyph's Unicode values as set of int.
        """
        # Glyphs stores Unicode values as hex string
        return {int(u, 16) for u in glyph.unicodes}

    @objc.python_method
    def glyph_names_for_font(self, font) -> list[str]:
        if font is None:
            return []
        return list(font.glyphs.keys())

    @objc.python_method
    def get_orthography_glyph_list(
        self, orthography: "Orthography", font: "GSFont", add_markers: bool = True
    ) -> list[str]:
        if add_markers:
            glyph_list: list[str | None] = [f"** {orthography.name} **"]
        else:
            glyph_list = []

        glyph_names = font.glyphs.keys()

        base = get_expanded_glyph_list(orthography.unicodes_base, ui=self.info)
        base = get_extra_names(glyph_names, base)
        glyph_list.extend([self.get_glyphname_for_unicode(u) for u, _n in sorted(base)])

        punc = get_expanded_glyph_list(orthography.unicodes_punctuation, ui=self.info)
        punc = get_extra_names(glyph_names, punc)
        if add_markers:
            glyph_list.append("** Punctuation **")
        if punc:
            glyph_list.extend(
                [self.get_glyphname_for_unicode(u) for u, n in sorted(punc)]
            )

        if self.include_optional:
            optn = get_expanded_glyph_list(orthography.unicodes_optional, ui=self.info)
            optn = get_extra_names(glyph_names, optn)
            if add_markers:
                glyph_list.append("** Optional **")
            if optn:
                glyph_list.extend(
                    [
                        self.get_glyphname_for_unicode(u)
                        for u, n in sorted(optn)
                        if self.get_glyphname_for_unicode(u) not in glyph_list
                    ]
                )
        if add_markers:
            glyph_list.extend(["** End **", ".notdef"])
        return [n for n in glyph_list if n is not None]

    @objc.python_method
    def get_glyphname_for_unicode(self, value: int | None = None) -> "str | None":
        if value is None:
            return None

        if self.font is None:
            return None

        if self.font.disablesNiceNames:
            # Use the AGLFN name
            name = getGlyphnameForUnicode(value)
        else:
            # Let Glyphs decide on the name
            g = GSGlyph()
            g.unicode = f"{value:04X}"
            g.updateGlyphInfo(changeName=True)
            name = g.name
            if name == "newGlyph":
                # Something went wrong, e.g. PUA
                if len(g.unicode) == 5:
                    name = f"u{g.unicode}"
                else:
                    name = f"uni{g.unicode}"
        return name

    @objc.python_method
    def get_missing_glyphs_for_block(self, block: str, font: "GSFont") -> list[str]:
        glyph_list = self.get_block_glyph_list(block, font, False, False)
        if font is None:
            return []

        existing = set(font.glyphs.keys())
        return [n for n in glyph_list if n not in existing]

    @objc.python_method
    def get_block_glyph_list(
        self,
        block: str,
        font: "GSFont",
        add_markers: bool = True,
        include_reserved: bool = True,
    ) -> list[str]:
        if add_markers:
            glyph_list = [f"** {block} **"]
        else:
            glyph_list = []
        tuples = [
            (cp, self.get_glyphname_for_unicode(cp))
            for cp in get_codepoints(block)
            if include_reserved or cp in uniName
        ]
        # Filter out entries with None as glyph names
        valid_tuples = [(cp, name) for cp, name in tuples if name is not None]
        uni_name_tuples = get_extra_names(font.glyphs.keys(), valid_tuples)
        glyph_list.extend([n for _, n in sorted(uni_name_tuples)])
        if add_markers:
            glyph_list.extend(["** End **", ".notdef"])
        return [n for n in glyph_list if n is not None]

    @objc.python_method
    def get_unicode_for_glyphname(self, name=None) -> "int | None":
        if name is None:
            return None

        font = self.font_fallback
        if font is None:
            return None

        if font.disablesNiceNames:
            u = getUnicodeForGlyphname(name)
        else:
            g = font.glyphs[name]
            if g is None:
                return None
            glyphInfo = g.glyphInfo
            if glyphInfo is None:
                return None

            u = glyphInfo.unicode
            if u is not None:
                u = int(u, 16)
        return u

    # UI Callbacks

    def toggleCase_(self, sender=None) -> None:
        font = self.font_fallback
        if font is None:
            return
        if self.case is None:
            return

        glyphname = self.get_glyphname_for_unicode(self.case)
        if glyphname is None:
            return

        if hasattr(font, "currentTab") and font.currentTab:
            # We’re in the Edit View
            # Check whether glyph is being edited
            font.currentTab.text = f"/{glyphname}"
        else:
            # We’re in the Font view
            font.selection = [font.glyphs[glyphname]]
        self.updateInfo()

    def addMissingForBlock_(self, sender=None) -> None:
        i = self.w.block_list.get()
        if i > -1:
            blk = self.blocks_in_popup[i]
            self._addMissingBlock(blk)
            self.updateInfo()

    @objc.python_method
    def _addMissingBlock(self, block) -> None:
        font = self.font_fallback
        if font is None:
            return

        missing = self.get_block_glyph_list(block, font, False)
        add_glyphs_to_font(missing, font)
        # TODO: Update the block's indicator
        # self.w.block_list.setItem("●" + block[1:])

    def addMissingForOrthography_(self, sender=None) -> None:
        """
        Add glyphs that are missing for an orthography.

        Args:
            sender (_type_, optional): The objc sender. Defaults to None.
        """
        # Get selected orthography
        i = self.w.orthography_list.get()
        if i > -1:
            ort: Orthography = self.ortho_list[i]
            self._addMissingOrthography(ort)
            self._updateOrthographies()

    @objc.python_method
    def _addMissingOrthography(self, orthography: "Orthography") -> None:
        font = self.font_fallback
        if font is None:
            return

        glyph_list = self.get_orthography_glyph_list(orthography, font, False)

        add_glyphs_to_font(glyph_list, font)

    def includeOptional_(self, sender=None) -> None:
        if sender is None:
            return

        self.include_optional = sender.get()
        self._updateOrthographies()

    def reassignUnicodes_(self, sender=None) -> None:
        if self.font is not None:
            unicodes = {g.unicode: g.name for g in self.font.glyphs if g.unicode}
            for g in self.font.glyphs:
                myUnicode = self.get_unicode_for_glyphname(g.name)
                if g.unicode != myUnicode:
                    print(f"{g.name}:", end="")
                    if g.unicode is not None:
                        print(f"{g.unicode:x} ->", end="")
                    else:
                        print("<None> ->", end="")
                    if myUnicode is not None:
                        print(f"{myUnicode:x}", end="")
                    else:
                        print("<None>", end="")
                    if myUnicode in unicodes:
                        print(f"-- Ignored: already in use (/{unicodes[myUnicode]}).")
                    else:
                        print()
                        if myUnicode is None:
                            g.unicode = ""
                        else:
                            g.unicode = hex(myUnicode)
                            unicodes[g.unicode] = g.name

    def resetFilter_(self, sender=None) -> None:
        self.w.reset_filter.enable(False)
        self.w.show_orthography.enable(True)
        self.w.show_block.enable(True)
        self.w.block_add_missing.enable(False)
        self.w.orthography_add_missing.enable(False)
        self._resetFilter(sender)
        self.filtered = False

    @objc.python_method
    def _resetFilter(self, sender=None) -> None:
        # Reset the sorting from set_filter
        font = self.font_fallback
        if font is None:
            return

        # https://forum.glyphsapp.com/t/create-list-filter-via-script/2134/13
        font.fontView.glyphsGroupViewController().update()

    def selectDatabase_(self, sender=None) -> None:
        if sender is None:
            return

        if sender.getTitle() == "CLDR":
            self.ortho = self.ortho_cdlr
        else:
            assert sender.getTitle() == "Hyperglot"
            self.ortho = self.ortho_hyperglot
        self._updateOrthographies()

    def selectBlock_WithName_(self, sender=None, name="") -> None:
        i = 0
        if sender is None:
            if name == "":
                self.w.block_list.set(0)
            else:
                try:
                    i = self.blocks_in_popup.index(name)
                except ValueError:
                    i = 0
                self.w.block_list.set(i)
        else:
            i = self.w.block_list.get()
        if i == 0:
            self.w.show_block.enable(False)
            self.w.block_add_missing.enable(False)
        else:
            self.w.show_block.enable(self.in_font_view and not self.filtered)
            # Show supported status for block
            font = self.font_fallback
            if font is None:
                is_supported = False
            else:
                block = self.blocks_in_popup[i]
                glyph_list = self.get_missing_glyphs_for_block(block, font)
                is_supported = len(glyph_list) == 0
                self.w.block_add_missing.enable(not is_supported)

    def selectOrthography_Index_(self, sender=None, index: int = -1) -> None:
        self.w.speakers_label.set("")
        if sender is None:
            i = index
            if i == -1:
                # Select the first supported language:
                for j in range(len(self.ortho_list)):
                    if self.ortho_list[j].support_basic:
                        i = j
                        break
                else:
                    i = 0
        else:
            i = sender.get()
        if i > -1:
            if i < len(self.orthographies_in_popup):
                self.selected_orthography = self.orthographies_in_popup[i]
                self.w.orthography_list.set(i)
                orthography = self.ortho_list[i]
                if self.include_optional:
                    is_supported = orthography.support_full
                else:
                    is_supported = orthography.support_basic
                self.w.orthography_add_missing.enable(not is_supported)
                if not is_supported:
                    missing = orthography.missing_base | orthography.missing_punctuation
                    if self.include_optional:
                        missing |= orthography.missing_optional
                    # print(
                    #     f"{len(missing)} codepoints missing from orthography "
                    #     f"'{orthography.name}':\n"
                    #     f"{[hex(m) for m in missing]}"
                    # )
                if orthography.speakers != 0:
                    speakers_label_text = speakers_as_string(orthography.speakers)
                    if orthography.script != "DFLT":
                        speakers_label_text += " (non-default script)"
                    self.w.speakers_label.set(speakers_label_text)
        else:
            self.selected_orthography = None
            self.w.orthography_add_missing.enable(False)

    def showBlock_(self, sender=None) -> None:
        # Callback for the "Show" button of the Unicode blocks list
        if sender is None:
            return

        i = self.w.block_list.get()
        if i <= 0:
            return

        if i < len(self.blocks_in_popup):
            font = self.font_fallback
            if font is None:
                return

            block = self.blocks_in_popup[i]
            glyph_list = [f"** {block} **"]
            glyph_list.extend(self.get_block_glyph_list(block, font))
            glyph_list.append("** End **")

            # Update status
            missing = self.get_missing_glyphs_for_block(block, font)
            is_supported = len(missing) == 0
            self.w.block_add_missing.enable(not is_supported)
            set_filter(font, glyph_list)
        self.w.reset_filter.enable(True)
        self.filtered = True
        self.w.show_block.enable(False)
        self.w.show_orthography.enable(False)

    def showOrthography_(self, sender=None) -> None:
        # Callback for the "Show" button of the Orthographies list
        if self.filtered:
            self._resetFilter()
        if sender is None:
            return

        i = self.w.orthography_list.get()
        if i < 0:
            return

        if i < len(self.orthographies_in_popup):
            font = self.font_fallback
            if font is None:
                return

            orthography = self.ortho_list[i]
            glyph_list = self.get_orthography_glyph_list(orthography, font)
            set_filter(font, glyph_list)
        # Set the selection to the same index as before
        self.selectOrthography_Index_(sender=None, index=i)
        self.w.reset_filter.enable(True)
        self.filtered = True
        self.w.show_block.enable(False)
        self.w.show_orthography.enable(False)

    def showWikiCharacter_(self, sender=None) -> None:
        if not self.unicode:
            return
        url = (
            "https://en.wikipedia.org/w/index.php?title=Special:Search&search="
            + urllib.parse.quote(chr(self.unicode), safe="")
        )
        webbrowser.open(url)

    def showWikiOrthography_(self, sender=None) -> None:
        if not self.selected_orthography:
            return
        search_string = self.selected_orthography.split("(")[0] + " language"
        url = (
            "https://en.wikipedia.org/w/index.php?title=Special:Search&search="
            + urllib.parse.quote(search_string, safe="")
        )
        webbrowser.open(url)

    # Internal

    @objc.python_method
    def _updateBlock(self, u: int | None) -> None:
        if u is None:
            self.w.block_list.set(0)
            self.w.show_block.enable(False)
            self.w.block_add_missing.enable(False)
        else:
            # Get the name of the Unicode block for codepoint u
            block = get_block(u)
            if block in self.blocks_in_popup:
                self.w.block_list.set(self.blocks_in_popup.index(block))
                self.w.show_block.enable(self.in_font_view and not self.filtered)
                if self.font is None:
                    self.w.block_add_missing.enable(False)
                else:
                    missing = bool(self.get_missing_glyphs_for_block(block, self.font))
                    self.w.block_add_missing.enable(missing)
            else:
                self.w.block_list.set(0)
                self.w.show_block.enable(False)
                self.w.block_add_missing.enable(False)

    @objc.python_method
    def _updateGlyph(self) -> None:
        if self.font is None:
            self.w.reassign_unicodes.enable(False)
            self.w.include_optional.enable(False)
            self.w.show_block.enable(False)
        else:
            self.w.reassign_unicodes.enable(True)
            self.w.include_optional.enable(True)
            self.w.show_block.enable(True)
        if self.glyph is None:
            self._updateInfo(None)
        else:
            self.unicode = self.glyph_unicode
            fake = False
            if self.unicode is None:
                if "." in self.glyph.name[1:]:
                    fake = True
                    base, _ext = self.glyph.name.split(".", 1)
                    if self.font is None:
                        self.unicode = self.get_unicode_for_glyphname(base)
                    else:
                        if base in self.font.glyphs:
                            base_glyph = self.font.glyphs[base]
                            if base_glyph.unicode is None:
                                self.unicode = None
                            else:
                                self.unicode = int(base_glyph.unicode, 16)
                            if self.unicode is None:
                                self.unicode = self.get_unicode_for_glyphname(base)
                        else:
                            self.unicode = self.get_unicode_for_glyphname(base)
                else:
                    base = self.glyph.name
                    self.unicode = self.get_unicode_for_glyphname(base)
            self._updateInfo(self.unicode, fake)

    @objc.python_method
    def _updateInfo(self, u=None, fake=False) -> None:
        self._updateBlock(u)
        if u is None:
            self.w.uni_name.set("❓")
            self.w.code.set("")
            if self.glyph is None:
                self.w.glyph_name.set("")
            else:
                self.w.glyph_name.set(self.glyph.name)
            self.w.case.enable(False)
            self._updateOrthographies()
            return

        self.info.unicode = u
        name = self.info.name
        if name is None:
            self.w.uni_name.set("")
        else:
            self.w.uni_name.set(name.title())
        if fake:
            self.w.code.set("😀 None")
            self.w.glyph_name.set(self.glyph.name if self.glyph else "")
            self.case = None
            self.w.case.enable(False)
        else:
            # Unicode
            if u == self.glyph_unicode:
                self.w.code.set(f"😀 {u:04X}")
            else:
                if self.glyph_unicode is None:
                    self.w.code.set(f"😡 None → {u:04X}")
                else:
                    self.w.code.set(f"😡 {self.glyph_unicode:04X} → {u:04X}")

            # Glyph name
            expected_name = self.get_glyphname_for_unicode(u)
            glyph_name = self.glyph.name if self.glyph else ""
            if glyph_name == expected_name:
                self.w.glyph_name.set(f"😀 {expected_name}")
            else:
                self.w.glyph_name.set(f"😡 {glyph_name} → {expected_name}")

            # Case mapping
            lc = self.info.lc_mapping
            if lc is None:
                uc = self.info.uc_mapping
                if uc is None:
                    self.case = None
                    self.w.case.enable(False)
                else:
                    self.case = uc
                    self.w.case.enable(True)
            else:
                self.case = lc
                self.w.case.enable(True)
        self._updateOrthographies()

    @objc.python_method
    def _updateOrthographies(self) -> None:
        self.w.speakers_label.set("")
        self.w.speakers_supported_label.set("")
        # Check which orthographies use current unicode
        if self.glyph is None or self.unicode is None:
            # Show all
            self.ortho_list = self.ortho.orthographies
        else:
            if self.include_optional:
                self.ortho_list = sorted(
                    self.ortho.get_orthographies_for_unicode_any(self.unicode)
                )
            else:
                self.ortho_list = sorted(
                    self.ortho.get_orthographies_for_unicode(self.unicode)
                )
        self.orthographies_in_popup = [o.name for o in self.ortho_list]
        orthography_list_ui_strings = []
        # TODO: We need a strategy for when multiple glyphs are selected
        for o in self.ortho_list:
            if o.support_full:
                ui_string = "● " + o.name
            elif o.support_basic:
                ui_string = "◑ " + o.name
            else:
                ui_string = "○ " + o.name
            if self.unicode is not None and not o.uses_unicode_base(self.unicode):
                ui_string += " [optional]"
            orthography_list_ui_strings.append(ui_string)
        self.w.orthography_list.setItems(orthography_list_ui_strings)
        if len(self.ortho_list) == 0:
            self.w.orthography_list.enable(False)
            self.w.show_orthography.enable(False)
            if (
                not self.include_optional
                and self.unicode is not None
                and len(self.ortho.get_orthographies_for_unicode_any(self.unicode)) != 0
            ):
                self.w.speakers_supported_label.set(
                    "Optional character. Activate “include optional” to show the languages."
                )
                return
            if self.unicode:
                self.w.speakers_supported_label.set(
                    "⚠ This character is not used in\u00a0"
                    + self.ortho.source_display_name
                    + "."
                )
        else:
            self.w.orthography_list.enable(True)
            self.w.show_orthography.enable(self.in_font_view and not self.filtered)
            # If the old name is in the new list, select it
            if self.selected_orthography is not None:
                try:
                    new_index = self.orthographies_in_popup.index(
                        self.selected_orthography
                    )
                    self.selectOrthography_Index_(index=new_index)
                except ValueError:
                    self.selectOrthography_Index_(index=-1)
            speakers_supported = (
                0
                if self.unicode is None
                else self.ortho.speakers_supported_by_unicode(self.unicode)
            )
            if speakers_supported == 0:
                # [Tim] This was the main goal of extending this tool:
                # To detect useless characters, i.e. those that are not required or optional
                # in any orthography that has at least base support.
                #
                # In other words, the current character can be removed from the font
                # without reducing the language support.
                #
                # FWIW, this situation corresponds to having only empty circles in the list of orthographies
                # (with or without “include optional” checked)
                self.w.speakers_supported_label.set(
                    "⚠ This character does not help support any\u00a0speakers."
                )
            else:
                self.w.speakers_supported_label.set(
                    "This character helps support "
                    + speakers_as_string(speakers_supported)
                    + "."
                )

    # Window callback

    @objc.python_method
    def windowClosed(self, sender) -> None:
        if self.hasNotification:
            Glyphs.removeCallback(self.updateInfo)
            self.hasNotification = False
