"""Unit tests for tools/jsrfkr/xbeedit.py on a synthetic XBE (no game data)."""
import hashlib
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import xbeedit  # noqa: E402
import fakexbe  # noqa: E402


class XbeEditTest(unittest.TestCase):
    def test_sections(self):
        image = fakexbe.build()
        self.assertEqual([(s.name, s.va, s.raw) for s in xbeedit.sections(image)],
                         [(n, va, raw) for n, va, raw in fakexbe.SECTIONS])
        self.assertEqual(xbeedit.offset(image, 0x12010), 0x2010)
        self.assertIsNone(xbeedit.offset(image, 0x14000))

    def test_add_section(self):
        image = fakexbe.build(rdata=b"old")
        new, va = xbeedit.add_section(image, "KRTEXT", b"hello\0")
        self.assertEqual(va, 0x14000)
        names = [s.name for s in xbeedit.sections(new)]
        self.assertEqual(names, [".text", ".rdata", ".data", "KRTEXT"])
        s = xbeedit.sections(new)[-1]
        self.assertEqual((s.raw, s.rsize, s.vsize, s.flags), (0x4000, 6, 6, 0x06))
        self.assertEqual(xbeedit.offset(new, va), 0x4000)
        self.assertEqual(bytes(new[0x4000:0x4006]), b"hello\0")
        self.assertEqual(len(new) % 0x1000, 0)
        base = fakexbe.BASE
        self.assertEqual(struct.unpack_from("<I", new, 0x120)[0], base + 0x400)     # table moved
        self.assertEqual(struct.unpack_from("<I", new, 0x11C)[0], 4)
        self.assertEqual(struct.unpack_from("<I", new, 0x10C)[0], va + 6 - base)
        self.assertLessEqual(struct.unpack_from("<I", new, 0x108)[0], 0x1000)
        self.assertEqual(bytes(new[:0x104]), bytes(image[:0x104]))
        self.assertEqual(bytes(new[0x200:0x200 + 56 * 3]), bytes(new[0x400:0x400 + 56 * 3]))   # old table kept
        self.assertEqual(bytes(new[0x1000:0x3100]), bytes(image[0x1000:0x3100]))
        with self.assertRaises(xbeedit.XbeEditError):
            xbeedit.add_section(new, "KRTEXT", b"x")

    def test_no_room(self):
        image = fakexbe.build()
        struct.pack_into("<I", image, 0x108, 0xFF0)
        with self.assertRaisesRegex(xbeedit.XbeEditError, "no room"):
            xbeedit.add_section(image, "KRTEXT", b"x")

    def test_fix_digests(self):
        new, _ = xbeedit.add_section(fakexbe.build(), "KRTEXT", b"abc")
        xbeedit.fix_digests(new, ["KRTEXT", ".rdata"])
        table = struct.unpack_from("<I", new, 0x120)[0] - fakexbe.BASE
        want = hashlib.sha1(struct.pack("<I", 3) + b"abc").digest()
        self.assertEqual(bytes(new[table + 56 * 3 + 0x24:table + 56 * 3 + 0x38]), want)
        want = hashlib.sha1(struct.pack("<I", 0x100) + bytes(0x100)).digest()
        self.assertEqual(bytes(new[table + 56 * 1 + 0x24:table + 56 * 1 + 0x38]), want)


if __name__ == "__main__":
    unittest.main()
