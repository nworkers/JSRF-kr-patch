"""Build the proof-of-concept Korean patch (issue #8, design 20261020-i008).

Reads the user's Japanese dump folder, the matching xiso and the US XBE, and
patch/poc/lines.tsv; writes under out/ (everything written holds game data):

  <out>/files/...          the changed files (default.xbe, jetfont.dat, mission files)
  <out>/jsrf-kr-poc.iso    a copy of the xiso with those files overwritten in place (xemu)
  <out>/rejsrf/            US default.xbe with the same glyph table (US build of reJSRF,
                           REJSRF_LANGUAGE=Japanese), the patched Japanese XBE as
                           default_jpn.xbe (Japanese build, --xbe default_jpn.xbe), and
                           Media with unchanged files as hard links

Lines are replaced in place: the Korean bytes must fit in the original string,
the rest is filled with NUL, and the original bytes must match orig_sha1.

--identity builds with the original glyph table and no lines (round trip:
every output must equal its original).

usage: python -I tools/poc/build_poc.py <game dir> <xiso> <out dir under out/>
           [--us-xbe f] [--lines f] [--identity] [--skip-iso] [--skip-rejsrf]
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "font"))
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))
sys.path.insert(0, HERE)
import build_font  # noqa: E402
import glyph_table  # noqa: E402
import xiso  # noqa: E402
from encode import Encoder  # noqa: E402
from xbe import load_checked  # noqa: E402

US_MD5 = "f4e366bfdceee551a09f42219c90d84e"
XBE = "default.xbe"
JETFONT = "Media/Font/jetfont.dat"


def md5(b):
    return hashlib.md5(b).hexdigest()


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        header = None
        for raw in f:
            raw = raw.rstrip("\r\n")
            if not raw or raw.startswith("#"):
                continue
            cols = raw.split("\t")
            if header is None:
                header = cols
                continue
            rows.append(dict(zip(header, cols)))
    return rows


def take_opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def take_flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


def apply_lines(x, rows, encoder, files, game):
    """Replace each line in place; returns the XBE sections touched."""
    sections = set()
    for row in rows:
        name = row["file"]
        if name not in files:
            files[name] = bytearray(open(os.path.join(game, name), "rb").read())
        data = files[name]
        kind, value = row["where"].split(":")
        if kind == "va":
            if name != XBE:
                raise SystemExit(f"{name}: va: places are for {XBE} only")
            va = int(value, 16)
            off = x.offset(va)
            sections.add(x.section_at(va).name)
        else:
            off = int(value, 16)
        n = int(row["orig_len"])
        if hashlib.sha1(data[off:off + n]).hexdigest() != row["orig_sha1"] or data[off + n] != 0:
            raise SystemExit(f"{name} {row['where']}: original bytes do not match orig_sha1")
        try:
            enc = encoder.encode(row["korean"])
        except ValueError as err:
            raise SystemExit(f"{name} {row['where']}: {err}")
        if len(enc) > n:
            raise SystemExit(f"{name} {row['where']}: Korean is {len(enc)} bytes, more than {n}")
        data[off:off + n] = enc + bytes(n - len(enc))
        print(f"  {name} {row['where']}: {len(enc)}/{n} bytes")
    return sections


def build_iso(src, dst, files, game):
    with xiso.Image(src) as img:
        for name in files:
            if md5(img.read(name)) != md5_file(os.path.join(game, name)):
                raise SystemExit(f"{src}: {name} differs from the dump folder")
    print(f"copying {src} -> {dst}")
    shutil.copyfile(src, dst)
    with xiso.Image(dst, "r+b") as img:
        for name, data in files.items():
            img.replace(name, bytes(data))


def build_rejsrf(dst, game, us_image, files):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    open(os.path.join(dst, XBE), "wb").write(us_image)
    open(os.path.join(dst, "default_jpn.xbe"), "wb").write(files[XBE])
    media = os.path.join(game, "Media")
    links = 0
    for d, _, names in os.walk(media):
        rel_dir = os.path.relpath(d, game)
        os.makedirs(os.path.join(dst, rel_dir), exist_ok=True)
        for n in names:
            rel = os.path.join(rel_dir, n).replace("\\", "/")
            target = os.path.join(dst, rel)
            if rel in files and rel != XBE:
                open(target, "wb").write(files[rel])
            else:
                try:
                    os.link(os.path.join(d, n), target)
                except OSError:
                    shutil.copyfile(os.path.join(d, n), target)
                links += 1
    return links


def main():
    args = sys.argv[1:]
    ident = take_flag(args, "--identity")
    skip_iso = take_flag(args, "--skip-iso")
    skip_rejsrf = take_flag(args, "--skip-rejsrf")
    lines_path = take_opt(args, "--lines", os.path.join(ROOT, "patch", "poc", "lines.tsv"))
    us_path = take_opt(args, "--us-xbe")
    if len(args) != 3:
        raise SystemExit(__doc__)
    game, iso, out = args
    out = os.path.abspath(out)
    if not out.startswith(os.path.join(ROOT, "out") + os.sep):
        raise SystemExit(f"{out}: the output must be under {os.path.join(ROOT, 'out')} (it holds game data)")
    us_path = us_path or os.path.join(game, "default_eng.xbe")

    x, jf = build_font.load_inputs(game)
    rows = [] if ident else read_lines(lines_path)
    text = None if ident else "".join(r["korean"] for r in rows)
    font = build_font.build(x, jf, text)
    files = {XBE: build_font.apply_table(x, font), JETFONT: font.jetfont}
    if rows:
        print(f"{len(rows)} lines from {os.path.relpath(lines_path, ROOT)}:")
        touched = apply_lines(x, rows, Encoder(font.codes(), x), files, game)
        build_font.fix_digests(x, files[XBE], sorted(touched | {".data"}))
    print(f"glyphs: {sum(1 for e in font.entries if e.syllable)} Hangul, kana kept: {font.keep_kana}")

    os.makedirs(out, exist_ok=True)
    for name, data in files.items():
        path = os.path.join(out, "files", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").write(data)
        orig = md5_file(os.path.join(game, name)) if name != XBE else x.md5
        print(f"{name}: {md5(data)} (original {orig}{', same' if md5(data) == orig else ''})")

    if not skip_rejsrf:
        us = load_checked(us_path, US_MD5, "US XBE")
        for va, n in ((glyph_table.TABLE_VA, glyph_table.TOTAL * 4), (glyph_table.BASES_VA, 16)):
            if us.read(va, n) != x.read(va, n):
                raise SystemExit(f"US XBE: bytes at {va:#x} differ from the Japanese XBE")
        us_image = build_font.apply_table(us, font)
        links = build_rejsrf(os.path.join(out, "rejsrf"), game, us_image, files)
        print(f"rejsrf/default.xbe (US): {md5(us_image)} (original {us.md5}"
              f"{', same' if bytes(us_image) == us.data else ''}); Media: {links} hard links")

    if not skip_iso:
        dst = os.path.join(out, "jsrf-kr-poc.iso")
        build_iso(iso, dst, files, game)
        new = md5_file(dst)
        if ident:
            orig = md5_file(iso)
            print(f"jsrf-kr-poc.iso: {new} (original {orig}{', same' if new == orig else ''})")
        else:
            print(f"jsrf-kr-poc.iso: {new}")
    print(f"wrote {out} (holds game data: never commit it)")


if __name__ == "__main__":
    main()
