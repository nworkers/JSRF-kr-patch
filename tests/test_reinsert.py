"""Unit tests for tools/jsrfkr/reinsert.py on synthetic data (no game data)."""
import hashlib
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import container, mission, msgscript, reinsert, textpatch, xbeedit  # noqa: E402
from jsrfkr.container import Block  # noqa: E402
from jsrfkr.reinsert import Change  # noqa: E402
from jsrfkr.xbe import Xbe  # noqa: E402
import fakexbe  # noqa: E402
from test_mission import sample as mission_sample  # noqa: E402
from test_msgscript import EVENT, TALK  # noqa: E402


def row(file, where, orig, pad="nul"):
    kind, path, value = textpatch.parse_where(where)
    return textpatch.Row("t", 1, file, kind, path, value, len(orig), hashlib.sha1(orig).hexdigest(), "x", pad)


def run(changes, data, x=None, always_move=False):
    files = {}
    result = reinsert.apply(changes, files, data.__getitem__, x, {}, always_move)
    return files, result


class ScriptTest(unittest.TestCase):
    def test_event_page_grows(self):
        tree = Block(b"MULT", [Block(b"NORM", [b"a"]), Block(b"NORM", []), Block(b"NORM", [EVENT])])
        name = "Media/Event/Event/e999.dat"
        script = msgscript.parse(EVENT)
        page = script.pages[0][0][0]
        new = b"longer than the original page"
        files, result = run([Change(row(name, f"norm:2/0+{page.offset:#x}", page.data, "space"), new)],
                            {name: container.build(tree)})
        again = msgscript.parse(container.parse(files[name]).get((2, 0)))
        self.assertEqual(again.pages[0][0][0].data, new)
        self.assertEqual([p.data for p in again.block(1)], [p.data for p in script.block(1)])
        self.assertEqual(container.parse(files[name]).get((0, 0)), b"a")
        self.assertEqual([d.how for d in result.done], ["page"])

    def test_talk_page_shrinks_without_padding(self):
        name = "Media/Event/TalkEvent/TE999.bin"
        script = msgscript.parse(TALK)
        page = script.block(0)[1]
        files, _ = run([Change(row(name, f"off:{page.offset:#x}", page.data, "space"), b"Y")], {name: TALK})
        self.assertEqual(len(files[name]), len(TALK) - len(page.data) + 1)
        self.assertEqual(msgscript.parse(files[name]).block(0)[1].data, b"Y")

    def test_page_codes_refused(self):
        name = "Media/Event/TalkEvent/TE999.bin"
        page = msgscript.parse(TALK).block(0)[1]
        for bad in (b"A$rB", b"A$e", b"$s\x01\x02"):
            with self.subTest(bad), self.assertRaisesRegex(textpatch.PatchError, "page counts"):
                run([Change(row(name, f"off:{page.offset:#x}", page.data, "space"), bad)], {name: TALK})

    def test_not_a_page(self):
        name = "Media/Event/TalkEvent/TE999.bin"
        page = msgscript.parse(TALK).block(0)[1]
        with self.assertRaisesRegex(textpatch.PatchError, "start of a page"):
            run([Change(row(name, f"off:{page.offset + 2:#x}", page.data[2:], "space"), b"Y")], {name: TALK})


class MissionTest(unittest.TestCase):
    NAME = "Media/Mission/mssn9999.bin"

    def test_fits_in_place(self):
        data, sec174, _, pool = mission_sample()
        files, result = run([Change(row(self.NAME, f"off:{pool[b'JP one']:#x}", b"JP one"), b"ko")],
                            {self.NAME: data})
        self.assertEqual(len(files[self.NAME]), len(data))
        self.assertEqual(mission.string_at(files[self.NAME], pool[b"JP one"]), b"ko")
        self.assertEqual(result.done[0].how, "in place")

    def test_longer_is_appended(self):
        data, sec174, sec194, pool = mission_sample()
        new = b"a much longer replacement"
        files, result = run([Change(row(self.NAME, f"off:{pool[b'JP two']:#x}", b"JP two"), new)],
                            {self.NAME: data})
        out = files[self.NAME]
        cmd = [c for c in mission.text_commands(out) if c.section == 0x194][0]
        self.assertEqual(cmd.pointers[0][1], len(data))
        self.assertEqual(mission.string_at(out, cmd.pointers[0][1]), new)
        self.assertEqual(bytes(out[:len(data)]),
                         data[:sec194 + 4] + struct.pack("<I", len(data)) + data[sec194 + 8:])
        self.assertEqual(result.done[0].how, "appended")

    def test_always_move(self):
        data, *_, pool = mission_sample()
        files, result = run([Change(row(self.NAME, f"off:{pool[b'JP one']:#x}", b"JP one"), b"JP one")],
                            {self.NAME: data}, always_move=True)
        self.assertEqual(result.done[0].how, "appended")
        cmd = mission.text_commands(files[self.NAME])[0]
        self.assertEqual(mission.string_at(files[self.NAME], cmd.pointers[0][1]), b"JP one")

    def test_longer_non_slot0_refused(self):
        data, *_, pool = mission_sample()
        with self.assertRaisesRegex(textpatch.PatchError, "language-0"):
            run([Change(row(self.NAME, f"off:{pool[b'EN one']:#x}", b"EN one"), b"much longer")],
                {self.NAME: data})


class XbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.save = "セーブ".encode("cp932")
        rdata = self.save + b"\0\0"
        data = struct.pack("<2I", 0x12000, 0x12000)
        text = b"\x90\x68" + struct.pack("<I", 0x12000)
        self.image = fakexbe.build(text, rdata, data)
        path = os.path.join(self.tmp.name, "default.xbe")
        with open(path, "wb") as f:
            f.write(self.image)
        self.x = Xbe(path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fits_in_place(self):
        files, result = run([Change(row("default.xbe", "va:0x12000", self.save), b"ab")],
                            {"default.xbe": bytes(self.image)}, self.x)
        self.assertEqual(bytes(files["default.xbe"][0x2000:0x2007]), b"ab\0\0\0\0\0")
        self.assertEqual(result.sections, {".rdata"})

    def test_longer_is_moved(self):
        new = "저장하기".encode("utf-8")       # any bytes longer than the original
        files, result = run([Change(row("default.xbe", "va:0x12000", self.save), new)],
                            {"default.xbe": bytes(self.image)}, self.x)
        out = files["default.xbe"]
        va = struct.unpack_from("<I", out, 0x3000)[0]
        self.assertEqual(va, 0x14000)
        self.assertEqual(struct.unpack_from("<I", out, 0x3004)[0], va)
        self.assertEqual(struct.unpack_from("<I", out, 0x1002)[0], va)
        at = xbeedit.offset(out, va)
        self.assertEqual(bytes(out[at:at + len(new) + 1]), new + b"\0")
        self.assertEqual(bytes(out[0x2000:0x2006]), self.save)            # old place kept
        self.assertEqual(result.sections, {".data", ".text", reinsert.SECTION})
        self.assertEqual(result.done[0].how, "moved")


class OtherTest(unittest.TestCase):
    def test_other_places_in_place_only(self):
        data = {"Media/Misc/x.bin": b"\x01ABCD\0"}
        files, _ = run([Change(row("Media/Misc/x.bin", "off:0x1", b"ABCD"), b"ko")], data)
        self.assertEqual(bytes(files["Media/Misc/x.bin"]), b"\x01ko\0\0\0")
        with self.assertRaisesRegex(textpatch.PatchError, "more than"):
            run([Change(row("Media/Misc/x.bin", "off:0x1", b"ABCD"), b"longer")], data)


if __name__ == "__main__":
    unittest.main()
