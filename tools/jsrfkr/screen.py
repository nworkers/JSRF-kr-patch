"""Screen-limit and structure checks for reinserted text (design 20261021-i013 §3.1, §3.4).

  structure   the page and branch codes ($r $e $p $b? $s $j $v, with their
              arguments) of a replacement must be those of the original, in
              order: page counts never change.
  page buffer each page (between $r) plus 5 bytes per line (the centring
              '$xNNN' the page parser adds) and a NUL must stay under 0x100
              bytes (JP 0xF9090 copies pages into 0x100-byte buffers). Error.
  width       pixels per line at scale 1, as the renderer draws (JP 0x3CF20):
              double-byte 24, space 21 * 0.532, single-byte width * 0.76 - 4
              (width from the table at 0x1F8640; 21 for fixed-width glyphs).
              Warning above the group limit.
  lines       lines per page. Warning above the group limit.
"""
from collections import namedtuple

from . import msgscript

PAGE_BUFFER = 0x100
CENTRE_BYTES = 5            # '$x' + three digits, added per line when centred
DOUBLE_ADVANCE = 24
SPACE_ADVANCE = 21 * 0.532
CELL_WIDTH = 21
# Window limits measured on the Japanese text (the widest line and most lines
# per page of each group); missions and XBE strings use their own original.
GROUP_WIDTH = {"event": 528, "talk": 456}
GROUP_LINES = {"event": 3, "talk": 3}
OTHER_WIDTH = 528
OTHER_LINES = 3
STRUCTURE = (b"$r", b"$e") + msgscript.CONTROL

Issue = namedtuple("Issue", "level message")     # level: 'error' or 'warning'


def structure(b):
    """The page and branch tokens of a string, in order."""
    return [t for t in msgscript.tokens(b) if t[:2] in STRUCTURE]


def pages(b):
    """Pages as lists of lines; each line a list of tokens."""
    out, page, line = [], [], []
    for t in msgscript.tokens(b):
        if t == b"$r":
            page.append(line)
            out.append(page)
            page, line = [], []
        elif t == b"$n":
            page.append(line)
            line = []
        else:
            line.append(t)
    page.append(line)
    out.append(page)
    return out


def single_widths(rows):
    """{byte: pixel advance} from font_tables.single_table rows (code, glyph+1, src_x, width)."""
    return {code: (CELL_WIDTH if src < 0 else width) * 0.76 - 4 for code, _, src, width in rows}


def line_width(tokens, single):
    w = 0.0
    for t in tokens:
        if t[:1] == b"$" and len(t) > 1:
            continue
        if len(t) == 2:
            w += DOUBLE_ADVANCE
        elif t == b" ":
            w += SPACE_ADVANCE
        else:
            w += single.get(t[0], CELL_WIDTH * 0.76 - 4)
    return w


def check(group, original, new, single):
    """Issues of a replacement `new` for `original` (both game bytes)."""
    issues = []
    if structure(new) != structure(original):
        issues.append(Issue("error", "page or branch codes ($r $e $p $b $s $j $v) differ from the original; "
                                     "page counts cannot change"))
    orig_pages = pages(original)
    width_limit = GROUP_WIDTH.get(group) or max(
        [OTHER_WIDTH] + [line_width(l, single) for p in orig_pages for l in p])
    lines_limit = GROUP_LINES.get(group) or max([OTHER_LINES] + [len(p) for p in orig_pages])
    for k, page in enumerate(pages(new)):
        size = sum(len(t) for line in page for t in line) + 2 * (len(page) - 1)
        if size + CENTRE_BYTES * len(page) + 1 >= PAGE_BUFFER:
            issues.append(Issue("error", f"page {k}: {size} bytes and {len(page)} lines overrun the "
                                         f"{PAGE_BUFFER:#x}-byte page buffer"))
        if len(page) > lines_limit:
            issues.append(Issue("warning", f"page {k}: {len(page)} lines (limit {lines_limit})"))
        for n, line in enumerate(page):
            w = line_width(line, single)
            if w > width_limit:
                issues.append(Issue("warning", f"page {k} line {n}: {w:.0f} px wide (limit {width_limit:.0f})"))
    return issues
