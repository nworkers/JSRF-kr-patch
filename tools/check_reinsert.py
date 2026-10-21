"""Round trips of the reinsertion engine on the dump (design 20261021-i013 §5). Prints counts only.

  1. original  every extracted unit put back as its original bytes: every
               touched file must equal the dump byte for byte
  2. moved     the same with mission and XBE strings always appended or moved:
               every text command's slot 0 and every reference of a moved
               XBE string must lead to the original bytes, and nothing else
               may differ from the dump outside the appended or added parts
               (mission: the slot-0 pointers; XBE: the header, references
               and the new section)

usage: python -I tools/check_reinsert.py <game dir>
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import extract, mission, reinsert, xbeedit, xbetext  # noqa: E402
from jsrfkr.xbe import JP_MD5, Xbe  # noqa: E402

HEADER_END = 0x1000     # the XBE headers end before the first section's raw data


def run(game, x, units, always_move):
    files = {}

    def load(name):
        with open(os.path.join(game, name), "rb") as f:
            return f.read()

    changes = [reinsert.Change(extract.as_row(u), u.japanese) for us in units.values() for u in us]
    result = reinsert.apply(changes, files, load, x, {}, always_move)
    return files, result, load


def check_original(game, x, units):
    files, result, load = run(game, x, units, False)
    diff = [name for name, data in files.items() if bytes(data) != load(name)]
    print(f"original round trip: {len(result.done)} units in {len(files)} files, "
          f"{len(diff)} files differ{': ' + ', '.join(diff[:5]) if diff else ''}")
    return not diff


def check_moved(game, x, units):
    files, result, load = run(game, x, units, True)
    problems = []
    moved = {d.row.file: 0 for d in result.done}
    for d in result.done:
        if d.how in ("appended", "moved"):
            moved[d.row.file] += 1
    for name, data in sorted(files.items()):
        orig = load(name)
        if name == extract.XBE:
            continue
        if not name.startswith("Media/Mission/"):
            if bytes(data) != orig:
                problems.append(f"{name}: differs")
            continue
        before, after = mission.text_commands(orig), mission.text_commands(data)
        allowed = {c.pointers[0][0] for c in before}
        for a, b in zip(before, after):
            if mission.string_at(orig, a.pointers[0][1]) != mission.string_at(data, b.pointers[0][1]):
                problems.append(f"{name}: slot 0 of record {a.index} reads different bytes")
            if a.pointers[1:] != b.pointers[1:]:
                problems.append(f"{name}: other slots of record {a.index} changed")
        head = bytearray(data[:len(orig)])
        for at in allowed:
            head[at:at + 4] = orig[at:at + 4]
        if bytes(head) != orig:
            problems.append(f"{name}: bytes outside the slot-0 pointers changed")
    image = files.get(extract.XBE)
    if image is not None:
        sec = {s.name: s for s in xbeedit.sections(image)}[reinsert.SECTION]
        strings = {s.va: s for s in xbetext.strings(x)}
        allowed = set()
        for d in result.done:
            if d.row.file != extract.XBE or d.how != "moved":
                continue
            s = strings[d.row.offset]
            for ref in s.data_refs + s.code_refs:
                o = x.offset(ref)
                allowed |= set(range(o, o + 4))
                va = struct.unpack_from("<I", image, o)[0]
                at = xbeedit.offset(image, va)
                if at is None or not (sec.va <= va < sec.va + sec.vsize):
                    problems.append(f"default.xbe: reference {ref:#x} does not point into {sec.name}")
                elif bytes(image[at:image.index(b"\0", at)]) != s.data:
                    problems.append(f"default.xbe: reference {ref:#x} leads to other bytes")
        orig = load(extract.XBE)
        changed = next((i for i in range(HEADER_END, len(orig)) if image[i] != orig[i] and i not in allowed), None)
        if changed is not None:
            problems.append(f"default.xbe: byte {changed:#x} changed outside the headers and references")
    print(f"moved round trip: {sum(moved.values())} strings appended or moved in "
          f"{sum(1 for v in moved.values() if v)} files, {len(problems)} problems")
    for p in problems[:10]:
        print(f"  {p}")
    return not problems


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    game = sys.argv[1]
    x = Xbe(os.path.join(game, extract.XBE))
    if x.md5 != JP_MD5:
        raise SystemExit(f"default.xbe: MD5 {x.md5} is not the Japanese build ({JP_MD5})")
    units, _ = extract.units(game, x)
    ok = check_original(game, x, units)
    ok = check_moved(game, x, units) and ok
    print("all round trips hold" if ok else "ROUND TRIP FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
