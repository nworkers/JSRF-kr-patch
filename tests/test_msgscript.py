"""Unit tests for tools/jsrfkr/msgscript.py on synthetic data (no game data)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import msgscript  # noqa: E402
from jsrfkr.msgscript import FormatError  # noqa: E402

JA = "あいう".encode("cp932")          # double-byte text
BI = "ビ".encode("cp932")              # 0x83 0x72: its trail byte is 'r'


def script(counts, values, text, head=None):
    """counts[l][m]; values: list per (l, m); text: the raw text bytes."""
    L, M = len(counts), len(counts[0])
    head = head or [20, L, L, 3, M, M, 0, 0, 0]
    out = struct.pack("<9I", *head)
    fields = [counts] + [[[f * 10 + l for _ in range(M)] for l in range(L)] for f in range(1, 5)]
    for f in fields:
        for row in f:
            out += struct.pack(f"<{M}I", *row)
    for v in values:
        out += struct.pack(f"<{len(v)}I", *v)
    return out + text


# Two languages, two messages each: "page$r ... $e$r" per message.
EVENT = script([[2, 1], [3, 1]], [[30, 0], [0], [30, 60, 0], [0]],
               JA + b"$n" + BI + b"$r$e$r" + b"$e$r" + b"Hi$rthere$r$e$r" + b"$e$r")
# One message per language; branch page, two parts split by $e$r, a choice page.
TALK = script([[6], [2]], [[30] * 5 + [0], [30, 0]],
              b"$p$bc\x00$bj\x04$bo\x01$r" + JA + b"$r$s\x04\x05$r$e$r" + BI + b"$r$e$r" + b"Yo$r$e$r",
              head=[20, 2, 1, 1, 1, 1, 0, 0, 0])


class MsgScriptTest(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(msgscript.tokens(BI + b"$r"), [BI, b"$r"])
        self.assertEqual(msgscript.tokens(b"$c5A$bj\x24B$s\x01\x02$$"), [b"$c5", b"A", b"$bj\x24", b"B", b"$s\x01\x02", b"$$"])
        self.assertEqual(msgscript.tokens(b"$x123$g05$n"), [b"$x123", b"$g05", b"$n"])

    def test_parse_event(self):
        s = msgscript.parse(EVENT)
        self.assertEqual((s.languages, s.messages), (2, 2))
        self.assertEqual([p.data for p in s.pages[0][0]], [JA + b"$n" + BI, b"$e"])
        self.assertEqual([p.data for p in s.block(1)], [b"Hi", b"there", b"$e", b"$e"])
        start = 4 * (9 + 5 * 4 + 7)
        self.assertEqual(s.pages[0][0][0].offset, start)
        for lang in s.pages:
            for msg in lang:
                for p in msg:
                    self.assertEqual(EVENT[p.offset:p.offset + len(p.data) + 2], p.data + b"$r")
        self.assertEqual(msgscript.build(s), EVENT)

    def test_parse_talk(self):
        s = msgscript.parse(TALK)
        block = s.block(0)
        self.assertEqual(len(block), 6)
        self.assertTrue(msgscript.is_control(block[0].data))
        self.assertTrue(msgscript.is_control(block[2].data))
        self.assertFalse(msgscript.is_control(block[1].data))
        self.assertEqual(msgscript.build(s), TALK)

    def test_letters(self):
        self.assertTrue(msgscript.has_letters(JA))
        self.assertFalse(msgscript.has_letters(b"$e"))
        self.assertFalse(msgscript.has_letters(b" $n\x81\x40$c1"))
        self.assertTrue(msgscript.has_letters(b"$c1A"))

    def test_build_counts_from_pages(self):
        s = msgscript.parse(EVENT)
        page = s.pages[0][0][0]
        s.pages[0][0][0] = page._replace(data=b"longer page text")
        again = msgscript.parse(msgscript.build(s))
        self.assertEqual(again.pages[0][0][0].data, b"longer page text")
        s.pages[0][0].insert(0, page)
        with self.assertRaisesRegex(ValueError, "page values"):
            msgscript.build(s)

    def test_errors(self):
        for name, data in [("short", EVENT[:20]), ("missing page", EVENT[:-4]),
                           ("extra bytes", EVENT + b"x"), ("languages", script([[1]], [[0]], b"$r", head=[0] * 9))]:
            with self.subTest(name), self.assertRaises(FormatError):
                msgscript.parse(data)


if __name__ == "__main__":
    unittest.main()
