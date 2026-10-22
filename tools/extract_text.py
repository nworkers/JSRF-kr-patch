"""Extract every on-screen Japanese string of the dump, with its place, to work/ (design 20261021-i011).

Writes, under the output folder (default work/text, must be under work/):
  <group>.tsv           file, where, orig_len, orig_sha1, pad, kind, ref,
                        japanese, english -- HOLDS ORIGINAL TEXT: never commit
  skeleton/<group>.tsv  the patch/text format (file, where, orig_len,
                        orig_sha1, korean, pad) with korean empty and no
                        original text; fill korean to make a text patch
  summary.txt           the counts printed at the end
Groups: event (Media/Event/Event/e###.dat item 2/0 pages), talk
(Media/Event/TalkEvent/TE###.bin pages), mission (Media/Mission/mssn####.bin
language-0 strings), xbe (default.xbe .rdata strings). Tabs, newlines and
backslashes inside text are written as \\t \\n \\\\.

Every place is read back through the patcher's place resolution before
anything is written; the default.xbe must be the US build (the patch base; its .rdata strings sit at the
same addresses as the Japanese build's).

usage: python -I tools/extract_text.py <game dir> [--out <folder under work/>]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import ROOT, extract  # noqa: E402
from jsrfkr.xbe import US_MD5, Xbe  # noqa: E402

WORK_ROOT = os.path.join(ROOT, "work")
WORK_COLUMNS = ("file", "where", "orig_len", "orig_sha1", "pad", "kind", "ref", "japanese", "english")
SKELETON_COLUMNS = ("file", "where", "orig_len", "orig_sha1", "korean", "pad")
# The record rule of tools/analysis/text_codes.py (text-renderer.md's 2,933 records).
OLD_GROUPS = (("Event/Event/*.dat", "event"), ("Event/TalkEvent/*.bin", "talk"),
              ("Mission/*.bin", "mission .bin"), ("Mission/*.dat", "mission .dat"))
OLD_RECORD = re.compile(rb"(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x09\x20-\x7e])+(?=\x00)")


def text(b, bad):
    if b is None:
        return ""
    try:
        s = b.decode("cp932")
    except UnicodeDecodeError:
        s = b.decode("cp932", "backslashreplace")
        bad.append(b)
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def write_tsv(path, comments, columns, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for c in comments:
            f.write(f"# {c}\n")
        f.write("\t".join(columns) + "\n")
        for r in rows:
            f.write("\t".join(str(v) for v in r) + "\n")


def old_records(game):
    import glob
    out = []
    for pattern, label in OLD_GROUPS:
        n = 0
        for path in glob.glob(os.path.join(game, "Media", pattern)):
            with open(path, "rb") as f:
                n += sum(1 for m in OLD_RECORD.finditer(f.read()) if b"$e" in m.group())
        out.append((label, n))
    return out


def main():
    args = sys.argv[1:]
    out = os.path.join(WORK_ROOT, "text")
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            raise SystemExit("--out needs a folder")
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1 or args[0].startswith("-"):
        raise SystemExit(__doc__)
    game, out = args[0], os.path.abspath(out)
    if not (out + os.sep).startswith(WORK_ROOT + os.sep):
        raise SystemExit(f"{out}: the output must be a folder under {WORK_ROOT} (it holds original text)")
    xbe_path = os.path.join(game, extract.XBE)
    if not os.path.isfile(xbe_path):
        raise SystemExit(f"{xbe_path}: not found (give the dump folder that holds default.xbe and Media)")
    x = Xbe(xbe_path)
    if x.md5 != US_MD5:
        raise SystemExit(f"{xbe_path}: MD5 {x.md5} is not the US default.xbe the patch is based on ({US_MD5})")

    by_group, census = extract.units(game, x)
    checked = extract.check(game, x, by_group)

    bad, lines = [], []
    for group in extract.GROUPS:
        us = by_group[group]
        write_tsv(os.path.join(out, f"{group}.tsv"),
                  [f"tools/extract_text.py, group {group}, from default.xbe {x.md5}",
                   "HOLDS ORIGINAL TEXT FROM THE DUMP: keep it under work/, never commit or share it"],
                  WORK_COLUMNS,
                  [(u.file, u.where, u.orig_len, u.orig_sha1, u.pad, u.kind, u.ref,
                    text(u.japanese, bad), text(u.english, bad)) for u in us])
        write_tsv(os.path.join(out, "skeleton", f"{group}.tsv"),
                  [f"Translation skeleton, group {group} (tools/extract_text.py). No original text.",
                   "Fill the korean column; an empty korean keeps the original. Keep $ codes as in work/text."],
                  SKELETON_COLUMNS,
                  [(u.file, u.where, u.orig_len, u.orig_sha1, "", u.pad) for u in us])
        size = sum(u.orig_len for u in us)
        lines.append(f"{group:8} files {census.files[group]:4}  records {census.records[group]:5}  "
                     f"units {len(us):5}  bytes {size:7}  left out {census.skipped[group]:5}")
    total = sum(len(v) for v in by_group.values())
    data_refs, code_refs, stray, unref = census.notes["xbe"]
    old = old_records(game)
    lines += [
        f"total    units {total}, every place checked against the dump ({checked})",
        f"xbe references: {data_refs} .data pointer slots, {code_refs} push immediates, "
        f"{stray} other byte matches in .text, {unref} strings without a reference",
        f"event items 2/0 without text: {census.notes.get('event_other', 0)}",
        f"undecodable strings (written with \\x escapes): {len(bad)}",
        "text-renderer.md record rule (NUL-terminated, holds $e): "
        + ", ".join(f"{label} {n}" for label, n in old) + f" = {sum(n for _, n in old)}",
        f"  comparable: event scripts {census.records['event']} (real records among the event ones); "
        f"mission language-0 strings with $e {census.notes.get('mission_e0', 0)}",
    ]
    with open(os.path.join(out, "summary.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {out} (holds original text: never commit it; skeleton/ holds none)")


if __name__ == "__main__":
    main()
