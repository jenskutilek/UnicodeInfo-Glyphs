from unittest import TestCase

from unicodeinfowindow import block_completeness, get_extension_map, get_extra_names


class UnicodeInfoWindowTests(TestCase):
    def test_block_completeness_full(self) -> None:
        codepoints = range(0x0100, 0x0180)
        assert block_completeness("Latin Extended-A", codepoints) == "●"

    def test_block_completeness_partial_1(self) -> None:
        codepoints = range(0x0100, 0x017F)
        assert block_completeness("Latin Extended-A", codepoints) == "◑"

    def test_block_completeness_partial_2(self) -> None:
        codepoints = range(0x0101, 0x0180)
        assert block_completeness("Latin Extended-A", codepoints) == "◑"

    def test_block_completeness_none(self) -> None:
        codepoints = [0x0099]
        assert block_completeness("Latin Extended-A", codepoints) == "○"

    def test_get_extension_map(self) -> None:
        glyph_names = ["a", "b", "c", "a.ss01", "b.ss02", "d.ss03", "a.ss01.sc"]
        assert get_extension_map(glyph_names) == {
            "a": {"a.ss01", "a.ss01.sc"},
            "b": {"b.ss02"},
            "c": set(),
            "d": {"d.ss03"},
        }

    def test_get_extra_names(self) -> None:
        glyph_names = ["a", "b", "c", "a.ss01", "b.ss02", "d.ss03", "a.ss01.sc"]
        assert get_extra_names(glyph_names, [(0x61, "a"), (0x62, "b")]) == {
            (0x61, "a"),
            (0x61, "a.ss01"),
            (0x61, "a.ss01.sc"),
            (0x62, "b"),
            (0x62, "b.ss02"),
        }
