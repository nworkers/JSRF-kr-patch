"""Edit an XBE image in memory: read its section table, add a section, fix digests (design 20261021-i013 §3.3).

Header fields used (offsets in the image, values are VAs from the base):
  0x104 base   0x108 size of headers   0x10C size of image
  0x11C section count   0x120 section header table
Section header (56 bytes): u32 flags, va, vsize, raw, rsize, name VA,
  name ref count, head and tail shared-page ref count VAs (u16 each),
  20-byte SHA-1 digest of (u32 rsize + raw data) at +0x24.

add_section() moves the table into the free space after the headers (the
first section's raw data starts at 0x1000 in the JP build), adds one entry,
its name and two new page counters, and places the section after the image
end (VA) and the file end (raw), both rounded up to 0x1000. The signature is
not fixed (emulators run unsigned images, analysis text-files.md §4).
"""
import hashlib
import struct

from .xbe import Section

ENTRY = 56
PAGE = 0x1000
DIGEST = 0x24


class XbeEditError(ValueError):
    pass


def _u32(image, off):
    return struct.unpack_from("<I", image, off)[0]


def _align(v, a):
    return v + (-v) % a


def sections(image):
    """Section list of an image (the table may have moved)."""
    base = _u32(image, 0x104)
    count, table = _u32(image, 0x11C), _u32(image, 0x120) - base
    out = []
    for i in range(count):
        flags, va, vs, raw, rs, nva = struct.unpack_from("<6I", image, table + ENTRY * i)
        n = nva - base
        out.append(Section(bytes(image[n:image.index(b"\0", n)]).decode("ascii"), va, vs, raw, rs, flags))
    return out


def offset(image, va):
    """File offset of a VA in an image, or None when not backed by file data."""
    for s in sections(image):
        if s.va <= va < s.va + s.rsize:
            return s.raw + va - s.va
    return None


def add_section(image, name, data, flags=0x06):
    """-> (new image bytearray, VA of the new section)."""
    image = bytearray(image)
    base, headers, size = _u32(image, 0x104), _u32(image, 0x108), _u32(image, 0x10C)
    count, table = _u32(image, 0x11C), _u32(image, 0x120) - base
    old = sections(image)
    if any(s.name == name for s in old):
        raise XbeEditError(f"section {name} already exists")
    first_raw = min(s.raw for s in old)
    new_table = _align(headers, 4)
    name_at = new_table + ENTRY * (count + 1)
    counters = _align(name_at + len(name) + 1, 2)
    end = counters + 4
    if end > first_raw:
        raise XbeEditError(f"no room for another section header ({end:#x} > first section at {first_raw:#x})")
    va = _align(base + size, PAGE)
    raw = _align(len(image), PAGE)
    entry = struct.pack("<9I", flags, va, len(data), raw, len(data), base + name_at, 0,
                        base + counters, base + counters + 2) + bytes(20)
    image[new_table:new_table + ENTRY * count] = image[table:table + ENTRY * count]
    image[new_table + ENTRY * count:name_at] = entry
    image[name_at:end] = name.encode("ascii") + bytes(end - name_at - len(name))
    struct.pack_into("<I", image, 0x108, end)
    struct.pack_into("<I", image, 0x10C, va + len(data) - base)
    struct.pack_into("<I", image, 0x11C, count + 1)
    struct.pack_into("<I", image, 0x120, base + new_table)
    image += bytes(raw - len(image))
    image += data
    image += bytes(_align(len(image), PAGE) - len(image))
    return image, va


def fix_digests(image, names):
    """Recompute the SHA-1 digest of the named sections from the image's own table."""
    table = _u32(image, 0x120) - _u32(image, 0x104)
    by_name = {s.name: k for k, s in enumerate(sections(image))}
    for name in names:
        k = by_name[name]
        flags, va, vs, raw, rs = struct.unpack_from("<5I", image, table + ENTRY * k)
        digest = hashlib.sha1(struct.pack("<I", rs) + bytes(image[raw:raw + rs])).digest()
        image[table + ENTRY * k + DIGEST:table + ENTRY * k + DIGEST + 20] = digest
