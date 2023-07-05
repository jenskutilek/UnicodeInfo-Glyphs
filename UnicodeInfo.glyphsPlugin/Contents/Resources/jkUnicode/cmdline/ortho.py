#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from fontTools.ttLib import TTFont
from jkUnicode.orthography import OrthographyInfo


class OrthoCmdLine:
    def __init__(self, font_path, args) -> None:
        self.o = OrthographyInfo()
        self.o.cmap = self.get_cmap(font_path)
        if args.support:
            self.o.report_missing(
                codes=args.support,
                minimum=args.minimum,
                punctuation=args.punctuation,
                bcp47=args.bcp47,
            )
        elif args.punctuation:
            self.o.report_missing_punctuation(bcp47=args.bcp47)
        elif args.near_miss:
            self.o.report_near_misses(args.near_miss[0], bcp47=args.bcp47)
        elif args.minimum:
            self.o.report_supported_minimum(bcp47=args.bcp47)
        elif args.minimum_inclusive:
            self.o.report_supported_minimum_inclusive(bcp47=args.bcp47)
        elif args.full_only:
            self.o.report_supported(full_only=True, bcp47=args.bcp47)
        elif args.kill_list:
            self.o.report_kill_list(bcp47=args.bcp47)
        else:
            self.o.report_supported(full_only=False, bcp47=args.bcp47)

    def get_cmap(self, font_path):
        # Get a cmap from a given font path
        f = TTFont(font_path)
        cmap = f.getBestCmap()
        f.close()
        return cmap


def ortho():
    parser = argparse.ArgumentParser(
        description="Query fonts about orthographic support."
    )
    parser.add_argument(
        "-b",
        "--bcp47",
        action="store_true",
        default=False,
        help="Output orthographies as BCP47 language subtags",
    )
    parser.add_argument(
        "-f",
        "--full-only",
        action="store_true",
        default=False,
        help="Report only orthographies that are supported with all optional characters",
    )
    parser.add_argument(
        "-i",
        "--minimum-inclusive",
        action="store_true",
        default=False,
        help="Report orthographies that have at minimum basic support",
    )
    parser.add_argument(
        "-k",
        "--kill-list",
        action="store_true",
        default=False,
        help="Output a list of letters that don't appear together in any supported orthography.",
    )
    parser.add_argument(
        "-m",
        "--minimum",
        action="store_true",
        default=False,
        help="Report orthographies that have only basic support, i.e. no optional characters and no punctuation present",
    )
    parser.add_argument(
        "-p",
        "--punctuation",
        action="store_true",
        default=False,
        help="Report missing punctuation for otherwise supported orthographies",
    )
    parser.add_argument(
        "-n",
        "--near-miss",
        type=int,
        nargs=1,
        help="Report almost supported orthographies with maximum number of missing characters",
    )
    parser.add_argument(
        "-s",
        "--support",
        type=str,
        nargs=1,
        help="List Unicode characters missing from font to support the provided BCP47 language code",
    )
    parser.add_argument("font", type=str, nargs="+", help="One or more fonts")

    args = parser.parse_args()

    for font_path in args.font:
        OrthoCmdLine(font_path, args)


if __name__ == "__main__":
    ortho()
