"""Measure the game's text records against the renderer's rules. Prints counts only.

For the event, talk and mission files (records = NUL-terminated strings that
hold `$e`, as in reJSRF scripts/analysis/text/text_records.py) this reports:

  * the `$` codes used, with digit arguments shown as '#'
  * double-byte codes missing from the XBE glyph table, and lead bytes >= 0xA0
    (which the renderer would read as two single-byte Latin-1 characters)
  * per Japanese line (split at $n and $r): the widest line in renderer pixels
    at scale 1 (double-byte advance 24 px, as in JP 0x3CF20)
  * per Japanese page (split at $r): the longest page in bytes (the page
    parser JP 0xF9090 copies each page into a 0x100-byte buffer)

No original text is printed, so the output may be quoted in documents.

usage: python -I tools/analysis/text_codes.py <game dir> <default.xbe>
"""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import font_tables  # noqa: E402
from xbe import Xbe  # noqa: E402

GROUPS = ["Event/Event/*.dat", "Event/TalkEvent/*.bin", "Mission/*.bin", "Mission/*.dat"]
STR = re.compile(rb"(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x09\x20-\x7e])+(?=\x00)")
TOKEN = re.compile(rb"[\x80-\x9f][\x00-\xff]|\$(?:b[a-z]|[a-z$])[0-9]*|[\x00-\xff]", re.S)
DBL_ADVANCE = 26 - 2       # cell 26 * scale, minus 2 * scale
SPACE_ADVANCE = 21 * 0.532 # 0x1F8B58 * 0x1CA488


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    game, xbe_path = sys.argv[1:]
    x = Xbe(xbe_path)
    table = {code for code, _ in font_tables.double_table(x) if code}
    codes, missing = collections.Counter(), collections.Counter()
    high_lead = records = 0
    widest = (0.0, "")
    longest_page = (0, "")
    for pattern in GROUPS:
        for path in glob.glob(os.path.join(game, "Media", pattern)):
            name = os.path.relpath(path, game)
            for m in STR.finditer(open(path, "rb").read()):
                s = m.group()
                if b"$e" not in s:
                    continue
                records += 1
                for t in TOKEN.findall(s):
                    if len(t) == 1 and t[0] >= 0xA0:
                        high_lead += 1
                    elif t[:1] == b"$":
                        codes[re.sub(rb"[0-9]", b"#", t).decode()] += 1
                    elif len(t) == 2 and (t[0] << 8 | t[1]) not in table:
                        missing[f"{t[0]:02X}{t[1]:02X}"] += 1
                japanese = s.split(b"$e")[0]
                for page in japanese.split(b"$r"):
                    if len(page) > longest_page[0]:
                        longest_page = (len(page), name)
                    for line in page.split(b"$n"):
                        w = 0.0
                        for t in TOKEN.findall(line):
                            if t[:1] == b"$":
                                continue
                            if len(t) == 2:
                                w += DBL_ADVANCE
                            elif t == b" ":
                                w += SPACE_ADVANCE
                            else:
                                w += 21 * 0.76 - 4   # default single-byte cell
                        if w > widest[0]:
                            widest = (w, name)
    print(f"records: {records}")
    print("codes:", ", ".join(f"{k} {v}" for k, v in codes.most_common()))
    print(f"double-byte codes not in the glyph table: {sum(missing.values())} "
          f"({', '.join(f'{k} x{v}' for k, v in missing.most_common(8))})")
    print(f"bytes >= 0xA0 read as single-byte Latin-1: {high_lead}")
    print(f"widest Japanese line: {widest[0]:.0f} px at scale 1 ({widest[0] / DBL_ADVANCE:.1f} "
          f"double-byte glyphs) in {widest[1]}")
    print(f"longest Japanese page: {longest_page[0]} bytes in {longest_page[1]}")


if __name__ == "__main__":
    main()
