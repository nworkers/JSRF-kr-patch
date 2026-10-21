"""Mission files Media/Mission/mssn####.bin: text commands and their strings.

Layout (analysis mission-files.md; JP and US 0x4DB30 relocate it after load):
  header 0x220 bytes; u32 pairs (file offset, count) at 0x34..0x197 locate
  the sections. Five sections hold command records:
    0x174 0x17C 0x184 0x18C   records of 0x54 bytes, opcode u32 at +0x10,
                              text pointers u32[7] at +0x14
    0x194                     records of 0x44 bytes, opcode u32 at +0x00,
                              text pointers u32[7] at +0x04
  For the text opcodes the 7 pointers are file offsets of NUL-terminated
  strings, one per language slot (slot 0 = Japanese); 0 = none. Every string
  follows a NUL (a pointer anywhere else is a format error).
"""
import struct
from collections import namedtuple

HEADER = 0x220
TABLE = (0x34, 0x198)
SECTIONS = (            # header slot, record size, opcode offset, pointer offset
    (0x174, 0x54, 0x10, 0x14),
    (0x17C, 0x54, 0x10, 0x14),
    (0x184, 0x54, 0x10, 0x14),
    (0x18C, 0x54, 0x10, 0x14),
    (0x194, 0x44, 0x00, 0x04),
)
TEXT_OPS = frozenset((0xBE, 0xBF, 0xC0, 0xE8, 0xE9, 0xEA, 0xEF))
SLOTS = 7

# section: header slot; index: record number; record: file offset of the record;
# pointers: SLOTS (slot file offset, string file offset or 0)
Command = namedtuple("Command", "section index record op pointers")


class FormatError(ValueError):
    pass


def text_commands(data):
    """Every text command record, in section and record order."""
    data = bytes(data)
    if len(data) < HEADER:
        raise FormatError("shorter than the header")
    out = []
    for slot, size, op_at, ptr_at in SECTIONS:
        base, count = struct.unpack_from("<2I", data, slot)
        if not base:
            continue
        if base < HEADER or base + size * count > len(data):
            raise FormatError(f"section {slot:#x}: {count} records at {base:#x} past the end")
        for i in range(count):
            rec = base + size * i
            op = struct.unpack_from("<I", data, rec + op_at)[0]
            if op not in TEXT_OPS:
                continue
            ptrs = []
            for k in range(SLOTS):
                at = rec + ptr_at + 4 * k
                p = struct.unpack_from("<I", data, at)[0]
                if p and not (HEADER <= p < len(data) and data[p - 1] == 0 and data.find(b"\0", p) >= 0):
                    raise FormatError(f"section {slot:#x} record {i}: slot {k} points at {p:#x}")
                ptrs.append((at, p))
            out.append(Command(slot, i, rec, op, tuple(ptrs)))
    return out


def string_at(data, off):
    """The NUL-terminated string at a file offset (without the NUL)."""
    return bytes(data[off:data.index(b"\0", off)])
