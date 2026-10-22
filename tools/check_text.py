"""Check the translation files without building an output folder (design 20261021-i015 §4).

Runs the patcher's text steps in memory (glyph table, encoding, reinsertion,
screen checks) and reports, per translation file: rows translated, bytes,
strings appended or moved, errors and warnings, plus the distinct Hangul
syllables against the glyph-table limits. Every row's errors are collected
(each file is applied on its own, and a failing file row by row), so one run
lists everything to fix. Exits with 1 when there is an error.

--review also writes work/text/review/<file>.tsv: for every row the place,
status, byte counts, the Japanese and English (from tools/extract_text.py's
work/text/*.tsv), the Korean, and help that is not a translation: the
glossary terms in the line with their Korean forms, the codes the line must
keep, and the line limits. It holds original text: never commit it.

usage: python -I tools/check_text.py <game dir> [--text <file or folder>] [--review]
"""
import glob
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import ROOT, glossary, msgscript, pipeline, reinsert, screen, textpatch  # noqa: E402
from jsrfkr.xbe import US_MD5, Xbe  # noqa: E402

JETFONT = "Media/Font/jetfont.dat"
WORK = os.path.join(ROOT, "work", "text")
REVIEW_COLUMNS = ("file", "where", "ref", "status", "orig_len", "korean_len", "japanese", "english",
                  "korean", "terms", "codes", "limits", "notes")
FORMAT = re.compile(r"%[-+ #0-9.]*[a-zA-Z]")
KEEP_KANA, NO_KANA = 1158, 1327


def source_of(message):
    """The row source ('xbe.tsv:12') a message starts with."""
    return message.split(" ", 1)[0]


def codes_of(text):
    """The '$' codes and printf specifiers of a (decoded) line, in order."""
    b = text.encode("cp932", "replace")
    codes = [t.decode("ascii", "replace") for t in msgscript.tokens(b) if t[:1] == b"$" and len(t) > 1]
    return codes + FORMAT.findall(text)


def limits_of(group, japanese_bytes, single):
    if group in screen.GROUP_WIDTH:
        return f"{screen.GROUP_LINES[group]} lines/page, {screen.GROUP_WIDTH[group]} px/line"
    pages = screen.pages(japanese_bytes)
    width = max([screen.OTHER_WIDTH] + [screen.line_width(l, single) for p in pages for l in p])
    lines = max([screen.OTHER_LINES] + [len(p) for p in pages])
    return f"{lines} lines/page, {width:.0f} px/line"


def apply_file(changes, load, x, single):
    """Apply one file's changes; returns (done, warnings, errors)."""
    try:
        r = reinsert.apply(changes, {}, load, x, single)
        return r.done, r.warnings, []
    except textpatch.PatchError as err:
        first = str(err).splitlines()
    done, warnings, errors = [], [], []
    for ch in changes:
        try:
            r = reinsert.apply([ch], {}, load, x, single)
            done += r.done
            warnings += r.warnings
        except textpatch.PatchError as err:
            errors += str(err).splitlines()
    return done, warnings, list(OrderedDict.fromkeys(errors or first))


def progress(rows, done, errors, warnings):
    """Per translation file: OrderedDict name -> Counter."""
    by_source = {r.source: os.path.basename(r.source.rsplit(":", 1)[0]) for r in rows}
    stats = OrderedDict()
    for r in rows:
        c = stats.setdefault(by_source[r.source], Counter())
        c["rows"] += 1
        c["orig bytes"] += r.orig_len
        if r.korean:
            c["translated"] += 1
    for d in done:
        c = stats[by_source[d.row.source]]
        c["korean bytes"] += d.size
        c["moved"] += d.how in ("appended", "moved")
    for kind, messages in (("errors", errors), ("warnings", warnings)):
        for m in messages:
            name = by_source.get(source_of(m))
            if name:
                stats[name][kind] += 1
    return stats


def work_rows():
    """(file, where) -> (ref, japanese, english, group) from work/text/*.tsv."""
    out = {}
    for path in sorted(glob.glob(os.path.join(WORK, "*.tsv"))):
        group = os.path.splitext(os.path.basename(path))[0]
        header = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                cols = line.rstrip("\n").split("\t")
                if header is None:
                    header = cols
                    continue
                d = dict(zip(header, cols))
                out[(d["file"], d["where"])] = (d["ref"], d["japanese"], d.get("english", ""), group)
    return out


def unescape(s):
    return s.replace("\\t", "\t").replace("\\n", "\n").replace("\\\\", "\\")


def write_review(rows, done, errors, warnings, single, terms):
    known = work_rows()
    if not known:
        raise SystemExit(f"{WORK}: no extraction output; run tools/extract_text.py first")
    sizes = {d.row.source: d.size for d in done}
    notes = {}
    for level, messages in (("error", errors), ("warning", warnings)):
        for m in messages:
            notes.setdefault(source_of(m), []).append(f"{level}: {m.split(': ', 1)[-1]}")
    by_file = OrderedDict()
    for r in rows:
        name = os.path.splitext(os.path.basename(r.source.rsplit(":", 1)[0]))[0]
        where = textpatch.format_where(r)
        ref, ja, en, group = known.get((r.file, where), ("", "", "", reinsert.group_of(r) or ""))
        note = notes.get(r.source, [])
        status = ("error" if any(n.startswith("error") for n in note) else
                  "warning" if note else "done" if r.korean else "empty")
        ja_bytes = unescape(ja).encode("cp932", "replace")
        by_file.setdefault(name, []).append((
            r.file, where, ref, status, r.orig_len, sizes.get(r.source, ""), ja, en, r.korean,
            ", ".join(glossary.hints(unescape(ja), terms)), " ".join(codes_of(unescape(ja))),
            limits_of(group, ja_bytes, single), " | ".join(note)))
    out = os.path.join(WORK, "review")
    os.makedirs(out, exist_ok=True)
    for name, lines in by_file.items():
        with open(os.path.join(out, f"{name}.tsv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# tools/check_text.py --review. HOLDS ORIGINAL TEXT: keep it under work/, never commit it\n")
            f.write("\t".join(REVIEW_COLUMNS) + "\n")
            for line in lines:
                f.write("\t".join(str(v) for v in line) + "\n")
    return out


def main():
    args = sys.argv[1:]
    review = "--review" in args
    if review:
        args.remove("--review")
    text = os.path.join(ROOT, "patch", "text")
    if "--text" in args:
        i = args.index("--text")
        if i + 1 >= len(args):
            raise SystemExit("--text needs a file or folder")
        text = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1 or args[0].startswith("-"):
        raise SystemExit(__doc__)
    game = args[0]
    try:
        rows = textpatch.read_rows(textpatch.text_files(text))
    except (OSError, textpatch.PatchError) as err:
        raise SystemExit(str(err))
    x = Xbe(os.path.join(game, "default.xbe"))
    if x.md5 != US_MD5:
        raise SystemExit(f"default.xbe: MD5 {x.md5} is not the US build the patch is based on ({US_MD5})")
    with open(os.path.join(game, JETFONT), "rb") as f:
        jetfont = f.read()
    translated = textpatch.translated(rows)
    try:
        font = pipeline.font_for(x, jetfont, translated)
    except ValueError as err:
        raise SystemExit(f"error: {err}")
    changes, errors = pipeline.encode(translated, font, x)
    single = pipeline.single_widths(x)

    def load(name):
        with open(os.path.join(game, name), "rb") as f:
            return f.read()

    by_file = OrderedDict()
    for ch in changes:
        by_file.setdefault(ch.row.file, []).append(ch)
    done, warnings = [], []
    for name, cs in by_file.items():
        d, w, e = apply_file(cs, load, x, single)
        done, warnings, errors = done + d, warnings + w, errors + e

    for name, c in progress(rows, done, errors, warnings).items():
        print(f"{name}: {c['translated']}/{c['rows']} rows translated, Korean {c['korean bytes']} bytes "
              f"(original {c['orig bytes']} for all rows), {c['moved']} appended or moved, "
              f"{c['errors']} errors, {c['warnings']} warnings")
    n = pipeline.hangul_count(font)
    print(f"Hangul syllables: {n} (kana kept up to {KEEP_KANA}, at most {NO_KANA}); kana kept: {font.keep_kana}")
    for m in errors:
        print(f"error: {m}")
    for m in warnings:
        print(f"warning: {m}")
    if review:
        print(f"wrote {write_review(rows, done, errors, warnings, single, glossary.load())} "
              "(holds original text: never commit it)")
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
