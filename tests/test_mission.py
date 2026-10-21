"""Unit tests for tools/jsrfkr/mission.py on synthetic data (no game data)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import mission  # noqa: E402


def sample(bad_pointer=False):
    """Header, a 0x174 section of two 0x54-byte records (one text, one not),
    a 0x194 section of one 0x44-byte text record, then a string pool."""
    data = bytearray(mission.HEADER)
    sec174 = len(data)
    data += bytes(0x54 * 2)
    sec194 = len(data)
    data += bytes(0x44)
    data += b"\0"
    pool = {}
    for name in (b"JP one", b"EN one", b"JP two"):
        pool[name] = len(data)
        data += name + b"\0"
    struct.pack_into("<2I", data, 0x174, sec174, 2)
    struct.pack_into("<2I", data, 0x194, sec194, 1)
    struct.pack_into("<I", data, sec174 + 0x10, 0xEF)
    struct.pack_into("<2I", data, sec174 + 0x14, pool[b"JP one"] + (1 if bad_pointer else 0), pool[b"EN one"])
    struct.pack_into("<I", data, sec174 + 0x54 + 0x10, 0x48)
    struct.pack_into("<2I", data, sec174 + 0x54 + 0x14, pool[b"JP one"], pool[b"JP one"])
    struct.pack_into("<I", data, sec194, 0xBF)
    struct.pack_into("<I", data, sec194 + 0x04, pool[b"JP two"])
    return bytes(data), sec174, sec194, pool


class MissionTest(unittest.TestCase):
    def test_text_commands(self):
        data, sec174, sec194, pool = sample()
        cmds = mission.text_commands(data)
        self.assertEqual([(c.section, c.index, c.op) for c in cmds], [(0x174, 0, 0xEF), (0x194, 0, 0xBF)])
        self.assertEqual(cmds[0].record, sec174)
        self.assertEqual(cmds[0].pointers[0], (sec174 + 0x14, pool[b"JP one"]))
        self.assertEqual(cmds[0].pointers[2], (sec174 + 0x1C, 0))
        self.assertEqual(mission.string_at(data, cmds[1].pointers[0][1]), b"JP two")
        self.assertEqual(len(cmds[1].pointers), mission.SLOTS)

    def test_bad_pointer(self):
        data, *_ = sample(bad_pointer=True)
        with self.assertRaisesRegex(mission.FormatError, "slot 0"):
            mission.text_commands(data)

    def test_short(self):
        with self.assertRaises(mission.FormatError):
            mission.text_commands(b"\0" * 0x100)


if __name__ == "__main__":
    unittest.main()
