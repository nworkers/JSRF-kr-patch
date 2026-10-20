"""Korean text -> the game's string bytes (design 20261020-i008 §2).

  * Hangul syllables use the fixed KS X 1001 mapping of tools/font/hangul.py
    (two-byte codes from 0x8890), and must be in the new glyph table.
  * Other characters are encoded as cp932 (Shift-JIS). A two-byte result must
    be a code the new glyph table still holds (kept symbols, digits, Latin
    capitals, kana); a one-byte result must be the space (drawn as an advance
    only) or a code in the single-byte table (JP 0x1F8640).
  * `$` control codes are plain single-byte characters here ('$' and the
    letters and digits after it are all in the single-byte table).
"""
import font_tables
import hangul


class Encoder:
    def __init__(self, double_codes, single_codes):
        self.double = set(double_codes)
        self.single = set(single_codes) | {0x20}

    @classmethod
    def for_xbe(cls, double_codes, xbe):
        """An encoder for the new double-byte codes and the XBE's single-byte table."""
        return cls(double_codes, {c for c, *_ in font_tables.single_table(xbe)})

    def encode(self, text):
        out, bad = bytearray(), []
        for ch in text:
            if hangul.is_hangul_syllable(ch):
                code = hangul.CODE_OF.get(ch)
                if code is None or code not in self.double:
                    bad.append(ch)
                    continue
                out += bytes((code >> 8, code & 0xFF))
                continue
            try:
                b = ch.encode("cp932")
            except UnicodeEncodeError:
                bad.append(ch)
                continue
            if len(b) == 2 and (b[0] << 8 | b[1]) in self.double:
                out += b
            elif len(b) == 1 and b[0] in self.single:
                out += b
            else:
                bad.append(ch)
        if bad:
            raise ValueError("characters not in the glyph table: " + " ".join(f"U+{ord(c):04X}" for c in bad))
        return bytes(out)
