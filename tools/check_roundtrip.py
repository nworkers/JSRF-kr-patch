"""Round-trip checks on the user's dump (design 20261021-i002 §4). Prints no original text.

  * every MULT/NORM file under Media: parse, rebuild, compare byte for byte
  * default.xbe: recomputing every section digest leaves the image unchanged
  * with --output <folder>: every file of a patched folder against the dump
    (lists files that differ or are missing; use it on a --identity output)

usage: python -I tools/check_roundtrip.py <game dir> [--output <patched folder>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import container  # noqa: E402
from jsrfkr.digest import md5_file  # noqa: E402
from jsrfkr.xbe import JP_MD5, fix_digests, load_checked  # noqa: E402


def all_files(top):
    for d, _, names in os.walk(top):
        for n in names:
            yield os.path.relpath(os.path.join(d, n), top).replace("\\", "/")


def check_containers(game):
    ok = total = 0
    failures = []
    for rel in sorted(all_files(os.path.join(game, "Media"))):
        path = os.path.join(game, "Media", rel)
        with open(path, "rb") as f:
            data = f.read()
        if not container.is_container(data):
            continue
        total += 1
        try:
            same = container.build(container.parse(data)) == data
        except container.FormatError as err:
            failures.append(f"Media/{rel}: {err}")
            continue
        if same:
            ok += 1
        else:
            failures.append(f"Media/{rel}: rebuilt bytes differ")
    print(f"MULT/NORM files: {ok}/{total} rebuilt identical")
    return failures


def check_xbe(game):
    x = load_checked(os.path.join(game, "default.xbe"), JP_MD5, "Japanese default.xbe")
    image = bytearray(x.data)
    fix_digests(x, image, [s.name for s in x.sections])
    same = bytes(image) == x.data
    print(f"default.xbe: {len(x.sections)} section digests recomputed, image {'unchanged' if same else 'CHANGED'}")
    return [] if same else ["default.xbe: recomputed digests differ"]


def compare_folder(game, out):
    a, b = set(all_files(game)), set(all_files(out))
    failures = [f"{n}: missing in output" for n in sorted(a - b)]
    failures += [f"{n}: not in the dump" for n in sorted(b - a - {"md5.txt"})]
    same = 0
    for n in sorted(a & b):
        if md5_file(os.path.join(game, n)) == md5_file(os.path.join(out, n)):
            same += 1
        else:
            failures.append(f"{n}: differs")
    print(f"output folder: {same}/{len(a)} files equal to the dump")
    return failures


def main():
    args = sys.argv[1:]
    out = None
    if "--output" in args:
        i = args.index("--output")
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__)
    game = args[0]
    failures = check_containers(game) + check_xbe(game)
    if out:
        failures += compare_folder(game, out)
    for f in failures[:50]:
        print("  " + f)
    if failures:
        raise SystemExit(f"{len(failures)} failure(s)")
    print("all round trips identical")


if __name__ == "__main__":
    main()
