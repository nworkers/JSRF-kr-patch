"""Unit tests for tools/jsrfkr/resplit.py and english.english_timing (no game data)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jsrfkr import english, msgscript, resplit, screen  # noqa: E402
import hangul  # noqa: E402  (tools/font, on sys.path through jsrfkr)
from test_msgscript import script  # noqa: E402


def ko(text):
    """Korean (and ASCII) text as game bytes, by the fixed Hangul mapping."""
    out = bytearray()
    for ch in text:
        code = hangul.CODE_OF.get(ch)
        out += bytes((code >> 8, code & 0xFF)) if code else ch.encode("cp932")
    return bytes(out)


class WordsTest(unittest.TestCase):
    def test_gaps(self):
        words = resplit.words_of([ko("가자. 나는 먹고 잤다, 하늘을 본다$n밤 하늘"), ko("끝")])
        gaps = [w.gap for w in words]
        self.assertEqual(gaps, [resplit.STRONG_SENTENCE,     # 가자.
                                resplit.STRONG_PHRASE,       # 나는
                                resplit.STRONG_CLAUSE,       # 먹고
                                resplit.STRONG_CLAUSE,       # 잤다,
                                resplit.STRONG_PHRASE,       # 하늘을
                                resplit.STRONG_CLAUSE,       # 본다 ($n)
                                resplit.STRONG_SPACE,        # 밤
                                resplit.STRONG_PAGE,         # 하늘 (end of a page)
                                resplit.STRONG_PAGE])        # 끝

    def test_letters_skip_codes_and_spaces(self):
        self.assertEqual(resplit.letters(ko("가 나$n다") + b"$c1"), 3)

    def test_closing_quote_after_sentence_end(self):
        self.assertEqual(resplit.gap_after(msgscript.tokens(ko("그래!”"))), resplit.STRONG_SENTENCE)


class WrapTest(unittest.TestCase):
    def test_one_line_when_it_fits(self):
        self.assertEqual(resplit.wrap(resplit.words_of([ko("가 나")]), {}, 528, 3), [ko("가 나")])

    def test_even_lines(self):
        words = resplit.words_of([ko("가가가가 나나나나 다다다다 라라라라")])
        lines = resplit.wrap(words, {}, 24 * 9, 3)       # nine Hangul per line at most
        self.assertEqual(lines, [ko("가가가가 나나나나"), ko("다다다다 라라라라")])

    def test_none_when_it_cannot_fit(self):
        self.assertIsNone(resplit.wrap(resplit.words_of([ko("가가가가가")]), {}, 24 * 4, 3))


class ResplitTest(unittest.TestCase):
    def test_breaks_on_sentence_near_target(self):
        korean = [ko("하나 둘 셋. 넷 다섯 여섯 일곱. 여덟 아홉")]
        english = [b"one two three.", b"four five six seven.", b"eight nine"]
        self.assertEqual(resplit.resplit(korean, english, {}),
                         [ko("하나 둘 셋."), ko("넷 다섯 여섯 일곱."), ko("여덟 아홉")])

    def test_words_kept_in_order(self):
        korean = [ko("가나 다라 마바 사아"), ko("자차 카타$n파하")]
        out = resplit.resplit(korean, [b"aa", b"bb", b"cc", b"dd", b"ee"], {})
        self.assertEqual(len(out), 5)
        self.assertEqual([w.data for w in resplit.words_of(out)], [w.data for w in resplit.words_of(korean)])

    def test_pages_fit_the_window(self):
        long = " ".join(["가나다라마바사"] * 12)
        out = resplit.resplit([ko(long)], [b"a" * 10, b"b" * 10], {})
        for page in out:
            self.assertEqual(screen.check("event", page, page, {}), [])

    def test_none_with_too_few_words(self):
        self.assertIsNone(resplit.resplit([ko("가나")], [b"a", b"b"], {}))

    def test_spread(self):
        self.assertEqual(resplit.spread(100, [1, 3], 2), [25, 75])
        self.assertEqual(resplit.spread(10, [1, 1, 1], 3), [4, 3, 3])
        self.assertEqual(resplit.spread(9, [0, 0], 2), [5, 4])


class EnglishTimingTest(unittest.TestCase):
    def build(self, korean, english, kv, ev):
        text = b"".join(p + b"$r" for p in korean + english)
        return script([[len(korean)], [len(english)]], [kv, ev], text)

    def lang1(self, data):
        s = msgscript.parse(data)
        return [p.data for p in s.pages[1][0]], s.values[1], [f[1][0] for f in s.fields]

    def test_same_page_count_keeps_english_values(self):
        data = self.build([ko("가나"), b"$e"], [b"Hi", b"$e"], [99, 0], [140, 0])
        counts = {}
        pages, values, fields = self.lang1(english.english_timing(data, counts=counts))
        self.assertEqual((pages, values), ([ko("가나"), b"$e"], [140, 0]))
        self.assertEqual(fields[1:], [11, 21, 31, 41])      # English fields 1-4 (script() fills f*10+l)
        self.assertEqual(counts, {"same": 1})

    def test_resplit_takes_english_pages_and_values(self):
        data = self.build([ko("하나 둘. 셋 넷."), b"$e"], [b"one two.", b"three four.", b"$e"], [200, 0], [70, 90, 0])
        pages, values, fields = self.lang1(english.english_timing(data))
        self.assertEqual(pages, [ko("하나 둘."), ko("셋 넷."), b"$e"])
        self.assertEqual(values, [70, 90, 0])
        self.assertEqual(fields[0], 3)

    def test_spread_when_no_layout(self):
        data = self.build([ko("하나"), b"$e"], [b"one", b"two", b"$e"], [50, 0], [70, 90, 0])
        counts = {}
        pages, values, _ = self.lang1(english.english_timing(data, counts=counts))
        self.assertEqual((pages, values), ([ko("하나"), b"$e"], [160, 0]))
        self.assertEqual(counts, {"spread": 1})

    def test_language0_unchanged(self):
        data = self.build([ko("하나 둘. 셋 넷."), b"$e"], [b"a.", b"b.", b"$e"], [200, 0], [70, 90, 0])
        before, after = msgscript.parse(data), msgscript.parse(english.english_timing(data))
        self.assertEqual([p.data for p in after.pages[0][0]], [p.data for p in before.pages[0][0]])
        self.assertEqual(after.values[0], before.values[0])


if __name__ == "__main__":
    unittest.main()
