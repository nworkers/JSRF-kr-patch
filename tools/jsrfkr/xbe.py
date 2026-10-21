"""Minimal access to an Xbox XBE image: sections, VA <-> file offset, section digests.

Standard library only.
"""
import hashlib
import struct

JP_MD5 = "d8490cdb75bd47b36c62effdf1461ae0"   # Japanese default.xbe (default_jpn.xbe)
US_MD5 = "f4e366bfdceee551a09f42219c90d84e"   # US default_eng.xbe


class Section:
    def __init__(self, name, va, vsize, raw, rsize, flags):
        self.name, self.va, self.vsize = name, va, vsize
        self.raw, self.rsize, self.flags = raw, rsize, flags

    def __repr__(self):
        return f"{self.name} va={self.va:08x} vsize={self.vsize:x} raw={self.raw:x} rsize={self.rsize:x}"


class Xbe:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = f.read()
        self.md5 = hashlib.md5(self.data).hexdigest()
        d = self.data
        if d[:4] != b"XBEH":
            raise ValueError(f"{path}: not an XBE")
        self.base = struct.unpack_from("<I", d, 0x104)[0]
        count = struct.unpack_from("<I", d, 0x11C)[0]
        hdr = struct.unpack_from("<I", d, 0x120)[0] - self.base
        self.sections = []
        for i in range(count):
            flags, va, vs, raw, rs, nva = struct.unpack_from("<6I", d, hdr + i * 56)
            name = d[nva - self.base:d.index(b"\0", nva - self.base)].decode("ascii")
            self.sections.append(Section(name, va, vs, raw, rs, flags))

    def section(self, name):
        return next(s for s in self.sections if s.name == name)

    def section_at(self, va):
        for s in self.sections:
            if s.va <= va < s.va + s.vsize:
                return s
        return None

    def offset(self, va):
        """File offset of a VA, or None when the VA is not backed by file data (bss)."""
        for s in self.sections:
            if s.va <= va < s.va + s.rsize:
                return s.raw + va - s.va
        return None

    def read(self, va, n):
        o = self.offset(va)
        if o is None:
            raise ValueError(f"VA {va:08x} has no file data")
        return self.data[o:o + n]

    def u8(self, va):
        return self.read(va, 1)[0]

    def u16(self, va):
        return struct.unpack("<H", self.read(va, 2))[0]

    def s16(self, va):
        return struct.unpack("<h", self.read(va, 2))[0]

    def u32(self, va):
        return struct.unpack("<I", self.read(va, 4))[0]

    def f32(self, va):
        return struct.unpack("<f", self.read(va, 4))[0]

    def cstr(self, va):
        o = self.offset(va)
        return self.data[o:self.data.index(b"\0", o)]

    def in_image(self, v):
        return self.section_at(v) is not None


def fix_digests(x, image, names):
    """Recompute the header SHA-1 of the named sections: SHA-1(u32 raw size + raw data)."""
    hdr = struct.unpack_from("<I", x.data, 0x120)[0] - x.base
    for name in names:
        s = x.section(name)
        k = x.sections.index(s)
        digest = hashlib.sha1(struct.pack("<I", s.rsize) + image[s.raw:s.raw + s.rsize]).digest()
        image[hdr + 56 * k + 0x24:hdr + 56 * k + 0x38] = digest


def load_checked(path, md5, label):
    x = Xbe(path)
    if x.md5 != md5:
        raise SystemExit(f"{label}: MD5 {x.md5} does not match the expected {md5} ({path})")
    return x
