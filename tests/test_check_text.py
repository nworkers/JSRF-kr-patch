"""Unit tests for tools/check_text.py helpers and tools/jsrfkr/glossary.py (no game data)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import check_text  # noqa: E402
from jsrfkr import glossary, reinsert, textpatch  # noqa: E402

GLOSSARY = """# 용어집

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| ビート | Beat | 비트 | |
| ゼロビート | Zero Beat | 제로 비트 | |
| ドーゲン坂 / ドーゲンザカ | Dogenzaka Hill | 도겐자카 | 지명 |

| 다른 표 | x | y |
|---|---|---|
| 無視 | a | b |
"""


def row(source, korean="", orig_len=4):
    return textpatch.Row(source, 1, "f", "off", None, 0, orig_len, "0" * 40, korean, "nul")


class GlossaryTest(unittest.TestCase):
    def test_parse(self):
        terms = glossary.parse(GLOSSARY)
        self.assertEqual([(t.japanese, t.korean) for t in terms],
                         [("ビート", "비트"), ("ゼロビート", "제로 비트"), ("ドーゲン坂", "도겐자카"), ("ドーゲンザカ", "도겐자카")])

    def test_hints(self):
        terms = glossary.parse(GLOSSARY)
        self.assertEqual(glossary.hints("ゼロビートとビートがドーゲン坂へ", terms),
                         ["ゼロビート=제로 비트", "ビート=비트", "ドーゲン坂=도겐자카"])
        self.assertEqual(glossary.hints("なし", terms), [])


class CheckTextTest(unittest.TestCase):
    def test_source_and_codes(self):
        self.assertEqual(check_text.source_of("xbe.tsv:12 default.xbe va:0x1: oops"), "xbe.tsv:12")
        self.assertEqual(check_text.codes_of("あ$nい$c5う$c1%d個"), ["$n", "$c5", "$c1", "%d"])

    def test_progress(self):
        rows = [row("a.tsv:2", "가"), row("a.tsv:3"), row("b.tsv:2", "나", 6)]
        done = [reinsert.Done(rows[0], 2, "in place"), reinsert.Done(rows[2], 8, "moved")]
        stats = check_text.progress(rows, done, ["b.tsv:2 f off:0x0: bad"], ["a.tsv:2 f off:0x0: wide"])
        self.assertEqual(list(stats), ["a.tsv", "b.tsv"])
        a, b = stats["a.tsv"], stats["b.tsv"]
        self.assertEqual((a["rows"], a["translated"], a["orig bytes"], a["korean bytes"], a["warnings"]), (2, 1, 8, 2, 1))
        self.assertEqual((b["moved"], b["errors"], b["korean bytes"]), (1, 1, 8))

    def test_limits(self):
        self.assertEqual(check_text.limits_of("event", b"x", {}), "3 lines/page, 528 px/line")
        wide = "あ".encode("cp932") * 30
        self.assertEqual(check_text.limits_of("xbe", wide, {}), "3 lines/page, 720 px/line")


if __name__ == "__main__":
    unittest.main()
