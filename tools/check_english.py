"""Check an English-mode output against a --japanese-places output (design 20261023-i020 §7).

Both folders must come from the same dump and text. Checks, printing no text:
  * event and talk scripts: language 0 identical in both; in the English-mode
    output, talk language 1 equals language 0 (fields, per-page values, pages)
    and event language 1 is what english.english_timing() makes of the
    japanese-places script (English timing, Korean pages re-split; design
    20261023-i026)
  * missions: the only differing bytes are slot-1 pointers, each now equal to
    its command's slot-0 pointer
  * default.xbe: the only differing u32s outside the header are English slots
    of patch/xbe-en.tsv, each holding its Japanese slot's value; every section
    digest matches
  * every other changed file identical

usage: python -I tools/check_english.py <english-mode out> <japanese-places out>
"""
import fnmatch
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import ROOT, container, english, mission, msgscript, pipeline, reinsert  # noqa: E402
from jsrfkr.xbe import Xbe  # noqa: E402

EN_MAP = os.path.join(ROOT, "patch", "xbe-en.tsv")


def changed_files(out):
    with open(os.path.join(out, "md5.txt"), encoding="utf-8") as f:
        return [line.split("  ", 1)[1].strip() for line in f if line.strip()]


def block(script, lang):
    M = script.messages
    return ([f[lang] for f in script.fields], [script.values[lang * M + m] for m in range(M)],
            [[p.data for p in msg] for msg in script.pages[lang]])


def check_script(name, a, b, single):
    event = fnmatch.fnmatchcase(name, reinsert.EVENT)
    if event:
        a, b = (container.parse(d).get(reinsert.EVENT_ITEM) for d in (a, b))
    sa, sb = msgscript.parse(a), msgscript.parse(b)
    out = []
    if block(sa, 0) != block(sb, 0):
        out.append(f"{name}: language 0 differs from the japanese-places output")
    if event:
        if block(sa, 1) != block(msgscript.parse(english.english_timing(b, single)), 1):
            out.append(f"{name}: language 1 is not the Korean with the English timing")
    elif block(sa, 1) != block(sa, 0):
        out.append(f"{name}: language 1 is not a copy of language 0")
    return out, 0


def check_mission(name, a, b):
    if len(a) != len(b):
        return [f"{name}: sizes differ"], 0
    out, allowed, n = [], set(), 0
    before = {c.record: c.pointers for c in mission.text_commands(b)}
    for c in mission.text_commands(a):
        (at1, p1), p0 = c.pointers[1], c.pointers[0][1]
        if p1 != before[c.record][1][1]:
            if p1 != p0:
                out.append(f"{name}: record {c.record:#x} slot 1 changed, but not to slot 0")
            allowed.update(range(at1, at1 + 4))
            n += 1
    stray = sum(1 for i in range(len(a)) if a[i] != b[i] and i not in allowed)
    if stray:
        out.append(f"{name}: {stray} bytes differ outside slot-1 pointers")
    return out, n


def digests_ok(data):
    hdr_va = struct.unpack_from("<I", data, 0x104)[0]
    count = struct.unpack_from("<I", data, 0x11C)[0]
    hdr = struct.unpack_from("<I", data, 0x120)[0] - hdr_va
    for k in range(count):
        rec = hdr + 56 * k
        raw, rsize = struct.unpack_from("<II", data, rec + 12)
        got = hashlib.sha1(struct.pack("<I", rsize) + data[raw:raw + rsize]).digest()
        if data[rec + 0x24:rec + 0x38] != got:
            return False
    return True


def check_xbe(a, b, x):
    pairs = {p.en_slot: p for p in english.read_map(EN_MAP)}
    out, n = [], 0
    if len(a) != len(b):
        return ["default.xbe: sizes differ"], 0
    first = min(s.raw for s in x.sections)
    for o in range(first, len(a) - 3, 4):
        if a[o:o + 4] == b[o:o + 4]:
            continue
        va = next((s.va + o - s.raw for s in x.sections if s.raw <= o < s.raw + s.rsize), None)
        p = pairs.get(va)
        if p is None:
            out.append(f"default.xbe: u32 at file offset {o:#x} differs and is not an English slot")
            continue
        jo = x.offset(p.jp_slot)
        if a[o:o + 4] != b[jo:jo + 4]:
            out.append(f"default.xbe: English slot {va:#x} does not hold its Japanese slot's value")
        n += 1
    if not digests_ok(a):
        out.append("default.xbe: a section digest does not match")
    return out, n


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    en_out, jp_out = sys.argv[1:]
    names = changed_files(en_out)
    if names != changed_files(jp_out):
        raise SystemExit("the two outputs changed different files")
    x = Xbe(os.path.join(jp_out, "default.xbe"))      # section layout of the patched image
    single = pipeline.single_widths(x)                 # the single-byte table is not patched
    problems = []
    counts = {"scripts": 0, "missions": 0, "slot-1 pointers": 0, "XBE slots": 0, "other": 0}
    for name in names:
        with open(os.path.join(en_out, name), "rb") as f:
            a = f.read()
        with open(os.path.join(jp_out, name), "rb") as f:
            b = f.read()
        if fnmatch.fnmatchcase(name, reinsert.EVENT) or fnmatch.fnmatchcase(name, reinsert.TALK):
            p, _ = check_script(name, a, b, single)
            counts["scripts"] += 1
        elif fnmatch.fnmatchcase(name, reinsert.MISSION):
            p, n = check_mission(name, a, b)
            counts["missions"] += 1
            counts["slot-1 pointers"] += n
        elif name == reinsert.XBE:
            p, n = check_xbe(a, b, x)
            counts["XBE slots"] += n
        else:
            p = [] if a == b else [f"{name}: differs"]
            counts["other"] += 1
        problems += p
    print(", ".join(f"{k}: {v}" for k, v in counts.items()))
    for p in problems[:40]:
        print("  " + p)
    if problems:
        raise SystemExit(f"{len(problems)} problem(s)")
    print("english places hold")


if __name__ == "__main__":
    main()
