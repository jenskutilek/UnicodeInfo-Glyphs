# encoding: utf-8

import objc
from AppKit import NSMenuItem
from GlyphsApp import Glyphs, UPDATEINTERFACE, WINDOW_MENU
from GlyphsApp.plugins import GeneralPlugin

from unicodeInfoWindow import UnicodeInfoWindow

from jkUnicode.uniBlock import get_block


class GlyphsUnicodeInfoWindow(UnicodeInfoWindow):
    pass


class UnicodeInfo(GeneralPlugin, GlyphsUnicodeInfoWindow):
    @objc.python_method
    def settings(self):
        self.name = Glyphs.localize(
            {"en": u"Unicode Info", "de": u"Unicode-Info"}
        )

    def showWindow_(self, sender):
        self.glyph = None
        self.build_window()
        Glyphs.addCallback(self.update, UPDATEINTERFACE)
        self.started()

    @objc.python_method
    def start(self):
        newMenuItem = NSMenuItem(self.name, self.showWindow_)
        Glyphs.menu[WINDOW_MENU].append(newMenuItem)
        print(newMenuItem)

    @objc.python_method
    def __del__(self):
        Glyphs.removeCallback(self.update)

    @objc.python_method
    def update(self, sender):

        # Extract font from sender
        font = sender.object().parent
        uni = None

        # We’re in the Edit View
        if hasattr(font, "currentTab") and font.currentTab:
            # Check whether glyph is being edited
            if len(font.selectedLayers) == 1:
                glyph = font.selectedLayers[0].parent
                if font == self.font:
                    if glyph.name == self.glyph_name:
                        return
                else:
                    self.font = font
                self.glyph_name = glyph.name
                self.glyph = glyph
                uni = self.get_unicode_for_glyph(glyph)
            else:
                self.glyph_name = None
                self.glyph = None

        # We’re in the Font view
        else:
            if font and len(font.selection) == 1:
                glyph = font.selection[0]
                if font == self.font:
                    if glyph.name == self.glyph_name:
                        return
                else:
                    self.font = font
                self.glyph_name = glyph.name
                self.glyph = glyph
                uni = self.get_unicode_for_glyph(glyph)
            else:
                self.glyph_name = None
                self.glyph = None

        if self.unicode == uni:
            return
        else:
            self.unicode = uni

        self._updateBlock(self.unicode)
        self._updateOrthographies()

    # Overrides for the UnicodeInfoWindow base class

    @property
    def font_fallback(self):
        if self._font is not None:
            return self._font
        return Glyphs.font

    @property
    def font_glyphs(self):
        if self._font is not None:
            return self._font.glyphs
        return []

    @property
    def glyph_font(self):
        if self._glyph is None:
            return None

        return self._glyph.parent

    # def get_unicode_for_glyphname(self, name=None):
    #     if name is None:
    #         return None
    #     # First try jkUnicode
    #     u = getUnicodeForGlyphname(name)
    #     if u is None:
    #         # then try GNFUL
    #         u = getGlyphNameComponentUnicode(name)
    #         if u is not None:
    #             u = u[1]
    #     return u

    @property
    def get_unicode_for_glyph(glyph):
        uni = glyph.unicode
        if uni is None:
            if "." in glyph.name:
                base, suffix = glyph.name.split(".", 1)
                if base in glyph.parent.glyphs:
                    uni = glyph.parent.glyphs[base].unicode
        if uni is not None:
            uni = int(uni, 16)
        return uni

    @objc.python_method
    def toggleCase(self, sender=None):
        pass
        # if self.font is None:
        #     return

        # glyphname = getGlyphnameForUnicode(self.case)
        # if self.view is None:
        #     # No Glyph Window, use the selection in the Font Window
        #     self.font.selectedGlyphNames = [glyphname]
        # else:
        #     # Show the cased glyph in the Glyph Window
        #     SetCurrentGlyphByName(glyphname)

    # Glyphs stuff

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__

    # Temporary Fix
    # Sort ID for compatibility with v919:
    _sortID = 0

    def setSortID_(self, id):
        try:
            self._sortID = id
        except Exception as e:
            self.logToConsole("setSortID_: %s" % str(e))

    def sortID(self):
        return self._sortID
