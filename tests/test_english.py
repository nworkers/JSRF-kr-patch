"""Unit tests for tools/jsrfkr/english.py on synthetic data (no game data)."""
import hashlib
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import container, english, mission, msgscript, textpatch  # noqa: E402
from jsrfkr.container import Block  # noqa: E402
from jsrfkr.xbe import Xbe  # noqa: E402
import fakexbe  # noqa: E402
from test_mission import sample as mission_sample  # noqa: E402
from test_msgscript import EVENT, TALK  # noqa: E402


def row(file, where, orig):
    kind, path, value = textpatch.parse_where(where)
    return textpatch.Row("t", 1, file, kind, path, value, len(orig), hashlib.sha1(orig).hexdigest(), "x", "nul")


def block(script, lang):
    M = script.messages
    return ([f[lang] for f in script.fields], [script.values[lang * M + m] for m in range(M)],
            [[p.data for p in msg] for msg in script.pages[lang]])


class ScriptTest(unittest.TestCase):
    def test_copy_language0(self):
        for data in (EVENT, TALK):
            with self.subTest(len(data)):
                before = msgscript.parse(data)
                after = msgscript.parse(english.copy_language0(data))
                self.assertEqual(block(after, 1), block(before, 0))
                self.assertEqual(block(after, 0), block(before, 0))

    def test_files(self):
        ev = "Media/Event/Event/e999.dat"
        tk = "Media/Event/TalkEvent/TE999.bin"
        tree = Block(b"MULT", [Block(b"NORM", [b"a"]), Block(b"NORM", []), Block(b"NORM", [EVENT])])
        files = {ev: bytearray(container.build(tree)), tk: bytearray(TALK)}
        p_ev = msgscript.parse(EVENT).pages[0][0][0]
        p_tk = msgscript.parse(TALK).block(0)[1]
        rows = [row(ev, f"norm:2/0+{p_ev.offset:#x}", p_ev.data), row(tk, f"off:{p_tk.offset:#x}", p_tk.data)]
        result = english.apply(rows, files, lambda n: 0, None, [])
        self.assertEqual(result.scripts, 2)
        s = msgscript.parse(container.parse(files[ev]).get((2, 0)))
        self.assertEqual(block(s, 1), block(s, 0))
        self.assertEqual(container.parse(files[ev]).get((0, 0)), b"a")
        s = msgscript.parse(files[tk])
        self.assertEqual(block(s, 1), block(s, 0))


class MissionTest(unittest.TestCase):
    NAME = "Media/Mission/mssn9999.bin"

    def test_slot1_follows_korean_slot0(self):
        data, _, _, pool = mission_sample()
        files = {self.NAME: bytearray(data)}
        # 'JP one' was replaced in place; 'JP two' was not translated
        rows = [row(self.NAME, f"off:{pool[b'JP one']:#x}", b"JP one")]
        result = english.apply(rows, files, lambda n: len(data), None, [])
        self.assertEqual(result.commands, 1)
        cmds = mission.text_commands(files[self.NAME])
        by_slot0 = {c.pointers[0][1]: c for c in cmds}
        self.assertEqual(by_slot0[pool[b"JP one"]].pointers[1][1], pool[b"JP one"])
        other = [c for c in cmds if c.pointers[0][1] != pool[b"JP one"]][0]
        self.assertNotEqual(other.pointers[1][1], other.pointers[0][1])

    def test_appended_counts_as_korean(self):
        data, _, sec194, pool = mission_sample()
        out = bytearray(data) + b"appended\0"
        struct.pack_into("<I", out, sec194 + 4, len(data))       # slot 0 of the 0x194 command
        files = {self.NAME: out}
        rows = [row(self.NAME, f"off:{pool[b'JP two']:#x}", b"JP two")]
        english.apply(rows, files, lambda n: len(data), None, [])
        cmd = [c for c in mission.text_commands(files[self.NAME]) if c.section == 0x194][0]
        self.assertEqual(cmd.pointers[1][1], len(data))


class XbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        jp = "セーブ".encode("cp932")
        rdata = jp + b"\0\0" + b"SAVE\0\0\0\0" + b"OK\0\0"
        # .data: JP slot, EN slot; then an untranslated pair
        data = struct.pack("<4I", 0x12000, 0x12008, 0x1200C, 0x1200C)
        self.image = bytes(fakexbe.build(b"", rdata, data))
        path = os.path.join(self.tmp.name, "default.xbe")
        with open(path, "wb") as f:
            f.write(self.image)
        self.x = Xbe(path)
        self.jp = jp

    def tearDown(self):
        self.tmp.cleanup()

    def test_english_slot_takes_japanese_value(self):
        image = bytearray(self.image)
        struct.pack_into("<I", image, 0x3000, 0x14000)           # as if reinsert moved the string
        files = {"default.xbe": image}
        pairs = [english.Pair(0x13000, 0x13004, 0x12000, 0x12008, "direct"),
                 english.Pair(0x13008, 0x1300C, 0x1200C, 0x1200C, "direct")]
        rows = [row("default.xbe", "va:0x12000", self.jp)]
        result = english.apply(rows, files, lambda n: 0, self.x, pairs)
        self.assertEqual(struct.unpack_from("<I", image, 0x3004)[0], 0x14000)
        self.assertEqual(struct.unpack_from("<I", image, 0x300C)[0], 0x1200C)   # untranslated pair kept
        self.assertEqual((result.slots, result.sections), (1, {".data"}))

    def test_map_must_match_the_xbe(self):
        files = {"default.xbe": bytearray(self.image)}
        pairs = [english.Pair(0x13000, 0x13004, 0x12000, 0x12099, "direct")]
        with self.assertRaisesRegex(english.EnglishError, "do not hold"):
            english.apply([row("default.xbe", "va:0x12000", self.jp)], files, lambda n: 0, self.x, pairs)

    def test_read_map(self):
        path = os.path.join(self.tmp.name, "m.tsv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# c\njp_slot\ten_slot\tjp_value\ten_value\trule\n0x13000\t0x13004\t0x12000\t0x12008\tdirect\n")
        self.assertEqual(english.read_map(path), [english.Pair(0x13000, 0x13004, 0x12000, 0x12008, "direct")])


if __name__ == "__main__":
    unittest.main()
