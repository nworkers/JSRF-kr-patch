"""Steps shared by tools/patch.py and tools/check_text.py (design 20261021-i015 §4).

  font_for(x, jetfont, rows)   the new glyph table and jetfont.dat for the
                               Hangul in the rows (tools/font/build_font.py);
                               raises ValueError when the syllables do not fit
  encode(rows, font, x)        rows -> reinsert.Change list, plus the error
                               message of every row that cannot be encoded
  single_widths(x)             single-byte advances for the screen checks
"""
import build_font      # tools/font, on sys.path through jsrfkr
import font_tables     # tools/analysis, on sys.path through jsrfkr

from . import reinsert, screen, textpatch
from .encode import Encoder


def font_for(x, jetfont, rows, ident=False):
    return build_font.build(x, jetfont, None if ident else "".join(r.korean for r in rows))


def hangul_count(font):
    return sum(1 for e in font.entries if e.syllable)


def encode(rows, font, x):
    encoder = Encoder.for_xbe(font.codes(), x)
    changes, errors = [], []
    for r in rows:
        try:
            changes.append(reinsert.Change(r, textpatch.encode_row(r, encoder)))
        except textpatch.PatchError as err:
            errors.append(str(err))
    return changes, errors


def single_widths(x):
    return screen.single_widths(font_tables.single_table(x))
