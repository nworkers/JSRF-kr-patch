"""Build the Korean jetfont.dat and glyph table (option A', design 20261020-i006).

Reads the user's dump (Japanese default.xbe and Media/Font/jetfont.dat, both
MD5-checked) and a UTF-8 text whose Hangul syllables need glyphs, and writes
to the output folder (which must be under work/; everything written derives
from game data):

  jetfont.dat      double-byte pages rebuilt in the new table order
  default.xbe      the XBE with the new table, class bases and .data digest
  layout.tsv       index, page, row, col, code, kind, syllable
  texN.png         alpha previews of the four double-byte pages

--identity rebuilds with the original table instead (round-trip test: the
output jetfont.dat and default.xbe must equal the originals).

usage: python -I tools/font/build_font.py <game dir> <text.txt> <out dir> [--identity] [--font f.ttf]
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import jsrfkr  # noqa: E402,F401  (puts tools/analysis on sys.path)
import dxt3  # noqa: E402
import glyph_table  # noqa: E402
import hangul  # noqa: E402
import jetfont  # noqa: E402
import ttf  # noqa: E402
from jsrfkr.xbe import JP_MD5, fix_digests, load_checked  # noqa: E402

DEFAULT_FONT = os.path.join(HERE, "..", "..", "patch", "font", "DoHyeon-Regular.ttf")
CELL, COLS, PER_PAGE, PAGES, PAGE_W = 26, 19, 361, 4, 512
# Ink box of the original kanji (measured: x 2..23, y 3..22).
BOX_X, BOX_Y, BOX_W, BOX_H = 2, 3, 22, 20


def md5(b):
    return hashlib.md5(b).hexdigest()


def cell_origin(i):
    page, rem = divmod(i, PER_PAGE)
    row, col = divmod(rem, COLS)
    return page, row * CELL, col * CELL


class Renderer:
    """Draws syllables with one scale for all 2,350, so a syllable always looks the same."""

    def __init__(self, path):
        self.font = ttf.Font(path)
        missing = [s for s in hangul.SYLLABLES if not self.font.glyph_index(s)]
        if missing:
            raise SystemExit(f"{path}: {len(missing)} KS X 1001 syllables missing (first {missing[0]})")
        boxes = [ttf.bbox(self._polys(s)) for s in hangul.SYLLABLES]
        self.x0 = min(b[0] for b in boxes)
        self.y0 = min(b[1] for b in boxes)
        self.x1 = max(b[2] for b in boxes)
        self.y1 = max(b[3] for b in boxes)
        self.scale = min(BOX_W / (self.x1 - self.x0), BOX_H / (self.y1 - self.y0))
        self.dx = BOX_X + (BOX_W - (self.x1 - self.x0) * self.scale) / 2
        self.dy = BOX_Y + (BOX_H - (self.y1 - self.y0) * self.scale) / 2

    def _polys(self, s):
        return ttf.flatten(self.font.contours(self.font.glyph_index(s)))

    def cell(self, s):
        def tr(x, y):
            return self.dx + (x - self.x0) * self.scale, self.dy + (self.y1 - y) * self.scale
        cov = ttf.rasterize(self._polys(s), CELL, CELL, tr)
        return bytearray(min(15, int(c * 15 + 0.5)) for c in cov)


def load_inputs(game):
    """The MD5-checked Japanese XBE and jetfont.dat bytes from a dump folder."""
    xbe_path = os.path.join(game, "default.xbe")
    if not os.path.exists(xbe_path) or md5(open(xbe_path, "rb").read()) != JP_MD5:
        xbe_path = os.path.join(game, "default_jpn.xbe")
    x = load_checked(xbe_path, JP_MD5, "Japanese XBE")
    font_file = os.path.join(game, "Media", "Font", "jetfont.dat")
    jf = open(font_file, "rb").read()
    if md5(jf) != jetfont.JETFONT_MD5:
        raise SystemExit(f"{font_file}: MD5 {md5(jf)} is not {jetfont.JETFONT_MD5}")
    return x, jf


class Font:
    """Result of build(): new jetfont.dat bytes, the table entries and class bases."""

    def __init__(self, jf, entries, bases, keep_kana, pages, renderer, border_ink):
        self.jetfont, self.entries, self.bases, self.keep_kana = jf, entries, bases, keep_kana
        self.pages, self.renderer, self.border_ink = pages, renderer, border_ink

    def codes(self):
        """Double-byte codes the renderer can find in the new table."""
        return {e.code for e in self.entries[:glyph_table.TOTAL] if e.code}


def build(x, jf, text=None, font_path=DEFAULT_FONT):
    """Rebuild the double-byte pages for the Hangul in `text` (None = identity round trip)."""
    recs = jetfont.records(jf)[:PAGES]
    old_pages = [dxt3.decode_alpha(jf[r["offset"]:r["offset"] + r["size"]], PAGE_W, PAGE_W) for r in recs]
    if any(dxt3.colour_blocks(jf[r["offset"]:r["offset"] + r["size"]]) != {dxt3.WHITE_BLOCK} for r in recs):
        raise SystemExit("unexpected colour blocks in jetfont.dat")

    if text is None:
        entries, bases = glyph_table.identity(x)
        # The cells past the table on page 3 are copied too.
        entries += [glyph_table.Entry(0, source=i) for i in range(len(entries), PAGES * PER_PAGE)]
        keep_kana = True
        renderer = None
    else:
        used, bad = hangul.collect(text)
        if bad:
            raise SystemExit("syllables outside KS X 1001: " + " ".join(f"U+{ord(c):04X}" for c in bad))
        try:
            entries, bases, keep_kana = glyph_table.build(x, [(hangul.CODE_OF[s], s) for s in used])
        except ValueError as err:
            raise SystemExit(str(err))
        renderer = Renderer(font_path)

    pages = [bytearray(PAGE_W * PAGE_W) for _ in range(PAGES)]
    border_ink = 0
    for i, e in enumerate(entries):
        page, oy, ox = cell_origin(i)
        if e.source is not None:
            sp, sy, sx = cell_origin(e.source)
            for r in range(CELL):
                a = (sy + r) * PAGE_W + sx
                pages[page][(oy + r) * PAGE_W + ox:(oy + r) * PAGE_W + ox + CELL] = old_pages[sp][a:a + CELL]
        elif e.syllable:
            img = renderer.cell(e.syllable)
            border_ink += sum(1 for k in range(CELL * CELL)
                              if img[k] and (k % CELL in (0, CELL - 1) or k // CELL in (0, CELL - 1)))
            for r in range(CELL):
                pages[page][(oy + r) * PAGE_W + ox:(oy + r) * PAGE_W + ox + CELL] = img[r * CELL:(r + 1) * CELL]

    new_jf = bytearray(jf)
    for r, img in zip(recs, pages):
        enc = dxt3.encode_alpha(img, PAGE_W, PAGE_W)
        assert len(enc) == r["size"]
        new_jf[r["offset"]:r["offset"] + r["size"]] = enc
    return Font(new_jf, entries, bases, keep_kana, pages, renderer, border_ink)


def apply_table(x, font, image=None):
    """Write the new glyph table and class bases into an XBE image (same VAs in JP and US)."""
    image = bytearray(x.data) if image is None else image
    tb = glyph_table.table_bytes(font.entries[:glyph_table.TOTAL])
    bb = glyph_table.bases_bytes(font.bases)
    to, bo = x.offset(glyph_table.TABLE_VA), x.offset(glyph_table.BASES_VA)
    image[to:to + len(tb)] = tb
    image[bo:bo + len(bb)] = bb
    fix_digests(x, image, [".data"])
    return image


def main():
    args = sys.argv[1:]
    ident = "--identity" in args
    if ident:
        args.remove("--identity")
    font_path = DEFAULT_FONT
    if "--font" in args:
        i = args.index("--font")
        font_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 3:
        raise SystemExit(__doc__)
    game, text_path, out = args
    x, jf = load_inputs(game)
    text = None if ident else open(text_path, encoding="utf-8").read()
    font = build(x, jf, text, font_path)
    new_jf, entries = font.jetfont, font.entries
    new_xbe = apply_table(x, font)

    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "jetfont.dat"), "wb").write(new_jf)
    open(os.path.join(out, "default.xbe"), "wb").write(new_xbe)
    with open(os.path.join(out, "layout.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("index\tpage\trow\tcol\tcode\tkind\tsyllable\n")
        for i, e in enumerate(entries[:glyph_table.TOTAL]):
            page, oy, ox = cell_origin(i)
            kind = "hangul" if e.syllable else ("kept" if e.source is not None and e.code else "empty")
            f.write(f"{i}\t{page}\t{oy // CELL}\t{ox // CELL}\t{e.code:04X}\t{kind}\t{e.syllable or ''}\n")
    for n, img in enumerate(font.pages):
        jetfont.write_png(os.path.join(out, f"tex{n}.png"), bytearray(v * 17 for v in img), PAGE_W, PAGE_W)

    n_hangul = sum(1 for e in entries if e.syllable)
    print(f"mode: {'identity (round trip)' if ident else 'Korean'}; Hangul {n_hangul}, kana kept: {font.keep_kana}, "
          f"class bases (sym, Latin, hira, kata) = {font.bases}")
    if font.renderer:
        print(f"font {os.path.basename(font_path)}: scale {font.renderer.scale:.5f} px/unit, "
              f"ink on cell borders: {font.border_ink} px")
    print(f"jetfont.dat {md5(new_jf)} (original {md5(jf)}{', same' if new_jf == jf else ''})")
    print(f"default.xbe {md5(new_xbe)} (original {x.md5}{', same' if bytes(new_xbe) == x.data else ''})")
    print(f"wrote {out} (derived from game data: keep it under work/)")


if __name__ == "__main__":
    main()
