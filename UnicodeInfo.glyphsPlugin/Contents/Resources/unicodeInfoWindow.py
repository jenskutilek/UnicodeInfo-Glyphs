# -*- coding: utf-8 -*-

import objc

from jkUnicode import UniInfo, get_expanded_glyph_list
from jkUnicode.aglfn import getGlyphnameForUnicode, getUnicodeForGlyphname
from jkUnicode.uniBlock import get_block, get_codepoints, uniNameToBlock
from jkUnicode.uniName import uniName


class UnicodeInfoWindow:
    @objc.python_method
    def build_window(self, manual_update=False):
        from vanilla import (
            Button,
            CheckBox,
            FloatingWindow,
            PopUpButton,
            TextBox,
        )

        try:
            from jkUnicode.orthography import OrthographyInfo

            self.orth_present = True
        except ImportError:
            self.orth_present = False

        width = 320
        height = 116

        if self.orth_present:
            height += 37
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
        self.w.uni_name = TextBox(
            (axis, y, -10, 20), u"", sizeStyle="small"
        )
        y += 20
        self.w.code_label = TextBox(
            (8, y, axis - 10, 20), "Code", sizeStyle="small"
        )
        self.w.code = TextBox(
            (axis, y, -10, 20), u"", sizeStyle="small"
        )
        self.w.reassign_unicodes = Button(
            (-81, y - 6, -10, 25),
            "Assign All",
            callback=self.reassignUnicodes,
            sizeStyle="small",
        )
        y += 20
        self.w.glyph_name_label = TextBox(
            (8, y, axis - 10, 20), "Glyph", sizeStyle="small"
        )
        self.w.glyph_name = TextBox(
            (axis, y, -10, 20), u"", sizeStyle="small"
        )
        self.w.case = Button(
            (-81, y - 6, -10, 25),
            "\u2191 \u2193 Case",
            callback=self.toggleCase,
            sizeStyle="small",
        )
        y += 20
        self.w.block_label = TextBox(
            (8, y, axis - 10, 20), "Block", sizeStyle="small"
        )
        self.w.block_list = PopUpButton(
            (axis, y - 4, -90, 20),
            [],
            callback=self.selectBlock,
            sizeStyle="small",
        )
        self.w.block_status = CheckBox(
            (-80, y - 3, -70, 20), "", sizeStyle="small"
        )
        self.w.show_block = Button(
            (-60, y - 6, -10, 25),
            "Show",
            callback=self.showBlock,
            sizeStyle="small",
        )
        if self.orth_present:
            y += 20
            self.w.orthography_label = TextBox(
                (8, y, axis - 10, 20), "Usage", sizeStyle="small"
            )
            self.w.orthography_list = PopUpButton(
                (axis, y - 4, -90, 20),
                [],
                callback=self.selectOrthography,
                sizeStyle="small",
            )
            self.w.orthography_status = CheckBox(
                (-80, y - 3, -70, 20), "", sizeStyle="small"
            )
            self.w.show_orthography = Button(
                (-60, y - 6, -10, 25),
                "Show",
                callback=self.showOrthography,
                sizeStyle="small",
            )
            y += 20
            self.w.include_optional = CheckBox(
                (axis, y, 200, 20),
                "Include optional characters",
                callback=self.includeOptional,
                sizeStyle="small",
            )
        if manual_update:
            y += 24
            self.w.block_add_missing = Button(
                (-290, y - 6, -226, 25),
                "Fill Block",
                callback=self.addMissingBlock,
                sizeStyle="small",
            )
            self.w.orthography_add_missing = Button(
                (-218, y - 6, -154, 25),
                "Fill Orth.",
                callback=self.addMissingOrthography,
                sizeStyle="small",
            )
            self.w.reset_filter = Button(
                (-146, y - 6, -68, 25),
                "Reset Filter",
                callback=self.resetFilter,
                sizeStyle="small",
            )
            # self.w.manual_update = Button(
            #     (-60, y - 6, -10, 25),
            #     "Query",
            #     callback=self.updateInfo,
            #     sizeStyle="small",
            # )

        self.info = UniInfo(0)
        self.unicode = None
        if self.orth_present:
            self.ortho = OrthographyInfo(ui=self.info)
            self.ortho_list = []
        self.case = None
        self.view = None
        self.selectedGlyphs = ()
        self.include_optional = False
        self.w.reassign_unicodes.enable(False)
        self.w.block_list.setItems([""] + sorted(uniNameToBlock.keys()))
        self.w.show_block.enable(False)
        self.w.block_status.enable(False)
        self.w.case.enable(False)

        if manual_update:
            self.w.block_add_missing.enable(False)
            self.w.orthography_add_missing.enable(False)
            self.w.reset_filter.enable(False)

        if self.orth_present:
            # self.w.orthography_list.enable(False)
            self.w.show_orthography.enable(False)
            self.w.orthography_status.enable(False)
            # if self.font is None:
            #     self.w.include_optional.enable(False)
            # else:
            #     self.w.include_optional.enable(True)

    @objc.python_method
    def build(self):
        raise NotImplementedError

    @objc.python_method
    def windowClosed(self, sender):
        raise NotImplementedError

    @objc.python_method
    def started(self):
        self.w.open()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        if self._font is not None:
            if self.orth_present:
                cmap = set()
                for g in self.font_glyphs:
                    if g.unicodes:
                        cmap |= self.glyph_unicodes(g)
                self.ortho.cmap = {u: None for u in cmap}

    @property
    def font_fallback(self):
        """
        Return the current glyph's font or, as a fallback, the current font.
        """
        raise NotImplementedError

    @property
    def font_glyphs(self):
        """
        Return the glyphs dict of the current glyph's font.
        """
        raise NotImplementedError

    @property
    def glyph(self):
        return self._glyph

    @glyph.setter
    def glyph(self, value):
        self._glyph = value
        if self._glyph is None:
            self.font = None
        else:
            self.font = self.glyph_font

    @property
    def glyph_font(self):
        """
        Return the current glyph's font.
        """
        raise NotImplementedError

    @property
    def glyph_unicode(self):
        """
        Return the current glyph's Unicode value as int.
        """
        raise NotImplementedError

    @objc.python_method
    def glyph_unicodes(self, glyph):
        """
        Return a glyph's Unicode values as set of int.
        """
        return set(glyph.unicodes)

    @objc.python_method
    def glyphs_for_font(self, font):
        """
        Return the glyphs dict for a font.
        """
        raise NotImplementedError

    @objc.python_method
    def get_extensions(self, font):
        # Return all used glyph name extensions in the font
        return [
            n.split(".", 1)[1]
            for n in self.glyphs_for_font(font).keys()
            if "." in n[1:]
        ]

    @objc.python_method
    def get_extension_map(self, font):
        # Return a map of base glyph names to extension names for the font
        d = {}
        for g in self.glyphs_for_font(font).keys():
            if "." in g[1:]:
                base, ext = g.split(".", 1)
                if base not in d:
                    d[base] = [g]
                else:
                    d[base].append(g)
            else:
                if g not in d:
                    d[g] = []
        return d

    @objc.python_method
    def get_extra_names(self, font, uni_name_tuples):
        ext_map = self.get_extension_map(font)
        additions = []
        for u, n in uni_name_tuples:
            additions.extend([(u, e) for e in ext_map.get(n, [])])
        uni_name_tuples.extend(additions)
        return list(set(uni_name_tuples))

    @objc.python_method
    def get_glyphname_for_unicode(self, value=None):
        if value is None:
            return None
        # from jkUnicode
        name = getGlyphnameForUnicode(value)
        alt = self.gnful_name(value)
        return (name, alt)

    @objc.python_method
    def get_unicode_for_glyphname(self, name=None):
        if name is None:
            return None
        # from jkUnicode
        u = getUnicodeForGlyphname(name)
        return u

    @objc.python_method
    def addMissingBlock(self, sender=None):
        i = self.w.block_list.get()
        if i > -1:
            blk = self.w.block_list.getItems()[i]
            self._addMissingBlock(blk)
            self.updateInfo()

    @objc.python_method
    def addMissingOrthography(self, sender=None):
        # Add glyphs that are missing for an orthography
        # Get selected orthography
        i = self.w.orthography_list.get()
        if i > -1:
            ort = self.ortho_list[i]
            self._addMissingOrthography(ort)
            self._updateOrthographies()

    @objc.python_method
    def resetFilter(self, sender=None):
        self.w.reset_filter.enable(False)
        self.w.show_orthography.enable(True)
        self.w.show_block.enable(True)
        self.w.block_add_missing.enable(False)
        self.w.orthography_add_missing.enable(False)
        self._resetFilter(sender)
        self.filtered = False

    @objc.python_method
    def selectOrthography(self, sender=None, index=-1):
        if sender is None:
            i = index
            if i == -1 and len(self.w.orthography_list.getItems()) > 0:
                i = self.w.orthography_list.get()
        else:
            i = sender.get()
        if i > -1:
            if i < len(self.w.orthography_list.getItems()):
                self.w.orthography_list.set(i)
                if self.include_optional:
                    is_supported = self.ortho_list[i].support_full
                else:
                    is_supported = self.ortho_list[i].support_basic
                self.w.orthography_status.set(is_supported)
                self.w.orthography_add_missing.enable(not is_supported)
                if not is_supported:
                    missing = (
                        self.ortho_list[i].missing_base
                        | self.ortho_list[i].missing_punctuation
                    )
                    if self.include_optional:
                        missing |= self.ortho_list[i].missing_optional
                    # print(
                    #     f"{len(missing)} codepoints missing from orthography "
                    #     f"'{self.ortho_list[i].name}':\n"
                    #     f"{[hex(m) for m in missing]}"
                    # )

        else:
            self.w.orthography_status.set(False)
            self.w.orthography_add_missing.enable(False)

    @objc.python_method
    def get_missing_glyphs_for_block(self, block, font):
        glyph_list = self.get_block_glyph_list(block, font, False, False)
        missing = [
            n
            for n in glyph_list
            if n not in self.font_glyphs
        ]
        if missing:
            print(
                f"{len(missing)} glyphs missing from block '{block}':"
                f"\n{missing}"
            )
        return missing

    @objc.python_method
    def selectBlock(self, sender=None, name=""):
        i = 0
        if sender is None:
            if name == "":
                self.w.block_list.set(0)
            else:
                items = self.w.block_list.getItems()
                if name in items:
                    i = items.index(name)
                else:
                    i = 0
                self.w.block_list.set(i)
        else:
            i = self.w.block_list.get()
        if i == 0:
            self.w.show_block.enable(False)
            self.w.block_status.set(False)
            self.w.block_add_missing.enable(False)
        else:
            self.w.show_block.enable(self.in_font_view and not self.filtered)
            # Show supported status for block
            font = self.font_fallback
            if font is None:
                is_supported = False
            else:
                block = self.w.block_list.getItems()[i]
                glyph_list = self.get_missing_glyphs_for_block(block, font)
                is_supported = len(glyph_list) == 0
                self.w.block_add_missing.enable(not is_supported)
            self.w.block_status.set(is_supported)

    @objc.python_method
    def updateInfo(self, sender):
        # Is called when the info is updated manually
        pass

    @objc.python_method
    def _updateInfo(self, u=None, fake=False):
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
        self.w.uni_name.set(self.info.name.title())
        if fake:
            self.w.code.set("😀 None")
            self.w.glyph_name.set(self.glyph.name)
            self.case = None
            self.w.case.enable(False)
        else:
            # Unicode
            if u == self.glyph_unicode:
                self.w.code.set("😀 %04X" % u)
            else:
                if self.glyph_unicode is None:
                    self.w.code.set("😡 None → %04X" % u)
                else:
                    self.w.code.set("😡 %04X → %04X" % (self.glyph_unicode, u))

            # Glyph name
            expected_name, alt_name = self.get_glyphname_for_unicode(u)
            if self.glyph.name == expected_name:
                self.w.glyph_name.set(f"😀 {expected_name}")
            elif alt_name is not None and self.glyph.name == alt_name:
                self.w.glyph_name.set(
                    f"😀 {alt_name} (Product: {expected_name})"
                )
            else:
                if alt_name is None:
                    self.w.glyph_name.set(
                        f"😡 {self.glyph.name} → {expected_name}"
                    )
                else:
                    self.w.glyph_name.set(
                        f"😡 {self.glyph.name} → {expected_name} or {alt_name}"
                    )

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
    def _updateBlock(self, u):
        if u is None:
            self.w.block_list.set(0)
            self.w.show_block.enable(False)
        else:
            # Get the name of the Unicode block for codepoint u
            block = get_block(u)
            items = self.w.block_list.getItems()
            if block in items:
                self.w.block_list.set(items.index(block))
                self.w.show_block.enable(
                    self.in_font_view and not self.filtered
                )
            else:
                self.w.block_list.set(0)
                self.w.show_block.enable(False)

    @objc.python_method
    def _updateOrthographies(self):
        if not self.orth_present:
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
            self.w.show_orthography.enable(False)
        else:
            self.w.orthography_list.enable(True)
            self.w.show_orthography.enable(
                self.in_font_view and not self.filtered
            )
            # If the old name is in the new list, select it
            if old_sel is not None:
                names = self.w.orthography_list.getItems()
                if old_sel in names:
                    new_index = names.index(old_sel)

        self.selectOrthography(index=new_index)

    @objc.python_method
    def _updateGlyph(self):
        if self.font is None:
            self.w.reassign_unicodes.enable(False)
            if self.orth_present:
                self.w.include_optional.enable(False)
            self.w.show_block.enable(False)
        else:
            self.w.reassign_unicodes.enable(True)
            if self.orth_present:
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
                    base, ext = self.glyph.name.split(".", 1)
                    if self.font is None:
                        self.unicode = self.get_unicode_for_glyphname(base)
                    else:
                        if base in self.font:
                            self.unicode = self.font[base].unicode
                            if self.unicode is None:
                                self.unicode = self.get_unicode_for_glyphname(
                                    base
                                )
                        else:
                            self.unicode = self.get_unicode_for_glyphname(base)
                else:
                    base = self.glyph.name
                    self.unicode = self.get_unicode_for_glyphname(base)
            self._updateInfo(self.unicode, fake)

    @objc.python_method
    def includeOptional(self, sender=None):
        if sender is None:
            return

        self.include_optional = sender.get()
        self._updateOrthographies()

    @objc.python_method
    def get_orthography_glyph_list(self, orthography, font, markers=True):
        if markers:
            glyph_list = ["_BASE_"]
        else:
            glyph_list = []

        base = get_expanded_glyph_list(
            orthography.unicodes_base, ui=self.info
        )
        base = self.get_extra_names(font, base)
        glyph_list.extend([
            self.get_glyphname_for_unicode(u)[0]
            for u, n in sorted(base)
        ])

        punc = get_expanded_glyph_list(
            orthography.unicodes_punctuation, ui=self.info
        )
        punc = self.get_extra_names(font, punc)
        if markers:
            glyph_list.append("_PUNCT_")
        if punc:
            glyph_list.extend([
                self.get_glyphname_for_unicode(u)[0]
                for u, n in sorted(punc)
            ])

        if self.include_optional:
            optn = get_expanded_glyph_list(
                orthography.unicodes_optional, ui=self.info
            )
            optn = self.get_extra_names(font, optn)
            if markers:
                glyph_list.append("_OPTIONAL_")
            if optn:
                glyph_list.extend(
                    [
                        self.get_glyphname_for_unicode(u)[0]
                        for u, n in sorted(optn)
                        if self.get_glyphname_for_unicode(u)[0] not in glyph_list
                    ]
                )
        if markers:
            glyph_list.append("_END_")
        return glyph_list

    @objc.python_method
    def showOrthography(self, sender=None):
        # Callback for the "Show" button of the Orthographies list
        if sender is None:
            return

        i = self.w.orthography_list.get()
        if i < 0:
            return

        items = self.w.orthography_list.getItems()
        if i < len(items):
            font = self.font_fallback
            if font is None:
                return

            orthography = self.ortho_list[i]
            glyph_list = self.get_orthography_glyph_list(orthography, font)

            self._saveGlyphSelection(font)
            self._showGlyphList(font, glyph_list)
            self._restoreGlyphSelection(font)
        # Set the selection to the same index as before
        self.selectOrthography(sender=None, index=i)
        self.w.reset_filter.enable(True)
        self.filtered = True
        self.w.show_block.enable(False)
        self.w.show_orthography.enable(False)

    @objc.python_method
    def get_block_glyph_list(self, block, font, markers=True, reserved=True):
        if markers:
            glyph_list = ["_START_"]
        else:
            glyph_list = []
        tuples = [
            (cp, self.get_glyphname_for_unicode(cp)[0])
            for cp in get_codepoints(block)
            if reserved or cp in uniName
        ]
        names = self.get_extra_names(font, tuples)
        names.sort()
        glyph_list.extend([n[1] for n in names])
        if markers:
            glyph_list.append("_END_")
        return glyph_list

    @objc.python_method
    def showBlock(self, sender=None):
        # Callback for the "Show" button of the Unicode blocks list
        if sender is None:
            return

        i = self.w.block_list.get()
        if i <= 0:
            return

        items = self.w.block_list.getItems()
        if i < len(items):
            font = self.font_fallback
            if font is None:
                return

            block = items[i]
            glyph_list = self.get_block_glyph_list(block, font, reserved=True)

            # Update status
            missing = self.get_missing_glyphs_for_block(block, font)
            is_supported = len(missing) == 0
            self.w.block_status.set(is_supported)
            self.w.block_add_missing.enable(not is_supported)

            self._saveGlyphSelection(font)
            self._showGlyphList(font, glyph_list)
            self._restoreGlyphSelection(font)
        self.w.reset_filter.enable(True)
        self.filtered = True
        self.w.show_block.enable(False)
        self.w.show_orthography.enable(False)

    @objc.python_method
    def toggleCase(self, sender=None):
        pass

    @objc.python_method
    def reassignUnicodes(self, sender=None):
        if self.font is not None:
            unicodes = {g.unicode: g.name for g in self.font if g.unicode}
            for g in self.font:
                myUnicode = self.get_unicode_for_glyphname(g.name)
                if g.unicode != myUnicode:
                    print("%s:" % g.name, end="")
                    if g.unicode is not None:
                        print("%x ->" % g.unicode, end="")
                    else:
                        print("<None> ->", end="")
                    if myUnicode is not None:
                        print("%x" % myUnicode, end="")
                    else:
                        print("<None>", end="")
                    if myUnicode in unicodes:
                        print(
                            "-- Ignored: already in use (/%s)."
                            % unicodes[myUnicode]
                        )
                    else:
                        print()
                        g.unicode = myUnicode
                        unicodes[myUnicode] = g.name
