from __future__ import annotations

import objc
from AppKit import NSClassFromString, NSImage
from Foundation import NSBundle


class UnicodeInfoWindow:
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
            callback=self.showWikiCharacter,
            bordered=False,
            sizeStyle="small",
        )
        self.w.reassign_unicodes = Button(
            (-72, y - 6, -10, 25),
            "Assign all",
            callback=self.reassignUnicodes,
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
            callback=self.toggleCase,
            sizeStyle="small",
        )
        y += 20
        self.w.block_label = TextBox((8, y, axis - 10, 20), "Block", sizeStyle="small")
        self.w.block_list = PopUpButton(
            (axis, y - 4, -101, 20),
            [],
            callback=self.selectBlock,
            sizeStyle="small",
        )
        self.w.show_block = Button(
            (-72, y - 6, -10, 25),
            "Show",
            callback=self.showBlock,
            sizeStyle="small",
        )
        y += 24
        self.w.database_label = TextBox(
            (8, y, axis - 5, 20), "Source", sizeStyle="small"
        )
        self.w.database_list = PopUpButton(
            (axis, y - 4, -101, 20),
            ["Hyperglot", "CLDR"],
            callback=self.selectDatabase,
            sizeStyle="small",
        )
        y += 16
        self.w.include_optional = CheckBox(
            (axis + 4, y, 200, 20),
            "Include optional characters",
            callback=self.includeOptional,
            sizeStyle="small",
        )
        y += 28
        self.w.orthography_label = TextBox(
            (8, y, axis - 10, 20), "Usage", sizeStyle="small"
        )
        self.w.orthography_list = PopUpButton(
            (axis, y - 4, -101, 20),
            [],
            callback=self.selectOrthography,
            sizeStyle="small",
        )
        self.w.wiki_orthography = ImageButton(
            (-94, y - 1.5, 16, 16),
            imageObject=wikipedia_icon,
            callback=self.showWikiOrthography,
            bordered=False,
            sizeStyle="small",
        )
        self.w.show_orthography = Button(
            (-72, y - 6, -10, 25),
            "Show",
            callback=self.showOrthography,
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
                callback=self.addMissingBlock,
                sizeStyle="small",
            )
            self.w.orthography_add_missing = Button(
                (axis + 76, y - 6, 72, 25),
                "Fill Orth.",
                callback=self.addMissingOrthography,
                sizeStyle="small",
            )
            self.w.reset_filter = Button(
                (-88, y - 6, -10, 25),
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
        block_list_ui_strings = [""]
        for block in self.blocks_in_popup[1:]:
            block_list_ui_strings.append(
                self.block_completeness(block, self.font_fallback) + " " + block
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
