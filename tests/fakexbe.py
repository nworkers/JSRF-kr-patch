"""A tiny synthetic XBE for the unit tests (no game data).

  headers 0x000-0x400   magic, base 0x10000, section table at 0x200, names at 0x300
  .text   raw 0x1000    VA 0x11000
  .rdata  raw 0x2000    VA 0x12000
  .data   raw 0x3000    VA 0x13000
Each section is 0x100 bytes.
"""
import struct

BASE = 0x10000
SECTIONS = ((".text", 0x11000, 0x1000), (".rdata", 0x12000, 0x2000), (".data", 0x13000, 0x3000))
SIZE = 0x100


def build(text=b"", rdata=b"", data=b""):
    image = bytearray(0x3000 + SIZE)
    image[0:4] = b"XBEH"
    struct.pack_into("<3I", image, 0x104, BASE, 0x400, 0x13000 + SIZE - BASE)
    struct.pack_into("<2I", image, 0x11C, len(SECTIONS), BASE + 0x200)
    name_at, counter = 0x300, 0x380
    for k, (name, va, raw) in enumerate(SECTIONS):
        struct.pack_into("<9I", image, 0x200 + 56 * k, 0x06, va, SIZE, raw, SIZE, BASE + name_at, 0,
                         BASE + counter + 2 * k, BASE + counter + 2 * k + 2)
        image[name_at:name_at + len(name)] = name.encode()
        name_at += 0x10
    for (name, va, raw), body in zip(SECTIONS, (text, rdata, data)):
        image[raw:raw + len(body)] = body
    return image
