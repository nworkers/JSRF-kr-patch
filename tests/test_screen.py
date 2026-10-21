"""Unit tests for tools/jsrfkr/screen.py (no game data)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from jsrfkr import screen  # noqa: E402

DOUBLE = "あ".encode("cp932")


def levels(issues):
    return [i.level for i in issues]


class ScreenTest(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(screen.structure(b"a$rb$c1$e$r$bj\x05"), [b"$r", b"$e", b"$r", b"$bj\x05"])
        ok = screen.check("mission", b"A$r$e$r", DOUBLE * 3 + b"$r$e$r", {})
        self.assertEqual(ok, [])
        bad = screen.check("mission", b"A$r$e$r", b"A$rB$r$e$r", {})
        self.assertEqual(levels(bad), ["error"])
        self.assertEqual(levels(screen.check("event", b"A", b"A$rB", {})), ["error"])

    def test_page_buffer(self):
        self.assertEqual(screen.check("event", b"A", b"$c1" * 80, {}), [])
        issues = screen.check("event", b"A", b"$c1" * 84, {})
        self.assertIn("error", levels(issues))

    def test_width_and_lines(self):
        line = DOUBLE * 22                                  # 528 px: at the event limit
        self.assertEqual(screen.check("event", b"A", line, {}), [])
        self.assertEqual(levels(screen.check("event", b"A", line + DOUBLE, {})), ["warning"])
        self.assertEqual(levels(screen.check("talk", b"A", DOUBLE * 20, {})), ["warning"])   # 480 > 456
        four = b"$n".join([DOUBLE] * 4)
        self.assertEqual(levels(screen.check("event", b"A", four, {})), ["warning"])
        # missions and XBE strings: at least their own original
        self.assertEqual(screen.check("xbe", four, four, {}), [])
        wide = DOUBLE * 30
        self.assertEqual(screen.check("xbe", wide, wide, {}), [])

    def test_single_widths(self):
        widths = screen.single_widths([(0x41, 1, -1, -1), (0x69, 2, 10, 5)])
        self.assertAlmostEqual(widths[0x41], 21 * 0.76 - 4)
        self.assertAlmostEqual(widths[0x69], 5 * 0.76 - 4)
        self.assertAlmostEqual(screen.line_width([b"A", b" ", DOUBLE], widths), 21 * 0.76 - 4 + 21 * 0.532 + 24)


if __name__ == "__main__":
    unittest.main()
