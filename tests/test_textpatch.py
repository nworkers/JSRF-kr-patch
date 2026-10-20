"""Unit tests for tools/jsrfkr/textpatch.py and encode.py on synthetic data (no game data)."""
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import container, textpatch  # noqa: E402
from jsrfkr.container import Block  # noqa: E402
from jsrfkr.encode import Encoder  # noqa: E402
import hangul  # noqa: E402  (on sys.path through jsrfkr)

HEADER = "file\twhere\torig_len\torig_sha1\tkorean\tpad\n"


def sha(b):
    return hashlib.sha1(b).hexdigest()


def encoder():
    # 가 and 나 plus the full-width '！' (0x8149); single-byte: space only
    return Encoder({hangul.CODE_OF["가"], hangul.CODE_OF["나"], 0x8149}, set())


class EncoderTest(unittest.TestCase):
    def test_encode(self):
        e = encoder()
        self.assertEqual(e.encode("가 나！"), bytes((0x88, 0x90, 0x20)) + bytes.fromhex(f"{hangul.CODE_OF['나']:04x}") + b"\x81\x49")
        for bad in ("다", "A", "漢", "é"):
            with self.subTest(bad), self.assertRaises(ValueError):
                e.encode(bad)


class TextPatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, body):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        return path

    def test_read_rows(self):
        p = self.write("a.tsv", "# comment\n" + HEADER +
                       f"Media/x.bin\toff:0x10\t4\t{'0' * 40}\t가나\t\n"
                       f"Media/e.dat\tnorm:2/0+0x1c\t6\t{'1' * 40}\t가\tspace\n")
        rows = textpatch.read_rows([p])
        self.assertEqual([(r.kind, r.path, r.offset, r.pad) for r in rows],
                         [("off", None, 0x10, "nul"), ("norm", (2, 0), 0x1C, "space")])
        self.assertEqual(textpatch.format_where(rows[1]), "norm:2/0+0x1c")

    def test_read_rows_errors(self):
        cases = {
            "duplicate": HEADER + f"f\toff:0x10\t4\t{'0' * 40}\t가\t\nf\toff:0x10\t4\t{'0' * 40}\t나\t\n",
            "bad place": HEADER + f"f\tpos:0x10\t4\t{'0' * 40}\t가\t\n",
            "bad norm": HEADER + f"f\tnorm:2/0\t4\t{'0' * 40}\t가\t\n",
            "bad pad": HEADER + f"f\toff:0x10\t4\t{'0' * 40}\t가\ttab\n",
            "va outside xbe": HEADER + f"Media/x.bin\tva:0x10\t4\t{'0' * 40}\t가\t\n",
            "missing column": "file\twhere\n",
        }
        for name, body in cases.items():
            with self.subTest(name), self.assertRaises(textpatch.PatchError):
                textpatch.read_rows([self.write(name + ".tsv", body)])

    def test_apply_off_and_norm(self):
        flat = b"\0" * 16 + b"ABCD\0" + b"\0" * 11
        tree = Block(b"MULT", [Block(b"NORM", [b"..XYZW\0.."])])
        files_in = {"Media/x.bin": flat, "Media/e.dat": container.build(tree)}
        p = self.write("t.tsv", HEADER +
                       f"Media/x.bin\toff:0x10\t4\t{sha(b'ABCD')}\t가\t\n"
                       f"Media/e.dat\tnorm:0/0+0x2\t4\t{sha(b'XYZW')}\t나\t\n")
        rows = textpatch.read_rows([p])
        files = {}
        textpatch.apply(rows, files, files_in.__getitem__, encoder())
        self.assertEqual(bytes(files["Media/x.bin"][16:21]), bytes((0x88, 0x90, 0, 0, 0)))
        item = container.parse(files["Media/e.dat"]).get((0, 0))
        self.assertEqual(item[2:6], bytes.fromhex(f"{hangul.CODE_OF['나']:04x}") + b"\0\0")
        self.assertEqual(len(files["Media/e.dat"]), len(files_in["Media/e.dat"]))

    def test_apply_checks(self):
        data = {"f": b"ABCD\0EFGH"}
        cases = {
            "hash": (f"f\toff:0x0\t4\t{'0' * 40}\t가\t\n", "orig_sha1"),
            "no nul": (f"f\toff:0x5\t3\t{sha(b'EFG')}\t가\t\n", "NUL"),
            "too long": (f"f\toff:0x0\t1\t{sha(b'A')}\t가\tspace\n", "more than"),
            "not a container": (f"f\tnorm:0/0+0x0\t1\t{sha(b'A')}\t가\t\n", "container"),
        }
        for name, (line, msg) in cases.items():
            rows = textpatch.read_rows([self.write(name + ".tsv", HEADER + line)])
            with self.subTest(name), self.assertRaisesRegex(textpatch.PatchError, msg):
                textpatch.apply(rows, {}, data.__getitem__, encoder())

    def test_norm_string_at_item_end(self):
        # A NORM item's data length excludes the terminator: a string may run to the item's end.
        tree = Block(b"MULT", [Block(b"NORM", [b"\x01\x02ABCD"])])
        data = {"e": container.build(tree)}
        rows = textpatch.read_rows([self.write("n.tsv", HEADER + f"e\tnorm:0/0+0x2\t4\t{sha(b'ABCD')}\t가\t\n")])
        files = {}
        textpatch.apply(rows, files, data.__getitem__, encoder())
        self.assertEqual(container.parse(files["e"]).get((0, 0)), b"\x01\x02\x88\x90\0\0")
        # the same string in a flat file needs a NUL after it
        flat = {"f": b"\x01\x02ABCD"}
        rows = textpatch.read_rows([self.write("f.tsv", HEADER + f"f\toff:0x2\t4\t{sha(b'ABCD')}\t가\t\n")])
        with self.assertRaisesRegex(textpatch.PatchError, "NUL"):
            textpatch.apply(rows, {}, flat.__getitem__, encoder())

    def test_space_pad(self):
        data = {"f": b"$pAB CD$r"}
        rows = textpatch.read_rows([self.write("s.tsv", HEADER + f"f\toff:0x2\t5\t{sha(b'AB CD')}\t가\tspace\n")])
        files = {}
        textpatch.apply(rows, files, data.__getitem__, encoder())
        self.assertEqual(bytes(files["f"]), b"$p\x88\x90   $r")

    def test_mixed_places_rejected(self):
        tree = Block(b"MULT", [Block(b"NORM", [b"AB\0"])])
        data = {"e": container.build(tree)}
        rows = textpatch.read_rows([self.write("m.tsv", HEADER +
                                              f"e\toff:0x20\t2\t{sha(b'AB')}\t가\t\n"
                                              f"e\tnorm:0/0+0x0\t2\t{sha(b'AB')}\t가\t\n")])
        with self.assertRaisesRegex(textpatch.PatchError, "same file"):
            textpatch.apply(rows, {}, data.__getitem__, encoder())


if __name__ == "__main__":
    unittest.main()
