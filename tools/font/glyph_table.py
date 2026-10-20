"""Build the new double-byte glyph table for option A' (design 20261020-i006 §2).

Layout of the 0x56E entries (front to back):
  Hangul (class 4, code order) | empty padding (code 0) | hiragana | katakana
  | digits + Latin | symbols (ends at 0x56E, the class-0 immediate at 0x3C7AC)
Symbols and digits/Latin always stay ($g writes full-width digits directly);
kana stay when there is room. The table cannot grow: 0x1F7088 + 0x56E*4 is
exactly where the single-byte table 0x1F8640 begins.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
import font_tables  # noqa: E402

TOTAL = font_tables.DBL_COUNT               # 1,390
TABLE_VA = font_tables.DBL_TABLE            # 0x1F7088
BASES_VA = font_tables.CLASS_BASES          # 0x1F8B80: symbols, Latin, hiragana, katakana


class Entry:
    """One table slot: code, plus where its picture comes from."""

    def __init__(self, code, source=None, syllable=None):
        self.code = code            # 0 = empty
        self.source = source        # index of the original cell to copy, or None
        self.syllable = syllable    # Hangul syllable to draw, or None


def original_groups(xbe):
    """Original (index, code) runs of the kept classes, read through the class bases."""
    table = font_tables.double_table(xbe)
    groups = {}
    for c, _, _, base, count in font_tables.class_ranges(xbe):
        groups[c] = [(i, table[i][0]) for i in range(base, base + count)]
    return groups


def capacity(keep_kana):
    g = 27 + 36 + (83 + 86 if keep_kana else 0)
    return TOTAL - g


def build(xbe, hangul_codes):
    """hangul_codes: list of (code, syllable) in code order. Returns (entries, bases, keep_kana)."""
    groups = original_groups(xbe)
    sym, latin, hira, kata = groups[0], groups[1], groups[2], groups[3]
    if (len(sym), len(latin), len(hira), len(kata)) != (27, 36, 83, 86):
        raise ValueError("unexpected original class sizes; not the Japanese table?")
    n = len(hangul_codes)
    keep_kana = n <= capacity(True)
    if n > capacity(False):
        raise ValueError(f"{n} Hangul syllables do not fit: at most {capacity(False)} "
                         f"({capacity(True)} with kana kept)")
    kanji = capacity(keep_kana)
    entries = [Entry(code, syllable=s) for code, s in hangul_codes]
    entries += [Entry(0) for _ in range(kanji - n)]
    hira_base = len(entries)
    if keep_kana:
        entries += [Entry(code, source=i) for i, code in hira]
    kata_base = len(entries)
    if keep_kana:
        entries += [Entry(code, source=i) for i, code in kata]
    latin_base = len(entries)
    entries += [Entry(code, source=i) for i, code in latin]
    sym_base = len(entries)
    entries += [Entry(code, source=i) for i, code in sym]
    assert len(entries) == TOTAL
    bases = (sym_base, latin_base, hira_base, kata_base)
    return entries, bases, keep_kana


def identity(xbe):
    """The original table as entries (for the round-trip test)."""
    table = font_tables.double_table(xbe)
    entries = [Entry(code, source=i) for i, (code, _) in enumerate(table)]
    bases = tuple(xbe.u32(BASES_VA + 4 * k) for k in range(4))
    return entries, bases


def table_bytes(entries):
    return b"".join(struct.pack("<HH", e.code, i + 1) for i, e in enumerate(entries))


def bases_bytes(bases):
    return struct.pack("<4I", *bases)
