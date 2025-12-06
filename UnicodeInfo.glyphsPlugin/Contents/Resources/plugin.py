from __future__ import annotations

from typing import Any

import objc
from AppKit import NSMenuItem
from GlyphsApp import UPDATEINTERFACE, WINDOW_MENU, Glyphs, GSGlyph
from GlyphsApp.plugins import GeneralPlugin
from jkUnicode.aglfn import getGlyphnameForUnicode, getUnicodeForGlyphname
from unicodeInfoWindow import UnicodeInfoWindow


def add_glyphs_to_font(glyph_names, font) -> None:
    glyph_list = [n for n in glyph_names if n not in font.glyphs]
    # print("Adding glyphs:", " ".join(glyph_list))
    font.disableUpdateInterface()
    glyphs = [GSGlyph(n) for n in glyph_list]
    font.glyphs.extend(glyphs)
    font.enableUpdateInterface()
    set_selection(font, glyph_list, deselect=True)


def set_filter(font=None, glyph_names=None) -> None:
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


def set_selection(font, glyph_names, deselect=False) -> None:
    font.disableUpdateInterface()
    if deselect:
        for g in font.glyphs:
            g.selected = False
    for g in glyph_names:
        font.glyphs[g].selected = True
    font.enableUpdateInterface()


class UnicodeInfo(GeneralPlugin, UnicodeInfoWindow):
    @objc.python_method
    def settings(self) -> None:
        self.hasNotification = False
        self.name = Glyphs.localize({"en": "Unicode Info", "de": "Unicode-Info"})

    def showWindow_(self, sender) -> None:
        self.glyph = None
        self.glyph_name = None
        self.filtered = False
        self.in_font_view = False
        self.build_window(manual_update=True)
        if not self.hasNotification:
            Glyphs.addCallback(self.updateInfo, UPDATEINTERFACE)
        self.hasNotification = True
        self.started()
        self.updateInfo()

    @objc.python_method
    def start(self) -> None:
        newMenuItem = NSMenuItem.alloc().init()
        newMenuItem.setTitle_(self.name)
        newMenuItem.setAction_(self.showWindow_)
        newMenuItem.setTarget_(self)
        Glyphs.menu[WINDOW_MENU].append(newMenuItem)

    @objc.python_method
    def windowClosed(self, sender) -> None:
        if self.hasNotification:
            Glyphs.removeCallback(self.updateInfo)
            self.hasNotification = False

    @objc.python_method
    def glyph_unicodes(self, glyph) -> set[int]:
        """
        Return a glyph's Unicode values as set of int.
        """
        # Glyphs stores Unicode values as hex string
        return set([int(u, 16) for u in glyph.unicodes])

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

    # Overrides for the UnicodeInfoWindow base class

    @property
    def font_fallback(self):
        if self._font is not None:
            return self._font
        return Glyphs.font

    @property
    def font_glyphs(self) -> dict[str, Any]:
        f = self.font_fallback
        if f is None:
            return {}
        return self.font_fallback.glyphs

    @property
    def glyph_font(self):
        if self._glyph is None:
            return None

        return self._glyph.parent

    @property
    def glyph_unicode(self) -> int | None:
        if self._glyph is None:
            return None
        if self._glyph.unicode is None:
            return None

        return int(self._glyph.unicode, 16)

    @objc.python_method
    def glyphs_for_font(self, font) -> dict[str, Any]:
        if font is None:
            return {}
        return font.glyphs

    @objc.python_method
    def gnful_name(self, u) -> None:
        return None

    @objc.python_method
    def get_glyphname_for_unicode(self, value=None) -> tuple[str | None, None]:
        if value is None:
            return None, None

        font = self.font_fallback
        if font is None:
            return None, None

        if font.disablesNiceNames:
            name = getGlyphnameForUnicode(value)
        else:
            g = GSGlyph()
            g.unicode = "%04X" % value
            g.updateGlyphInfo(changeName=True)
            name = g.name
        return name, None

    @objc.python_method
    def get_unicode_for_glyphname(self, name=None) -> int | None:
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

    # @objc.python_method
    # def get_unicode_for_glyph(self, glyph):
    #     uni = glyph.unicode
    #     if uni is None:
    #         if "." in glyph.name:
    #             base, suffix = glyph.name.split(".", 1)
    #             if base in glyph.parent.glyphs:
    #                 uni = glyph.parent.glyphs[base].unicode
    #     if uni is not None:
    #         uni = int(uni, 16)
    #     return uni

    @objc.python_method
    def toggleCase(self, sender=None) -> None:
        font = self.font_fallback
        if font is None:
            return
        if self.case is None:
            return

        glyphname, _ = self.get_glyphname_for_unicode(self.case)
        if glyphname is None:
            return

        if hasattr(font, "currentTab") and font.currentTab:
            # We’re in the Edit View
            # Check whether glyph is being edited
            font.currentTab.text = f"/{glyphname}"
        else:
            # We’re in the Font view
            font.selection = [font[glyphname]]
        self.updateInfo()

    @objc.python_method
    def _resetFilter(self, sender=None) -> None:
        # Reset the sorting from set_filter
        font = self.font_fallback
        if font is None:
            return

        # https://forum.glyphsapp.com/t/create-list-filter-via-script/2134/13
        font.fontView.glyphsGroupViewController().update()

    @objc.python_method
    def _addMissingBlock(self, block) -> None:
        font = self.font_fallback
        if font is None:
            return

        glyph_list = self.get_block_glyph_list(block, font, False)
        add_glyphs_to_font(glyph_list, font)

    @objc.python_method
    def _addMissingOrthography(self, orthography) -> None:
        font = self.font_fallback
        if font is None:
            return

        glyph_list = self.get_orthography_glyph_list(orthography, font, False)
        add_glyphs_to_font(glyph_list, font)

    @objc.python_method
    def _saveGlyphSelection(self, font=None) -> None:
        pass

    @objc.python_method
    def _showGlyphList(self, font, glyph_list) -> None:
        set_filter(font, glyph_list)

    @objc.python_method
    def _restoreGlyphSelection(self, font=None) -> None:
        pass

    # Glyphs stuff

    @objc.python_method
    def __file__(self) -> str:
        """Please leave this method unchanged"""
        return __file__

    # Temporary Fix
    # Sort ID for compatibility with v919:
    _sortID = 0

    def setSortID_(self, id: int) -> None:
        try:
            self._sortID = id
        except Exception as e:
            self.logToConsole("setSortID_: %s" % str(e))

    def sortID(self) -> int:
        return self._sortID
