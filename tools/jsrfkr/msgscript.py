"""Message scripts: event text items (e###.dat item 2/0) and talk events (TE###.bin).

Layout (analysis message-script.md), all u32 little-endian:
  head[9]          head[1] = L languages, head[4] = M messages per language;
                   the other values are kept as read
  fields[5][L][M]  five arrays in this order, each language-major;
                   fields[0][l][m] = page count of message m in language l
  values[L*M][..]  one u32 per page, for (l, m) in language-major order
  text             the pages of every (l, m) in the same order, each page
                   followed by '$r', running to the end of the data (no NUL)

A page is the bytes between two '$r' tokens. Tokens follow the renderer:
lead bytes 0x80-0x9F take one trail byte, and '$' codes take their argument
bytes ('$b?' and '$s' arguments are binary page numbers). build() writes a
Script back from its values; page counts are taken from the pages, so a
Script whose pages changed can be rebuilt once its per-page values match.
"""
import struct
from collections import namedtuple

HEAD = 9
FIELDS = 5
PAGE_END = b"$r"
# Argument bytes after '$' + letter (text-renderer.md §6); '$b' takes a
# second letter and one binary byte, handled apart.
ARGS = {"c": 1, "x": 3, "g": 2, "s": 2, "j": 1, "v": 1, "f": 1, "m": 1, "h": 1, "o": 2}
CONTROL = (b"$p", b"$b", b"$s", b"$j", b"$v")   # pages with these steer, they are not shown

Page = namedtuple("Page", "offset data")   # offset: from the start of the script data


class FormatError(ValueError):
    pass


def tokens(b):
    """Split bytes into renderer tokens: double-byte characters, '$' codes with
    their arguments, and single bytes."""
    out, i, n = [], 0, len(b)
    while i < n:
        c = b[i]
        if 0x80 <= c <= 0x9F and i + 1 < n:
            size = 2
        elif c == 0x24 and i + 1 < n:
            k = chr(b[i + 1])
            size = 4 if k == "b" else 2 + ARGS.get(k, 0)
        else:
            size = 1
        out.append(b[i:i + size])
        i += size
    return out


def is_control(page):
    """A branch or choice page ('$p', '$b?', '$s' ...): steers, is not shown."""
    return any(t[:2] in CONTROL for t in tokens(page))


def has_letters(page):
    """Anything left once '$' codes and spaces (single 0x20, double 0x8140) are removed."""
    return any(not (t[:1] == b"$" and len(t) > 1) and t not in (b" ", b"\x81\x40") for t in tokens(page))


class Script:
    def __init__(self, head, fields, values, pages):
        self.head, self.fields, self.values = list(head), fields, values
        self.pages = pages          # pages[l][m] = [Page, ...]

    @property
    def languages(self):
        return self.head[1]

    @property
    def messages(self):
        return self.head[4]

    def block(self, lang):
        """All pages of a language, messages in order. Branch arguments
        ('$bj', '$bo', '$s') count pages from 0 in this list."""
        return [p for m in self.pages[lang] for p in m]


def parse(data):
    """Parse a whole message script; raises FormatError when the page counts do
    not account for the text exactly."""
    data = bytes(data)
    if len(data) < 4 * HEAD:
        raise FormatError("shorter than the header")
    head = list(struct.unpack_from(f"<{HEAD}I", data, 0))
    L, M = head[1], head[4]
    if not (1 <= L <= 16 and 1 <= M <= 64):
        raise FormatError(f"{L} languages x {M} messages")
    pos = 4 * HEAD

    def words(n):
        nonlocal pos
        if pos + 4 * n > len(data):
            raise FormatError("header runs past the end")
        v = list(struct.unpack_from(f"<{n}I", data, pos))
        pos += 4 * n
        return v

    fields = []
    for _ in range(FIELDS):
        flat = words(L * M)
        fields.append([flat[l * M:(l + 1) * M] for l in range(L)])
    counts = fields[0]
    values = [words(counts[l][m]) for l in range(L) for m in range(M)]
    text_start = pos
    toks = tokens(data[pos:])
    pages, k = [], 0
    for l in range(L):
        lang = []
        for m in range(M):
            msg = []
            for _ in range(counts[l][m]):
                start, body = pos, []
                while k < len(toks) and toks[k] != PAGE_END:
                    body.append(toks[k])
                    pos += len(toks[k])
                    k += 1
                if k == len(toks):
                    raise FormatError(f"language {l} message {m}: text ends before page {len(msg)}")
                msg.append(Page(start, b"".join(body)))
                pos += 2
                k += 1
            lang.append(msg)
        pages.append(lang)
    if pos != len(data):
        raise FormatError(f"{len(data) - pos} bytes after the last page (text starts at {text_start:#x})")
    return Script(head, fields, values, pages)


def build(script):
    """The bytes of a script; page counts come from its pages."""
    L, M = script.languages, script.messages
    fields = [[list(row) for row in f] for f in script.fields]
    fields[0] = [[len(script.pages[l][m]) for m in range(M)] for l in range(L)]
    out = bytearray(struct.pack(f"<{HEAD}I", *script.head))
    for f in fields:
        for l in range(L):
            out += struct.pack(f"<{M}I", *f[l])
    for i, v in enumerate(script.values):
        l, m = divmod(i, M)
        if len(v) != fields[0][l][m]:
            raise ValueError(f"language {l} message {m}: {len(v)} page values for {fields[0][l][m]} pages")
        out += struct.pack(f"<{len(v)}I", *v)
    for l in range(L):
        for m in range(M):
            for p in script.pages[l][m]:
                out += p.data + PAGE_END
    return bytes(out)
