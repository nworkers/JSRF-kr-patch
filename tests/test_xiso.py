"""Unit tests for tools/jsrfkr/xiso.py on a synthetic XDVDFS image (no game data)."""
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import xiso  # noqa: E402

S = xiso.SECTOR


def image(files):
    """Volume descriptor at sector 32, root directory at 33, file data from 34."""
    out = bytearray(S * 34)
    out[32 * S:32 * S + 20] = xiso.MAGIC
    table, sector, data = bytearray(), 34, bytearray()
    names = sorted(files)
    for i, name in enumerate(names):
        body = files[name]
        right = (len(table) + 14 + len(name) + 3) // 4 * 4 // 4 if i + 1 < len(names) else 0
        entry = struct.pack("<HHIIBB", 0, right, sector, len(body), 0, len(name)) + name.encode()
        entry += b"\xff" * (-len(entry) % 4)
        table += entry
        data += body + bytes(-len(body) % S)
        sector += -(-len(body) // S)
    table += b"\xff" * (S - len(table))
    struct.pack_into("<II", out, 32 * S + 20, 33, len(table))
    out[33 * S:34 * S] = table
    return out + data


class XisoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "t.iso")
        with open(self.path, "wb") as f:
            f.write(image({"A.BIN": b"a" * 10, "B.BIN": b"b" * 100}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_size_and_within_sectors(self):
        with xiso.Image(self.path, "r+b") as img:
            self.assertEqual(img.replace("A.BIN", b"x" * 10), "in place")
            self.assertEqual(img.replace("B.BIN", b"y" * 2000), "in place")
            self.assertEqual(img.replace("A.BIN", b"z" * 4), "in place")
        with xiso.Image(self.path) as img:
            self.assertEqual(img.read("A.BIN"), b"z" * 4)
            self.assertEqual(img.read("B.BIN"), b"y" * 2000)
            self.assertEqual(img.find("B.BIN").sector, 35)

    def test_grow_past_sectors(self):
        size = os.path.getsize(self.path)
        with xiso.Image(self.path, "r+b") as img:
            self.assertEqual(img.replace("A.BIN", b"g" * (S + 1)), "moved")
        with xiso.Image(self.path) as img:
            e = img.find("A.BIN")
            self.assertEqual((e.sector, e.size), (size // S, S + 1))
            self.assertEqual(img.read("A.BIN"), b"g" * (S + 1))
            self.assertEqual(img.read("B.BIN"), b"b" * 100)
        self.assertEqual(os.path.getsize(self.path) % S, 0)


if __name__ == "__main__":
    unittest.main()
