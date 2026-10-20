"""Unit tests for tools/jsrfkr/container.py on synthetic data (no game data)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import container  # noqa: E402
from jsrfkr.container import Block, FormatError  # noqa: E402


def sample():
    return Block(b"MULT", [
        Block(b"NORM", [b"abc", b"", b"0123456789abcdef"]),
        Block(b"NORM", []),
        Block(b"MULT", [Block(b"NORM", [b"x" * 17])]),
    ])


class ContainerTest(unittest.TestCase):
    def test_layout(self):
        data = container.build(Block(b"NORM", [b"abc", b""]))
        self.assertEqual(data[:16], struct.pack("<4sIII", b"NORM", 2, 0, 0))
        # item 0: data at 0x20, 3 bytes, padded to 0x30
        self.assertEqual(struct.unpack_from("<4I", data, 0x10), (0x20, 0x30, 3, 0))
        self.assertEqual(data[0x20:0x30], b"abc" + bytes(13))
        # item 1: empty, flag 1, the link sits where item 0 ends
        self.assertEqual(struct.unpack_from("<4I", data, 0x30), (0x40, 0x40, 0, 1))
        self.assertEqual(len(data), 0x40)

    def test_empty_norm_is_header_only(self):
        self.assertEqual(container.build(Block(b"NORM", [])), struct.pack("<4sIII", b"NORM", 0, 0, 0))

    def test_round_trip(self):
        tree = sample()
        data = container.build(tree)
        self.assertEqual(container.parse(data), tree)
        self.assertEqual(container.build(container.parse(data)), data)

    def test_length_change_recomputes_links(self):
        tree = sample()
        before = container.build(tree)
        tree.set((0, 0), b"a much longer item than before")
        after = container.build(tree)
        self.assertGreater(len(after), len(before))
        again = container.parse(after)
        self.assertEqual(again.get((0, 0)), b"a much longer item than before")
        self.assertEqual(again.get((2, 0, 0)), b"x" * 17)

    def test_paths(self):
        tree = sample()
        self.assertEqual(tree.get((0, 2)), b"0123456789abcdef")
        self.assertEqual(container.parse_path("2/0/0"), (2, 0, 0))
        self.assertEqual(container.format_path((2, 0, 0)), "2/0/0")
        self.assertEqual([p for p, _ in container.walk(tree)], [(0, 0), (0, 1), (0, 2), (2, 0, 0)])
        with self.assertRaises(KeyError):
            tree.get((5,))
        with self.assertRaises(KeyError):
            tree.get((0, 0, 1))      # through data
        with self.assertRaises(KeyError):
            tree.set((2,), b"x")      # a block, not a NORM item
        with self.assertRaises(ValueError):
            container.parse_path("2/-1")

    def test_rejects_malformed(self):
        good = container.build(sample())
        cases = {
            "trailing bytes": good + bytes(16),
            "bad magic": b"XXXX" + good[4:],
            "non-zero header": good[:8] + b"\x01" + good[9:],
            "truncated": good[:-16],
        }
        norm = bytearray(container.build(Block(b"NORM", [b"abc"])))
        norm[0x25] = 1                      # padding byte
        cases["non-zero padding"] = bytes(norm)
        norm = bytearray(container.build(Block(b"NORM", [b""])))
        norm[0x1C] = 0                      # flag of an empty item
        cases["flag"] = bytes(norm)
        for name, data in cases.items():
            with self.subTest(name), self.assertRaises(FormatError):
                container.parse(data)


if __name__ == "__main__":
    unittest.main()
