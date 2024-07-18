# UnicodeInfo-Glyphs

A Unicode and orthography info window for Glyphs.app.

Bring up the Unicode Info window via _Window > Unicode Info._

![](images/screenshot.png)

When a glyph is selected, or you are editing a glyph, glyph name, Unicode, and usage information is displayed in the Unicode Info window.


## Glyph Names and Unicode Codepoints

The top section shows the Unicode name of the current glyph, as well as the codepoint and the expected glyph name. If there is a mismatch, the smiley will look angry.

- **W** will search Wikipedia for the character.

- **Assign All** assigns Unicodes to all glyphs based on their names. When you use the automatic naming in Glyphs, this should never be necessary.

- **↑↓ Case** jumps to the corresponding uppercase or lowercase version of the current glyph. In the _Edit_ view, your current glyph will be exchanged with the cased version. In the _Font_ view, the selection is changed from the current glyph to the cased glyph.


## Unicode Block Information

Under _Block,_ the Unicode block which the current character belongs to is shown. An empty/half-filled/filled circle next to the block name indicates the support level of your font for this block (no/some/all characters present).

- **Show** can only be used in the _Font_ view and shows all characters your font contains from the selected Unicode block at the top of the _Font_ view. Before you can show another block, you must press **Reset Filter.**

- **Fill Block** adds placeholder glyphs for all missing characters of the selected block to your font.


## Orthography Information

Under _Source,_ you can select whether you want orthography information based on [Hyperglot](https://hyperglot.rosettatype.com) or the [Unicode CLDR](https://cldr.unicode.org).

If you check **Include optional characters,** those will be taken into account for the _Show_ and _Fill_ operations, and for determining the orthography support.

Under _Usage,_ the dropdown contains a list of all orthographies that use the current character. An empty/half-filled/filled circle next to the orthography name indicates the support level of your font for this orthography (no/basic/optional characters present).

- **Show** can only be used in the _Font_ view and shows all characters your font contains from the selected orthography at the top of the _Font_ view. Before you can show another orthography, you must press **Reset Filter.**

- **Fill Orth.** adds placeholder glyphs for all missing characters of the selected orthography to your font.

Whenever you select an orthography that is not fully supported, a list of missing codepoints is printed to the console of the _Macro_ panel.

## Known issues

- When "custom naming" is active, or with automatic names, but not up-to-date glyph info, the results of the _Fill_ buttons are unreliable and may lead to duplicate glyphs.

© 2016–2024 by Jens Kutilek, Tim Ahrens
