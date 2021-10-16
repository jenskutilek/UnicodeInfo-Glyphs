# encoding: utf-8

import objc
from GlyphsApp import Glyphs, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin

from unicode_info import UnicodeInfoWindow
import jkUnicode

# from jkUnicode.aglfn import getGlyphnameForUnicode, getUnicodeForGlyphname
from jkUnicode.uniBlock import get_block, uniNameToBlock  # get_codepoints

# from jkUnicode.uniName import uniName
try:
    from jkUnicode.orthography import OrthographyInfo

    orth_present = True
except ImportError:
    orth_present = False


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


class UnicodeInfoPalette(PalettePlugin, UnicodeInfoWindow):
    @objc.python_method
    def settings(self):
        from vanilla import CheckBox, Group, PopUpButton, TextBox, Window

        self.name = Glyphs.localize(
            {"en": u"Unicode Info", "de": u"Unicode-Info"}
        )

        # Create Vanilla window and group with controls
        width = 150
        height = 86
        self.paletteView = Window((width, height))
        self.paletteView.group = Group((0, 0, width, height))
        self.w = self.paletteView.group
        y = 0
        self.w.block_label = TextBox(
            (10, y, -10, 20), "Block:", sizeStyle="small"
        )
        y += 17
        self.w.block_list = PopUpButton(
            (10, y, -30, 20), [], sizeStyle="small", callback=self.selectBlock
        )
        self.w.block_status = CheckBox((-20, y, -10, 20), "", sizeStyle="small")
        if orth_present:
            y += 24
            self.w.orthography_label = TextBox(
                (10, y, -10, 20), "Usage:", sizeStyle="small"
            )
            y += 17
            self.w.orthography_list = PopUpButton(
                (10, y, -30, 20),
                [],
                sizeStyle="small",
                callback=self.selectOrthography,
            )
            self.w.orthography_status = CheckBox(
                (-20, y, -10, 20), "", sizeStyle="small"
            )

        # Set dialog to NSView
        self.dialog = self.w.getNSView()

    @objc.python_method
    def setup_class(self):

        self.info = jkUnicode.UniInfo(0)
        self.unicode = None
        if orth_present:
            self.ortho = OrthographyInfo()
            self.ortho_list = []
        self.case = None
        self.view = None
        self.include_optional = False
        # self.w.reassign_unicodes.enable(False)
        self.w.block_list.setItems([""] + sorted(uniNameToBlock.keys()))
        # self.w.show_block.enable(False)
        self.w.block_status.enable(False)
        # self.w.case.enable(False)
        if orth_present:
            self.w.orthography_list.enable(False)
            # self.w.show_orthography.enable(False)
            self.w.orthography_status.enable(False)
            # if self.font is None:
            # 	self.w.include_optional.enable(False)
            # else:
            # 	self.w.include_optional.enable(True)

    @objc.python_method
    def start(self):
        # Adding a callback for the 'GSUpdateInterface' event
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

        self.font = None
        self.glyph_name = None
        self.glyph = None
        self.setup_class()

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
                uni = get_unicode_for_glyph(glyph)
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
                uni = get_unicode_for_glyph(glyph)
            else:
                self.glyph_name = None
                self.glyph = None

        if self.unicode == uni:
            return
        else:
            self.unicode = uni

        self._updateBlock(self.unicode)
        self._updateOrthographies()

    @objc.python_method
    def _updateBlock(self, u):
        if u is None:
            self.w.block_list.set(0)
            # self.w.show_block.enable(False)
        else:
            # Get the name of the Unicode block for codepoint u
            block = get_block(u)
            items = self.w.block_list.getItems()
            if block in items:
                self.w.block_list.set(items.index(block))
                # self.w.show_block.enable(True)
            else:
                self.w.block_list.set(0)
                # self.w.show_block.enable(False)
        # self.selectBlock()

    @objc.python_method
    def _updateOrthographies(self):
        if not orth_present:
            return
        # Save the old selection from the orthography list
        old_index = self.w.orthography_list.get()
        if old_index > -1:
            old_sel = self.ortho_list[self.w.orthography_list.get()].name
        else:
            old_sel = None
        new_index = 0

        # Check which orthographies use current unicode
        if self.glyph is None:
            # Show all
            self.ortho_list = [o for o in sorted(self.ortho.orthographies)]
        else:
            if self.include_optional:
                self.ortho_list = [
                    o
                    for o in sorted(
                        self.ortho.get_orthographies_for_unicode_any(
                            self.unicode
                        )
                    )
                ]
            else:
                self.ortho_list = [
                    o
                    for o in sorted(
                        self.ortho.get_orthographies_for_unicode(self.unicode)
                    )
                ]

        self.w.orthography_list.setItems([o.name for o in self.ortho_list])

        if len(self.ortho_list) == 0:
            self.w.orthography_list.enable(False)
            # self.w.show_orthography.enable(False)
        else:
            self.w.orthography_list.enable(True)
            # self.w.show_orthography.enable(True)
            # If the old name is in the new list, select it
            if old_sel is not None:
                names = self.w.orthography_list.getItems()
                if old_sel in names:
                    new_index = names.index(old_sel)

        self.selectOrthography(index=new_index)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        if self._font is not None:
            if orth_present:
                self.ortho.cmap = [
                    int(g.unicode, 16) for g in self.font.glyphs if g.unicode
                ]

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
