# -*- coding: utf-8 -*-
# Unicode Info
# editor-independent module
# Version 0.1 by Jens Kutilek 2016-10-24
# Version 1.0 by Jens Kutilek 2017-01-19
# Version 1.1 by Jens Kutilek 2021-10-16

import vanilla
import jkUnicode
from jkUnicode.aglfn import getGlyphnameForUnicode, getUnicodeForGlyphname
from jkUnicode.uniBlock import get_block, get_codepoints, uniNameToBlock
from jkUnicode.uniName import uniName
try:
    from jkUnicode.orthography import OrthographyInfo
    orth_present = True
except ImportError:
    orth_present = False


def get_extensions(font):
    # Return all used glyph name extensions in the font
    return [n.split(".", 1)[1] for n in font.keys() if "." in n[1:]]


def get_extension_map(font):
    # Return a map of base glyph names to extension names for the font
    d = {}
    for g in font.keys():
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


def get_extra_names(font, uni_name_tuples):
    ext_map = get_extension_map(font)
    additions = []
    for u, n in uni_name_tuples:
        additions.extend([(u, e) for e in ext_map.get(n, [])])
    uni_name_tuples.extend(additions)
    return list(set(uni_name_tuples))


def get_unicode_for_glyphname(name=None):
    if name is None:
        return None
    # First try jkUnicode
    u = getUnicodeForGlyphname(name)
    if u is None:
        # then try GNFUL
        u = getGlyphNameComponentUnicode(name)
        if u is not None:
            u = u[1]
    return u


class UnicodeInfoWindow(object):
    def setup_window(self):
        width = 320
        if orth_present:
            height = 153
        else:
            height = 116
        ini_height = height - 16
        axis = 50

        self.w = vanilla.FloatingWindow(
            (width, ini_height),
            "Unicode Info",
            minSize=(width, height),
            maxSize=(530, height)
        )

        y = 10
        self.w.uni_name_label = vanilla.TextBox((8, y, axis-10, 20),
                                               "Name",
                                               sizeStyle="small")
        self.w.uni_name = vanilla.TextBox((axis, y, -10, 20),
                                               u"",
                                               sizeStyle="small")
        y += 20
        self.w.code_label = vanilla.TextBox((8, y, axis-10, 20),
                                               "Code",
                                               sizeStyle="small")
        self.w.code = vanilla.TextBox((axis, y, -10, 20),
                                               u"",
                                               sizeStyle="small")
        self.w.reassign_unicodes = vanilla.Button((-81, y-6 , -10, 25), "Assign All",
            callback=self.reassignUnicodes,
            sizeStyle="small",
        )
        y += 20
        self.w.glyph_name_label = vanilla.TextBox((8, y, axis-10, 20),
                                               "Glyph",
                                               sizeStyle="small")
        self.w.glyph_name = vanilla.TextBox((axis, y, -10, 20),
                                               u"",
                                               sizeStyle="small")
        self.w.case = vanilla.Button((-81, y-6, -10, 25), u"\u2191 \u2193 Case",
            callback=self.toggleCase,
            sizeStyle="small",
        )
        y += 20
        self.w.block_label = vanilla.TextBox((8, y, axis-10, 20),
                                               "Block",
                                               sizeStyle="small")
        self.w.block_list = vanilla.PopUpButton((axis, y-4, -90, 20),
                                               [],
                                               callback=self.selectBlock,
                                               sizeStyle="small")
        self.w.block_status = vanilla.CheckBox((-80, y-3, -70, 20),
                                               "",
                                               sizeStyle="small")
        self.w.show_block = vanilla.Button((-60, y-6 , -10, 25), "Show",
            callback=self.showBlock,
            sizeStyle="small",
        )
        if orth_present:
            y += 20
            self.w.orthography_label = vanilla.TextBox((8, y, axis-10, 20),
                                                   "Usage",
                                                   sizeStyle="small")
            self.w.orthography_list = vanilla.PopUpButton((axis, y-4, -90, 20),
                                                   [],
                                                   callback=self.selectOrthography,
                                                   sizeStyle="small")
            self.w.orthography_status = vanilla.CheckBox((-80, y-3, -70, 20),
                                                   "",
                                                   sizeStyle="small")
            self.w.show_orthography = vanilla.Button((-60, y-6 , -10, 25), "Show",
                callback=self.showOrthography,
                sizeStyle="small",
            )
            y += 20
            self.w.include_optional = vanilla.CheckBox((axis, y, 200, 20),
                "Include optional characters",
                callback=self.includeOptional,
                sizeStyle="small")
        

        self.font = CurrentFont()
        self.glyph = CurrentGlyph()
        
        self.setup_class()
        
        self.setUpBaseWindowBehavior()
        self.w.open()
        #self._updateInfo()
        addObserver(self, "_currentGlyphChanged", "currentGlyphChanged")


    def setup_class(self):
        
        self.info = jkUnicode.UniInfo(0)
        self.unicode = None
        if orth_present:
            self.ortho = OrthographyInfo()
            self.ortho_list = []
        self.case = None
        self.view = None
        self.include_optional = False
        self.w.reassign_unicodes.enable(False)
        self.w.block_list.setItems([""] + sorted(uniNameToBlock.keys()))
        self.w.show_block.enable(False)
        self.w.block_status.enable(False)
        self.w.case.enable(False)
        if orth_present:
            self.w.orthography_list.enable(False)
            self.w.show_orthography.enable(False)
            self.w.orthography_status.enable(False)
            if self.font is None:
                self.w.include_optional.enable(False)
            else:
                self.w.include_optional.enable(True)
    
    @property
    def font(self):
        return self._font
    
    @font.setter
    def font(self, value):
        self._font = value
        if self._font is not None:
            if orth_present:
                self.ortho.cmap = [g.unicode for g in self.font if g.unicode]
    
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
                    is_supported = self.ortho_list[i].support_full()
                else:
                    is_supported = self.ortho_list[i].support_basic()
                self.w.orthography_status.set(is_supported)
        else:
            self.w.orthography_status.set(False)
    
    
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
            #self.w.show_block.enable(False)
            self.w.block_status.set(False)
        else:
            #self.w.show_block.enable(True)
            # Show supported status for block
            #self.w.block_status.set(is_supported)
            pass
    

    def _updateInfo(self, u=None, fake=False):
        self._updateBlock(u)
        if u is None:
            self.w.uni_name.set(u"❓")
            self.w.code.set("")
            if self.glyph is None:
                self.w.glyph_name.set("")
            else:
                self.w.glyph_name.set(self.glyph.name)
            self.w.case.enable(False)
            self._updateOrthographies()
            return
        
        self.info.unicode = u
        self.gnful_name = GlyphName(uniNumber=u).getName()
        self.w.uni_name.set(self.info.name.title())
        if fake:
            self.w.code.set(u"😀 None")
            self.w.glyph_name.set(self.glyph.name)
            self.case = None
            self.w.case.enable(False)
        else:
            # Unicode
            if u == self.glyph.unicode:
                self.w.code.set(u"😀 %04X" % u)
            else:
                if self.glyph.unicode is None:
                    self.w.code.set(u"😡 None → %04X" % u)
                else:
                    self.w.code.set(u"😡 %04X → %04X" % (self.glyph.unicode, u))
            
            # Glyph name
            if self.glyph.name == self.info.glyphname:
                self.w.glyph_name.set(u"😀 %s" % self.info.glyphname)
            elif self.glyph.name == self.gnful_name:
                self.w.glyph_name.set(u"😀 %s (Product: %s)" % (self.gnful_name, self.info.glyphname))
            else:
                self.w.glyph_name.set(u"😡 %s → %s or %s" % (self.glyph.name, self.gnful_name, self.info.glyphname))
            
            # Case mapping
            lc = self.info.lc_mapping
            if lc is None:
                uc = self.info.uc_mapping
                if uc is None:
                    self.case = None
                    self.w.case.enable(False)
                else:
                    self.case = uc
                    if self.view is None:
                        self.w.case.enable(False)
                    else:
                        self.w.case.enable(True)
            else:
                self.case = lc
                if self.view is None:
                    self.w.case.enable(False)
                else:
                    self.w.case.enable(True)
        self._updateOrthographies()
    
    
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
                self.w.show_block.enable(True)
            else:
                self.w.block_list.set(0)
                self.w.show_block.enable(False)
        #self.selectBlock(name=block)
    
    
    def _updateOrthographies(self):
        if not orth_present:
            return
        # Save the old selection from the orthography list
        old_index = self.w.orthography_list.get()
        if old_index > -1:
            old_sel = self.ortho_list[self.w.orthography_list.get()].name
        else: old_sel = None
        new_index = 0
        
        # Check which orthographies use current unicode
        if self.glyph is None:
            # Show all
            self.ortho_list = [o for o in sorted(self.ortho.orthographies)]
        else:
            if self.include_optional:
                self.ortho_list = [o for o in sorted(self.ortho.get_orthographies_for_unicode_any(self.unicode))]
            else:
                self.ortho_list = [o for o in sorted(self.ortho.get_orthographies_for_unicode(self.unicode))]
        
        self.w.orthography_list.setItems([o.name for o in self.ortho_list])
        
        if len(self.ortho_list) == 0:
            self.w.orthography_list.enable(False)
            self.w.show_orthography.enable(False)
        else:
            self.w.orthography_list.enable(True)
            self.w.show_orthography.enable(True)
            # If the old name is in the new list, select it
            if old_sel is not None:
                names = self.w.orthography_list.getItems()
                if old_sel in names:
                    new_index = names.index(old_sel)
        
        self.selectOrthography(index=new_index)
    
    
    def _currentGlyphChanged(self, info):
        self.glyph = info["glyph"]
        self.view = info["view"]
        self.font = CurrentFont()
        if self.font is None:
            self.w.reassign_unicodes.enable(False)
            if orth_present: self.w.include_optional.enable(False)
            self.w.show_block.enable(False)
        else:
            self.w.reassign_unicodes.enable(True)
            if orth_present: self.w.include_optional.enable(True)
            self.w.show_block.enable(True)
        if self.glyph is None:
            self._updateInfo(None)
        else:
            self.unicode = self.glyph.unicode
            fake = False
            if self.unicode is None:
                if "." in self.glyph.name[1:]:
                    fake = True
                    base, ext = self.glyph.name.split(".", 1)
                    if self.font is None:
                        self.unicode = get_unicode_for_glyphname(base)
                    else:
                        if base in self.font:
                            self.unicode = self.font[base].unicode
                            if self.unicode is None:
                                self.unicode = get_unicode_for_glyphname(base)
                        else:
                            self.unicode = get_unicode_for_glyphname(base)
                else:
                    base = self.glyph.name
                    self.unicode = get_unicode_for_glyphname(base)
            self._updateInfo(self.unicode, fake)
    
    
    def includeOptional(self, sender=None):
        if sender is not None:
            self.include_optional = sender.get()
            self._updateOrthographies()
    
    
    def showOrthography(self, sender=None):
        # Callback for the "Show" button of the Orthographies list
        if sender is not None:
            i = self.w.orthography_list.get()
            if i > -1:
                items = self.w.orthography_list.getItems()
                if i < len(items):
                    orthography = self.ortho_list[i]
                    glyph_list = ["_BASE_"]
                    
                    base = jkUnicode.get_expanded_glyph_list(orthography.unicodes_base)
                    base = get_extra_names(self.font, base)
                    glyph_list.extend([t[1] for t in sorted(base)])
                    
                    punc = jkUnicode.get_expanded_glyph_list(orthography.unicodes_punctuation)
                    punc = get_extra_names(self.font, punc)
                    glyph_list.append("_PUNCT_")
                    if punc:
                        glyph_list.extend([t[1] for t in sorted(punc)])
                    
                    if self.include_optional:
                        optn = jkUnicode.get_expanded_glyph_list(orthography.unicodes_optional)
                        optn = get_extra_names(self.font, optn)
                        glyph_list.append("_OPTIONAL_")
                        if optn:
                            glyph_list.extend([t[1] for t in sorted(optn) if not t[1] in glyph_list])
                    glyph_list.append("_END_")
                    self.font.glyphOrder = glyph_list
                # Set the selection to the same index as before
                self.selectOrthography(sender=None, index=i)
    
    
    def showBlock(self, sender=None):
        # Callback for the "Show" button of the Unicode blocks list
        if sender is not None:
            i = self.w.block_list.get()
            if i > 0:
                items = self.w.block_list.getItems()
                if i < len(items):
                    block = items[i]
                    glyph_list = ["_START_"]
                    tuples = [(cp, getGlyphnameForUnicode(cp)) for cp in get_codepoints(block) if cp in uniName]
                    names = get_extra_names(self.font, tuples)
                    names.sort()
                    glyph_list.extend([n[1] for n in names])
                    glyph_list.append("_END_")
                    self.font.glyphOrder = glyph_list
    
    
    def toggleCase(self, sender=None):
        if self.view is None or self.font is None:
            return
        else:
            glyphname = getGlyphnameForUnicode(self.case)
            if glyphname in self.font:
                SetCurrentGlyphByName(glyphname)
    
    
    def reassignUnicodes(self, sender=None):
        if self.font is not None:
            unicodes = {g.unicode: g.name for g in self.font if g.unicode}
            for g in self.font:
                myUnicode = get_unicode_for_glyphname(g.name)
                if g.unicode != myUnicode:
                    print(f"{g.name}:", end=" ")
                    if g.unicode is not None:
                        print("%x ->" % g.unicode, end=" ")
                    else:
                        print("<None> ->", end=" ")
                    if myUnicode is not None:
                        print("%x" % myUnicode, end=" ")
                    else:
                        print("<None>", end=" ")
                    if myUnicode in unicodes:
                        print("-- Ignored: already in use (/%s)." % unicodes[myUnicode])
                    else:
                        print()
                        g.unicode = myUnicode
                        unicodes[myUnicode] = g.name
    
            
    def windowCloseCallback(self, sender):
        removeObserver(self, "currentGlyphChanged")
        super(UnicodeInfoUI, self).windowCloseCallback(sender)
 

#OpenWindow(UnicodeInfoUI)
