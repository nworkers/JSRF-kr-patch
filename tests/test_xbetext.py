"""Unit tests for tools/jsrfkr/xbetext.py on synthetic data (no game data)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import xbetext  # noqa: E402
from jsrfkr.xbe import Section  # noqa: E402


class FakeXbe:
    """Three sections laid out back to back in `data`: .text, .rdata, .data."""

    def __init__(self, text, rdata, data):
        self.data = text + rdata + data
        self.sections = [Section(".text", 0x1000, len(text), 0, len(text), 0),
                         Section(".rdata", 0x10000, len(rdata), len(text), len(rdata), 0),
                         Section(".data", 0x20000, len(data), len(text) + len(rdata), len(data), 0)]

    def section(self, name):
        return next(s for s in self.sections if s.name == name)


def sj(s):
    return s.encode("cp932")


class XbeTextTest(unittest.TestCase):
    def test_rule(self):
        self.assertTrue(xbetext.is_japanese(sj("セーブ")))
        self.assertTrue(xbetext.is_japanese(sj("Ｘ")))
        self.assertTrue(xbetext.is_japanese(sj("Xbox本体の電源")))
        self.assertFalse(xbetext.is_japanese(sj("残") + b"=9"))      # one kanji among symbols: a float
        self.assertFalse(xbetext.is_japanese(b"TOTAL"))
        self.assertFalse(xbetext.is_japanese(sj("、。")))              # symbols only (lead 0x81)
        self.assertFalse(xbetext.is_japanese(b"\x83\x40\x01"))         # a byte outside the set

    def test_strings_and_refs(self):
        rdata = bytearray(0x40)
        rdata[0x00:0x07] = sj("セーブ") + b"\0"          # VA 0x10000, aligned
        rdata[0x09:0x10] = sj("ロード") + b"\0"          # VA 0x10009, not aligned: left out
        rdata[0x10:0x15] = b"ABCD\0"                      # not Japanese
        rdata[0x18:0x1D] = sj("警部") + b"\0"            # VA 0x10018
        data = struct.pack("<4I", 0x10000, 0x10018, 0x10018, 0x12345678)
        text = b"\x90\x68" + struct.pack("<I", 0x10018) + b"\x90\x01" + struct.pack("<I", 0x10000)
        found = xbetext.strings(FakeXbe(text, bytes(rdata), data))
        self.assertEqual([(s.va, s.data) for s in found], [(0x10000, sj("セーブ")), (0x10018, sj("警部"))])
        self.assertEqual(found[0].data_refs, (0x20000,))
        self.assertEqual(found[0].code_refs, ())
        self.assertEqual(found[0].stray, (0x1000 + 8,))
        self.assertEqual(found[1].data_refs, (0x20004, 0x20008))
        self.assertEqual(found[1].code_refs, (0x1000 + 2,))


if __name__ == "__main__":
    unittest.main()
