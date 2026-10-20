"""Fixed mapping between KS X 1001 Hangul syllables and the game's double-byte codes.

The k-th KS X 1001 syllable (in Unicode order, which is also KS order) gets the
k-th code of the sequence that starts at 0x8890 and skips second bytes outside
0x40-0x7E / 0x80-0xFC. All these codes are class 4 for the renderer (>= 0x8890)
and have lead bytes below 0xA0. First: U+AC00 -> 0x8890; last: U+D79D -> 0x94ED.
"""

FIRST_CODE = 0x8890


def _ks_syllables():
    out = []
    for cp in range(0xAC00, 0xD7A4):
        try:
            if len(chr(cp).encode("euc_kr")) == 2:   # longer = KS X 1001 make-up sequence
                out.append(chr(cp))
        except UnicodeEncodeError:
            pass
    return out


def _codes(n):
    out = []
    for lead in range(FIRST_CODE >> 8, 0xA0):
        for trail in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            code = lead << 8 | trail
            if code >= FIRST_CODE:
                out.append(code)
                if len(out) == n:
                    return out
    raise ValueError("code space exhausted")


SYLLABLES = _ks_syllables()                     # 2,350
CODES = _codes(len(SYLLABLES))
CODE_OF = dict(zip(SYLLABLES, CODES))
SYLLABLE_OF = dict(zip(CODES, SYLLABLES))


def is_hangul_syllable(ch):
    return "가" <= ch <= "힣"


def collect(text):
    """(KS syllables used, sorted by code; other Hangul syllables found)."""
    used = {ch for ch in text if is_hangul_syllable(ch)}
    ok = sorted((ch for ch in used if ch in CODE_OF), key=CODE_OF.get)
    bad = sorted(ch for ch in used if ch not in CODE_OF)
    return ok, bad
