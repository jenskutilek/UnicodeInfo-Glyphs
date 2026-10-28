from unittest import TestCase

from unicodeinfowindow import get_extension_map, get_extra_names


class UnicodeInfoWindowTests(TestCase):
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
