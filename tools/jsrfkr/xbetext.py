"""Japanese strings in default.xbe and what refers to them (analysis xbe-strings.md).

A string is taken from .rdata when it
  * starts after a NUL at a 4-byte aligned VA and ends at a NUL,
  * is made of Shift-JIS double-byte characters (lead 0x81-0x9F, 0xE0-0xEF)
    and single bytes 0x09, 0x0A, 0x20-0x7E, and decodes as cp932,
  * has a double-byte character with lead 0x82-0x9F (kana, kanji, full-width
    letters), and at least two double-byte characters or only that one.
References: aligned u32 slots in .data equal to the VA, and 'push imm32'
(0x68) in .text whose immediate is the VA. Other byte matches of the VA in
.text are counted apart (none is an instruction operand in the JP build).
"""
import re
import struct
from collections import namedtuple

CHARS = re.compile(rb"(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x09\x0a\x20-\x7e])+")
DOUBLE = re.compile(rb"[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]")
KANA_KANJI = re.compile(rb"[\x82-\x9f][\x40-\x7e\x80-\xfc]")
PUSH = 0x68

# data_refs: VAs of .data slots; code_refs: VAs of push immediates; stray: other .text matches
XbeString = namedtuple("XbeString", "va data data_refs code_refs stray")


def is_japanese(b):
    if CHARS.fullmatch(b) is None:
        return False
    try:
        b.decode("cp932")
    except UnicodeDecodeError:
        return False
    doubles = DOUBLE.findall(b)
    if not KANA_KANJI.search(b"".join(doubles)):
        return False
    return len(doubles) >= 2 or (len(doubles) == 1 and len(b) == 2)


def _candidates(blob, va0):
    i = 0
    while i < len(blob):
        if blob[i] and (i == 0 or blob[i - 1] == 0) and (va0 + i) % 4 == 0:
            end = blob.find(b"\0", i)
            if end < 0:
                return
            b = blob[i:end]
            if is_japanese(b):
                yield va0 + i, b
            i = end
        i += 1


def strings(x):
    """Every Japanese .rdata string of an Xbe with its references, by VA."""
    rd, da, tx = x.section(".rdata"), x.section(".data"), x.section(".text")
    found = list(_candidates(x.data[rd.raw:rd.raw + rd.rsize], rd.va))
    wanted = {va for va, _ in found}
    slots = {}
    blob = x.data[da.raw:da.raw + da.rsize]
    for i in range(0, len(blob) - 3, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if v in wanted:
            slots.setdefault(v, []).append(da.va + i)
    code = x.data[tx.raw:tx.raw + tx.rsize]
    out = []
    for va, b in found:
        key, push, stray, i = struct.pack("<I", va), [], [], 0
        while True:
            i = code.find(key, i)
            if i < 0:
                break
            (push if i and code[i - 1] == PUSH else stray).append(tx.va + i)
            i += 1
        out.append(XbeString(va, b, tuple(slots.get(va, ())), tuple(push), tuple(stray)))
    return out
