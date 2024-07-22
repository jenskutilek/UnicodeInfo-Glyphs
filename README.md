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

If you check **Include optional characters,** those will be taken into account for the _Show_ and _Fill_ operations. What’s more, the drop-down list will also include orthographies for which the character is optional. Note: this checkbox does _not_ affect whether an orthography is considered unsupported, basic or fully supported.

Under _Usage,_ the dropdown contains a list of all orthographies that use the current character, with some additional information:

○ The font does not contain all basic characters. The orthography is not supported.

◑ The font contains all basic but not all optional characters.

● The font contains all basic and optional characters.

Note: the circle gives you information about the _font_. It is independent of the current character and independent of _Include optional characters_.

Whenever you select an orthography that is not fully supported, a list of missing codepoints is printed to the console of the _Macro_ panel.

**[optional]** means that the current character is optional for the orthography. Otherwise, the character is basic (i.e. essential).

- The **W** link opens the orthography in Wikipedia. You may want to do more research and decide for yourself how important a character is for a particular orthography.

- **Show** can only be used in the _Font_ view and shows all characters your font contains from the selected orthography at the top of the _Font_ view. Before you can show another orthography, you must press **Reset Filter.**

- The **number of speakers of a language** is combined from Hyperglot as well as CLDR. This number is independent of your selection of the source, and independent of the current character. Currently, this does not distinguish between different orthographies for a language and their use, as we do not have this information. If an orthography is not the default script for a language, however, this is indicated as “(non-default script)” in the list.

- The **number of speakers supported by the current character** is the sum of all orthographies with at least basic support (◑ or ●), for which the current character is not only optional. In other words, removing this character would make certain orthographies (with the indicated sum of speakers) unsupported. The message “⚠ This character does not help support any speakers” implies that there are only unsupported languages in the drop-down list. The character is practically of no use at the moment as it is only used in orthographies that your font does not support anyway. You should consider removing this character or adding the missing characters for unsupported orthographies.

- **Fill Orth.** adds placeholder glyphs for all missing characters of the selected orthography to your font.


## Known issues

- When "custom naming" is active, or with automatic names, but not up-to-date glyph info, the results of the _Fill_ buttons are unreliable and may lead to duplicate glyphs.

© 2016–2024 by Jens Kutilek, Tim Ahrens
