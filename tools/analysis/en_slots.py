"""Map each language-0 .data slot of a Japanese string to the slot English mode reads instead.

Input: the US default.xbe (MD5 f4e366bf..., language value 1 at 0x1FC724).
Analysis: docs/analysis/english-mode.md §3. Four table shapes are found:

  direct     T[lang] -> string                       code: [lang*4 + T]
  array      T[lang] -> per-language string array    code: [lang*4 + T], equal gaps
  split      a run of string slots that splits into 5 or 6 equal language blocks
  special    places read with other index forms, each checked against its code bytes:
             graffiti names (lang 0 -> 0x226F40[i], else 0x227170[i], code 0x1249A0),
             [(lang*9 + i)*4 + 0x22D7E0] (code 0x1386F6), [lang*8 + 0x22D7B8] (code 0x138738)

Only pairs whose language-0 slot points to a Japanese string (jsrfkr.xbetext)
are written. The output holds addresses only (no text):

  jp_slot  en_slot  jp_value  en_value  rule

usage: python -I tools/analysis/en_slots.py <US default.xbe> [--tsv patch/xbe-en.tsv]
"""
import collections
import os
import struct
import sys

import capstone
from capstone import x86

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from jsrfkr import xbetext  # noqa: E402
from jsrfkr.xbe import US_MD5, load_checked  # noqa: E402

LANG = 0x1FC724
HEADER = "jp_slot\ten_slot\tjp_value\ten_value\trule\n"
# (code VA, expected bytes there, pairs builder)
SPECIAL = (
    (0x1249AF, bytes.fromhex("8b0c8570712200"), "graffiti", lambda: [(0x226F40 + 4 * i, 0x227170 + 4 * i) for i in range(140)]),
    (0x1386F6, bytes.fromhex("8d04c003c18b0c85e0d72200"), "2d k=9", lambda: [(0x22D7E0 + 4 * i, 0x22D804 + 4 * i) for i in range(9)]),
    (0x138738, bytes.fromhex("8b14c5b8d72200"), "lang*8", lambda: [(0x22D7B8, 0x22D7C0)]),
)


class Map:
    def __init__(self, x):
        self.x = x
        self.text, self.rd, self.dd = x.section(".text"), x.section(".rdata"), x.section(".data")
        self.jp = {s.va for s in xbetext.strings(x)}
        self.pairs = {}
        self.rule = {}
        self.lang_slot = set()
        self.tables = collections.Counter()

    def u32(self, a):
        o = self.x.offset(a)
        return None if o is None else struct.unpack_from("<I", self.x.data, o)[0]

    def kind(self, v):
        if v is None:
            return "."
        if v in self.jp:
            return "J"
        if self.rd.va <= v < self.rd.va + self.rd.rsize:
            o = self.x.offset(v)
            return "e" if self.x.data[o - 1] == 0 and 0x20 <= self.x.data[o] < 0x7F else "r"
        if self.dd.va <= v < self.dd.va + self.dd.vsize:
            return "D"
        return "."

    def add(self, block0, block1, others, rule):
        for a, b in zip(block0, block1):
            if a not in self.pairs:
                self.pairs[a], self.rule[a] = b, rule
        for blk in [block0, block1] + others:
            self.lang_slot.update(blk)
        self.tables[rule] += 1

    def code_tables(self):
        code = self.x.data[self.text.raw:self.text.raw + self.text.rsize]
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        md.detail = True
        pat = b"\xb9" + struct.pack("<I", LANG)
        found = set()
        i = code.find(pat)
        while i >= 0:
            va = self.text.va + i
            for ins in list(md.disasm(code[i:i + 120], va))[1:16]:
                hit = False
                for op in ins.operands:
                    if op.type == x86.X86_OP_MEM and op.mem.index and not op.mem.base and op.mem.scale == 4:
                        d = op.mem.disp & 0xFFFFFFFF
                        if self.dd.va <= d < self.dd.va + self.dd.vsize:
                            found.add(d)
                            hit = True
                if hit or ins.mnemonic == "ret":
                    break
            i = code.find(pat, i + 1)
        return sorted(found)

    def array_table(self, T, L, rule):
        ptrs = [self.u32(T + 4 * i) for i in range(L)]
        gaps = {ptrs[i + 1] - ptrs[i] for i in range(L - 1)}
        if len(gaps) != 1 or min(gaps) <= 0:
            return False
        n = gaps.pop() // 4
        blocks = [[ptrs[l] + 4 * i for i in range(n)] for l in range(L)]
        self.add(blocks[0], blocks[1], blocks[2:], rule)
        return True

    def build(self):
        for T in self.code_tables():
            k0, k1 = self.kind(self.u32(T)), self.kind(self.u32(T + 4))
            if k0 in "Je" and k1 in "Je":
                self.add([T], [T + 4], [[T + 8], [T + 12], [T + 16]], "direct")
            elif k0 == "D" and k1 == "D":
                for L in (6, 5, 2):
                    if all(self.kind(self.u32(T + 4 * i)) == "D" for i in range(L)) and self.array_table(T, L, "array"):
                        break
        end = self.dd.va + self.dd.rsize
        a = self.dd.va
        while a < end:                      # array tables found by shape
            if self.kind(self.u32(a)) != "D":
                a += 4
                continue
            run = [a]
            while self.kind(self.u32(run[-1] + 4)) == "D":
                run.append(run[-1] + 4)
            vals = [self.u32(r) for r in run]
            if len(run) >= 5:
                g = vals[1] - vals[0]
                if g > 0 and all(vals[i + 1] - vals[i] == g for i in range(4)) and self.kind(self.u32(vals[0])) in "Je":
                    L = 6 if len(run) >= 6 and vals[5] - vals[4] == g else 5
                    blocks = [[vals[l] + 4 * i for i in range(g // 4)] for l in range(L)]
                    if not any(b in self.lang_slot for b in blocks[0]):
                        self.add(blocks[0], blocks[1], blocks[2:], "array (shape)")
            a = run[-1] + 4
        runs, cur = [], []                  # language blocks inside one run of string slots
        for s in range(self.dd.va, end, 4):
            if self.kind(self.u32(s)) in "Je":
                if cur and s != cur[-1] + 4:
                    runs.append(cur)
                    cur = []
                cur.append(s)
        runs.append(cur)
        for r in runs:
            if not r or any(s in self.lang_slot for s in r) or not any(self.u32(s) in self.jp for s in r):
                continue
            for L in (6, 5):
                if len(r) % L:
                    continue
                k = len(r) // L
                blocks = [r[i * k:(i + 1) * k] for i in range(L)]
                j0 = sum(self.u32(s) in self.jp for s in blocks[0])
                jr = max(sum(self.u32(s) in self.jp for s in b) for b in blocks[1:])
                if j0 and jr < j0:
                    self.add(blocks[0], blocks[1], blocks[2:], "split")
                    break
        for va, want, rule, pairs in SPECIAL:
            o = self.x.offset(va)
            if self.x.data[o:o + len(want)] != want:
                raise SystemExit(f"code at {va:#x} is not the expected {rule} access")
            a0, a1 = zip(*pairs())
            for a, b in zip(a0, a1):
                self.pairs[a], self.rule[a] = b, "special " + rule
            self.lang_slot.update(a0 + a1)
            self.tables["special " + rule] += 1

    def rows(self):
        out = []
        for a in sorted(self.pairs):
            if self.u32(a) in self.jp:
                b = self.pairs[a]
                out.append((a, b, self.u32(a), self.u32(b), self.rule[a]))
        return out


def main():
    args = sys.argv[1:]
    tsv = None
    if "--tsv" in args:
        i = args.index("--tsv")
        tsv = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__)
    x = load_checked(args[0], US_MD5, "US default.xbe")
    m = Map(x)
    m.build()
    rows = m.rows()
    print("tables:", ", ".join(f"{k} {v}" for k, v in sorted(m.tables.items())))
    print(f"pairs (language-0 slot of a Japanese string -> English slot): {len(rows)}")
    print("English slot kinds:", dict(collections.Counter(m.kind(r[3]) for r in rows)))
    print("English slots used twice:", sum(1 for v in collections.Counter(r[1] for r in rows).values() if v > 1))
    print(f"Japanese strings with a paired slot: {len({r[2] for r in rows})} of {len(m.jp)}")
    if tsv:
        with open(tsv, "w", encoding="utf-8", newline="\n") as f:
            f.write("# English-mode slot map for the US default.xbe (tools/analysis/en_slots.py,\n"
                    "# docs/analysis/english-mode.md). Addresses only, no text.\n")
            f.write(HEADER)
            for a, b, va, vb, rule in rows:
                f.write(f"{a:#010x}\t{b:#010x}\t{va:#010x}\t{vb:#010x}\t{rule}\n")
        print(f"wrote {tsv}")


if __name__ == "__main__":
    main()
