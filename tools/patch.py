"""Build the Korean-patched game folder from the user's Japanese dump (design 20261021-i002).

  1. checks   the output is under out/ and empty; patch/manifest.json MD5s
              (the Japanese default.xbe, jetfont.dat, every file the text
              patches touch) match the dump. Nothing is written on a mismatch.
  2. font     new glyph table and jetfont.dat for the Hangul in the text
  3. text     in-place replacement of each place in patch/text/*.tsv
  4. XBE      glyph table, patch/xbe/*.json, va: places, section digests
  5. output   the whole dump folder copied, changed files written anew
              (--link: unchanged files hard-linked; editing them then edits
              the dump too); --iso also writes <out>.iso, a copy of the
              user's xiso with the changed files overwritten at the same size
  6. md5.txt  MD5 of every changed file (the same input gives the same values)

--identity uses the original glyph table and no text or XBE patches (round
trip: the output folder must equal the dump; check with
tools/check_roundtrip.py --output). --update-manifest records the dump's MD5
for every file the text patches touch (the Japanese default.xbe must match).

usage: python -I tools/patch.py <game dir> <out dir under out/> [--text f|dir] [--iso xiso]
                                [--link] [--identity]
       python -I tools/patch.py <game dir> --update-manifest [--text f|dir]
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import ROOT, textpatch, xbepatch, xiso  # noqa: E402
from jsrfkr.digest import ManifestError, check_inputs, load_manifest, md5, md5_file, write_manifest  # noqa: E402
from jsrfkr.encode import Encoder  # noqa: E402
from jsrfkr.xbe import Xbe, fix_digests  # noqa: E402
import build_font  # noqa: E402  (tools/font, on sys.path through jsrfkr)

XBE = "default.xbe"
JETFONT = "Media/Font/jetfont.dat"
PATCH = os.path.join(ROOT, "patch")
MANIFEST = os.path.join(PATCH, "manifest.json")
OUT_ROOT = os.path.join(ROOT, "out")


def take_opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        if i + 1 >= len(args):
            raise SystemExit(f"{name} needs a value")
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def take_flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


def read_text(text_path):
    try:
        return textpatch.read_rows(textpatch.text_files(text_path))
    except (OSError, textpatch.PatchError) as err:
        raise SystemExit(str(err))


def update_manifest(game, rows):
    manifest = load_manifest(MANIFEST)
    target = manifest["target"]
    if md5_file(os.path.join(game, target["file"])) != target["md5"]:
        raise SystemExit(f"{target['file']}: not the Japanese build the manifest targets")
    names = {XBE, JETFONT} | {r.file for r in rows}
    added = []
    for name in sorted(names):
        path = os.path.join(game, name)
        if not os.path.isfile(path):
            raise SystemExit(f"{name}: not in the dump")
        value = md5_file(path)
        if manifest["inputs"].get(name) not in (None, value):
            raise SystemExit(f"{name}: the manifest has {manifest['inputs'][name]}, the dump {value}")
        if name not in manifest["inputs"]:
            manifest["inputs"][name] = value
            added.append(name)
    write_manifest(MANIFEST, manifest)
    print(f"manifest: {len(added)} added" + "".join(f"\n  {n}" for n in added))


def check_out(out):
    if not (out + os.sep).startswith(OUT_ROOT + os.sep) or out == OUT_ROOT:
        raise SystemExit(f"{out}: the output must be a folder under {OUT_ROOT} (it holds game data)")
    if os.path.exists(out) and (not os.path.isdir(out) or os.listdir(out)):
        raise SystemExit(f"{out}: exists and is not an empty folder")


def build_files(game, rows, xbe_patches, ident):
    """Changed files: dump path -> bytes."""
    x = Xbe(os.path.join(game, XBE))
    with open(os.path.join(game, JETFONT), "rb") as f:
        jf = f.read()
    text = None if ident else "".join(r.korean for r in rows)
    font = build_font.build(x, jf, text)
    image = build_font.apply_table(x, font)
    files = {XBE: image, JETFONT: bytearray(font.jetfont)}
    sections = {".data"}

    def load(name):
        with open(os.path.join(game, name), "rb") as f:
            return f.read()

    try:
        touched, done = textpatch.apply(rows, files, load, Encoder.for_xbe(font.codes(), x), x)
        sections |= touched
        sections |= xbepatch.apply(xbe_patches, x, image)
    except (textpatch.PatchError, xbepatch.XbePatchError) as err:
        raise SystemExit(str(err))
    fix_digests(x, image, sorted(sections))
    for row, n in done:
        print(f"  {row.file} {textpatch.format_where(row)}: {n}/{row.orig_len} bytes")
    hangul = sum(1 for e in font.entries if e.syllable)
    print(f"text: {len(rows)} places; glyphs: {hangul} Hangul, kana kept: {font.keep_kana}; "
          f"XBE patches: {len(xbe_patches)}; XBE sections: {', '.join(sorted(sections))}")
    return {name: bytes(data) for name, data in files.items()}


def write_output(game, out, files, link):
    copied = 0
    for d, _, names in os.walk(game):
        rel_dir = os.path.relpath(d, game)
        os.makedirs(os.path.join(out, rel_dir), exist_ok=True)
        for n in names:
            rel = os.path.normpath(os.path.join(rel_dir, n)).replace("\\", "/")
            target = os.path.join(out, rel)
            if rel in files:
                with open(target, "wb") as f:
                    f.write(files[rel])
            elif link:
                try:
                    os.link(os.path.join(d, n), target)
                except OSError as err:
                    raise SystemExit(f"{rel}: hard link failed ({err}); run without --link to copy")
                copied += 1
            else:
                shutil.copyfile(os.path.join(d, n), target)
                copied += 1
    missing = sorted(set(files) - {os.path.relpath(os.path.join(d, n), out).replace("\\", "/")
                                   for d, _, ns in os.walk(out) for n in ns})
    if missing:
        raise SystemExit(f"changed files not in the dump folder: {', '.join(missing)}")
    return copied


def write_iso(src, dst, files, game):
    with xiso.Image(src) as img:
        for name in files:
            if md5(img.read(name)) != md5_file(os.path.join(game, name)):
                raise SystemExit(f"{src}: {name} differs from the dump folder")
    print(f"copying {src} -> {dst}")
    shutil.copyfile(src, dst)
    with xiso.Image(dst, "r+b") as img:
        for name, data in files.items():
            img.replace(name, data)
    return md5_file(dst)


def main():
    args = sys.argv[1:]
    ident = take_flag(args, "--identity")
    link = take_flag(args, "--link")
    update = take_flag(args, "--update-manifest")
    iso = take_opt(args, "--iso")
    text_path = take_opt(args, "--text", os.path.join(PATCH, "text"))
    if update:
        if len(args) != 1 or ident or link or iso:
            raise SystemExit(__doc__)
        update_manifest(args[0], read_text(text_path))
        return
    if len(args) != 2:
        raise SystemExit(__doc__)
    game, out = args[0], os.path.abspath(args[1])
    check_out(out)
    iso_out = out + ".iso"
    if iso and os.path.exists(iso_out):
        raise SystemExit(f"{iso_out}: already exists")

    rows = [] if ident else read_text(text_path)
    try:
        xbe_patches = [] if ident else xbepatch.load(os.path.join(PATCH, "xbe"))
        manifest = load_manifest(MANIFEST)
        check_inputs(manifest, game, {XBE, JETFONT} | {r.file for r in rows})
    except (ManifestError, xbepatch.XbePatchError) as err:
        raise SystemExit(f"input check failed:\n{err}")
    if manifest["target"]["file"] != XBE:
        raise SystemExit(f"manifest target {manifest['target']['file']} is not {XBE}")
    if rows:
        print(f"text from {os.path.relpath(text_path, ROOT)}:")

    files = build_files(game, rows, xbe_patches, ident)
    copied = write_output(game, out, files, link)
    lines = []
    for name in sorted(files):
        orig = md5_file(os.path.join(game, name))
        new = md5(files[name])
        lines.append(f"{new}  {name}")
        print(f"{name}: {new} (original {orig}{', same' if new == orig else ''})")
    with open(os.path.join(out, "md5.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{'linked' if link else 'copied'} {copied} unchanged files")
    if iso:
        value = write_iso(iso, iso_out, files, game)
        same = ident and value == md5_file(iso)
        print(f"{os.path.basename(iso_out)}: {value}{' (same as the input xiso)' if same else ''}")
    print(f"wrote {out} (holds game data: never commit it)")


if __name__ == "__main__":
    main()
