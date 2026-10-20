"""Decode the jetfont glyph tables that the text renderer reads from default.xbe.

The renderer object (JP/US 0x3C000-0x3D790) never computes a glyph cell from
the Shift-JIS value. It searches a code table in .data and uses the table
index as the cell number:

  double-byte table  0x1F7088: 0x56E entries of (u16 code, u16 index+1)
  single-byte table  0x1F8640: 0x9C entries of (u16 code, u16 glyph+1,
                               s16 src_x, s16 width)   (-1 = default cell)
  font descriptors   0x1F8B20 (double-byte) and 0x1F8B48 (single-byte),
                     0x28 bytes each: pages, first texture, texture size,
                     cells per page, cell w/h, columns, rows, UV step w/h
  class bounds       0x1F8B70: u16 code bounds of the five double-byte classes
  class bases        0x1F8B80: table index where each class starts
  single-byte bias   0x1F8B7A/0x1F8B7C/0x1F8B98: search start for a byte

Prints the layout and a summary. With --tsv, also writes the full map
(index, page, row, col, code) to a file; that file is derived from game data
and belongs in work/, never in the repository.

usage: python -I tools/analysis/font_tables.py <default.xbe> [--tsv work/font_map.tsv]
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from jsrfkr.xbe import JP_MD5, US_MD5, Xbe  # noqa: E402

DBL_TABLE = 0x1F7088
DBL_COUNT = 0x56E          # also an immediate in the class-0 search (JP 0x3C7AC)
SGL_TABLE = 0x1F8640
SGL_COUNT = 0x9C           # immediate in the single-byte search (JP 0x3C883, 0x3C8A0)
DESC_DBL = 0x1F8B20
DESC_SGL = 0x1F8B48
CLASS_BOUNDS = 0x1F8B70
CLASS_BASES = 0x1F8B80
CLASS_NAMES = ["symbols", "digits+Latin", "hiragana", "katakana", "kanji"]


def descriptor(x, va):
    return {
        "pages": x.u32(va), "first_texture": x.u32(va + 4), "texture_size": x.f32(va + 8),
        "cells_per_page": x.u32(va + 0xC), "cell_w": x.f32(va + 0x10), "cell_h": x.f32(va + 0x14),
        "columns": x.u32(va + 0x18), "rows": x.u32(va + 0x1C),
        "uv_w": x.f32(va + 0x20), "uv_h": x.f32(va + 0x24),
    }


def class_ranges(x):
    """(class, first code, end code, first index, count) as the lookup code uses them."""
    bounds = [x.u16(CLASS_BOUNDS + 2 * i) for i in range(5)]   # 0, 8240, 829F, 8340, 8890
    bases = [x.u32(CLASS_BASES + 4 * i) for i in range(4)]     # symbols, Latin, hira, kata
    # Counts exactly as 0x3C790 derives them; class 4 (kanji) starts at 0
    # and its count is the hiragana base (0x1F8B88).
    counts = [DBL_COUNT - bases[0], bases[0] - bases[1], bases[3] - bases[2], bases[1] - bases[3]]
    out = []
    for c in range(4):
        lo = 0x8140 if c == 0 else bounds[c]
        out.append((c, lo, bounds[c + 1], bases[c], counts[c]))
    out.append((4, bounds[4], 0x10000, 0, bases[2]))
    return out


def double_table(x):
    return [struct.unpack("<HH", x.read(DBL_TABLE + 4 * i, 4)) for i in range(DBL_COUNT)]


def single_table(x):
    return [struct.unpack("<HHhh", x.read(SGL_TABLE + 8 * i, 8)) for i in range(SGL_COUNT)]


def main():
    args = sys.argv[1:]
    tsv = None
    if "--tsv" in args:
        i = args.index("--tsv")
        tsv = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__)
    x = Xbe(args[0])
    build = {JP_MD5: "JP", US_MD5: "US"}.get(x.md5, "unknown")
    print(f"{args[0]}: MD5 {x.md5} ({build})")

    dd, sd = descriptor(x, DESC_DBL), descriptor(x, DESC_SGL)
    print(f"double-byte font descriptor {DESC_DBL:#x}: {dd}")
    print(f"single-byte font descriptor {DESC_SGL:#x}: {sd}")

    dbl = double_table(x)
    ids_ok = all(e[1] == i + 1 for i, e in enumerate(dbl))
    empty = [i for i, e in enumerate(dbl) if e[0] == 0]
    capacity = dd["pages"] * dd["cells_per_page"]
    print(f"\ndouble-byte table {DBL_TABLE:#x}: {len(dbl)} entries, second field == index+1: {ids_ok}")
    print(f"  cells: {capacity} ({dd['pages']} pages x {dd['columns']}x{dd['rows']}), "
          f"table uses {len(dbl)}, empty (code 0) entries: {len(empty)}"
          + (f" (index {empty[0]}..{empty[-1]})" if empty else ""))
    lead = sorted({e[0] >> 8 for e in dbl if e[0]})
    print(f"  lead bytes used: {lead[0]:#x}..{lead[-1]:#x}; codes with lead >= 0xA0: "
          f"{sum(1 for e in dbl if e[0] >> 8 >= 0xA0)}")
    for c, lo, hi, base, count in class_ranges(x):
        seg = dbl[base:base + count]
        inside = sum(1 for e in seg if e[0] == 0 or lo <= e[0] < hi)
        print(f"  class {c} {CLASS_NAMES[c]:<12} codes {lo:04X}-{hi - 1:04X} -> index {base}..{base + count - 1}"
              f" ({count} entries, {inside} inside the code range)")

    sgl = single_table(x)
    custom = sum(1 for e in sgl if e[2] != -1)
    print(f"\nsingle-byte table {SGL_TABLE:#x}: {len(sgl)} entries, codes "
          f"{sgl[0][0]:#x}..{sgl[-1][0]:#x}, glyphs {min(e[1] for e in sgl)}..{max(e[1] for e in sgl)}, "
          f"custom src_x/width: {custom}")
    print(f"  search start: byte - {x.u16(0x1F8B7A):#x} (byte < 0x80), "
          f"byte - {x.u16(0x1F8B7C):#x} + {x.u32(0x1F8B98)} (byte >= 0x80)")

    if tsv:
        with open(tsv, "w", encoding="utf-8", newline="\n") as f:
            f.write("index\tpage\trow\tcol\tcode\n")
            per = dd["cells_per_page"]
            for i, (code, _) in enumerate(dbl):
                page, rem = divmod(i, per)
                row, col = divmod(rem, dd["columns"])
                f.write(f"{i}\t{page}\t{row}\t{col}\t{code:04X}\n")
        print(f"\nwrote {tsv} (derived from game data: keep it in work/)")


if __name__ == "__main__":
    main()
