"""Check that the text renderer is the same code at the same address in the JP and US XBEs.

For each code range, the bytes at the same VA in both builds are compared.
Every difference must sit inside a 32-bit operand whose JP and US values are
both addresses inside the image (a relocated .data/.bss reference); such
differences are tallied by their US-JP delta. Anything else is reported as a
real change. Data ranges (the glyph tables) must be byte-identical.

usage: python -I tools/analysis/renderer_compare.py <jp default.xbe> <us default_eng.xbe> [-v]
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from jsrfkr.xbe import JP_MD5, US_MD5, load_checked  # noqa: E402

CODE_RANGES = [
    (0x2C040, 0x2C1D0, "jetfont loader (file table 0x1EDE3C, six textures)"),
    (0x3C000, 0x3D790, "font object: lookup, draw string, width, wrappers"),
    (0x5F350, 0x5F500, "graphics init that opens TNRoman.bin"),
    (0xF81B0, 0xF9660, "message tokenizer, typewriter, page parser"),
    (0xFA7F0, 0xFA890, "$p position test"),
    (0xFE690, 0xFE6B1, "skip to next $r"),
]
DATA_RANGES = [
    (0x1C5B50, 0x1C5B6A, "'D:\\Media\\Font\\jetfont.dat'"),
    (0x1CAF74, 0x1CAF8E, "'D:\\Media\\Font\\TNRoman.bin'"),
    (0x1EDE3C, 0x1EDE40, "file table entry -> jetfont.dat"),
    (0x1F7088, 0x1F8640, "double-byte glyph table"),
    (0x1F8640, 0x1F8B20, "single-byte glyph table"),
    (0x1F8B20, 0x1F8BA0, "font descriptors, class bounds and bases"),
]


def compare_code(jp, us, lo, hi):
    a, b = jp.read(lo, hi - lo), us.read(lo, hi - lo)
    diffs = [i for i in range(len(a)) if a[i] != b[i]]
    covered, deltas, pairs, real = set(), collections.Counter(), [], []
    for i in diffs:
        if i in covered:
            continue
        for s in range(i - 3, i + 1):
            if s < 0 or s + 4 > len(a):
                continue
            va = int.from_bytes(a[s:s + 4], "little")
            vu = int.from_bytes(b[s:s + 4], "little")
            if jp.in_image(va) and us.in_image(vu):
                covered |= set(range(s, s + 4))
                deltas[vu - va] += 1
                pairs.append((lo + s, va, vu))
                break
        else:
            real.append(lo + i)
    return len(diffs), deltas, pairs, real


def main():
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv[1:]
    if len(args) != 2:
        raise SystemExit(__doc__)
    sys.argv[1:3] = args
    jp = load_checked(sys.argv[1], JP_MD5, "JP XBE")
    us = load_checked(sys.argv[2], US_MD5, "US XBE")
    total_real = 0
    for lo, hi, what in CODE_RANGES:
        n, deltas, pairs, real = compare_code(jp, us, lo, hi)
        total_real += len(real)
        summary = ", ".join(f"{d:+#x} x{c}" for d, c in sorted(deltas.items()))
        print(f"code {lo:#08x}-{hi:#08x} {what}: {n} differing bytes; "
              f"relocated operands: {summary or 'none'}; other changes: {len(real)}")
        for va in real[:10]:
            print(f"    real change at {va:#08x}")
        if verbose:
            for at, va, vu in pairs:
                print(f"    {at:#08x}: JP {va:#08x} US {vu:#08x}")
    for lo, hi, what in DATA_RANGES:
        same = jp.read(lo, hi - lo) == us.read(lo, hi - lo)
        total_real += 0 if same else 1
        print(f"data {lo:#08x}-{hi:#08x} {what}: {'identical' if same else 'DIFFERENT'}")
    print("result:", "same renderer (only relocated data addresses differ)" if total_real == 0
          else f"{total_real} real differences")


if __name__ == "__main__":
    main()
