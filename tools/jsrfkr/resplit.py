"""Re-split a message's Korean pages into the English page count (design 20261023-i026).

English mode shows language 1 with the English timing (page count, per-page
display values, start delay), which was made for the English voice. The
Korean follows the Japanese pages, so where the page counts differ the
Korean is laid out again over the English pages:

  1. words     the Korean pages become one run of words (split at spaces and
               '$n'); each gap between words has a strength: end of an
               original page 5, end of a sentence 4, a clause end (clause
               mark, line break, or a connective ending such as -고 -서 -면
               -는데 -지만) 3, after a particle (-은 -을 -에 -로 ...) 2,
               any other space 1
  2. targets   the English pages' share of the English letters gives, for
               each English page, the fraction of the text that should be
               shown by its end
  3. choose    dynamic programming picks the page breaks: the Korean letter
               fraction at each break should match its target, weak gaps
               cost extra, and every page must fit the window (lines, width,
               page buffer) once wrapped
  4. wrap      each new page is wrapped into the fewest lines that fit, with
               the line breaks chosen to keep lines even

The words and their order never change; only spaces and '$n' between them
are rewritten. resplit() returns None when no layout fits.
"""
import hangul    # tools/font, on sys.path through jsrfkr

from . import msgscript, screen

STRONG_PAGE, STRONG_SENTENCE, STRONG_CLAUSE, STRONG_PHRASE, STRONG_SPACE = 5, 4, 3, 2, 1
# Cost of a page break at a gap of each strength, in units of text fraction:
# a break moves up to 0.1 of the text away from its target to land on a
# sentence end rather than a clause end, and up to 0.35 rather than inside a
# phrase. Korean puts the verb last, so an English-style mid-sentence break
# would show words whose meaning belongs to another English page.
GAP_COST = {STRONG_PAGE: 0.0, STRONG_SENTENCE: 0.0, STRONG_CLAUSE: 0.1, STRONG_PHRASE: 0.2, STRONG_SPACE: 0.35}
SENTENCE_END = {b".", b"!", b"?", b"\x81\x42", b"\x81\x48", b"\x81\x49", b"\x81\x63"}   # . ! ? 。 ？ ！ …
CLAUSE_MARK = {b",", b"\x81\x41", b"\x81\x43", b":", b"\x81\x46"}                        # , 、 ， : ：
CLOSERS = {b"\x81\x68", b"\x81\x76", b"\x81\x78", b"\"", b"'", b")", b"\x81\x6a"}        # ” 」 』 " ' ) ）
SPACES = (b" ", b"\x81\x40")
END_PAGE = b"$e"
# Last syllable of a word: connective endings and particles.
CONNECTIVE = set("고서며면데만까록러게")
PARTICLE = set("은는이가을를에로와과도께테")


class Word:
    def __init__(self, tokens):
        self.tokens = tokens
        self.letters = sum(1 for t in tokens if not (t[:1] == b"$" and len(t) > 1))
        self.gap = STRONG_SPACE         # strength of the gap after this word

    @property
    def data(self):
        return b"".join(self.tokens)


def _sentence_end(tokens):
    toks = [t for t in tokens if t not in CLOSERS]
    return bool(toks) and toks[-1] in SENTENCE_END


def _last_syllable(tokens):
    for t in reversed(tokens):
        if len(t) == 2 and (t[0] << 8 | t[1]) in hangul.SYLLABLE_OF:
            return hangul.SYLLABLE_OF[t[0] << 8 | t[1]]
        if t not in CLOSERS:
            return None
    return None


def gap_after(tokens, line_end=False):
    """Strength of the gap after a word (its tokens)."""
    if _sentence_end(tokens):
        return STRONG_SENTENCE
    syllable = _last_syllable(tokens)
    if tokens[-1] in CLAUSE_MARK or line_end or syllable in CONNECTIVE:
        return STRONG_CLAUSE
    if syllable in PARTICLE:
        return STRONG_PHRASE
    return STRONG_SPACE


def words_of(pages):
    """The words of a list of page byte strings, with gap strengths."""
    out = []
    for page in pages:
        current = []
        for t in msgscript.tokens(page) + [b"$n"]:
            if t in SPACES or t == b"$n":
                if current:
                    w = Word(current)
                    w.gap = gap_after(current, t == b"$n")
                    out.append(w)
                    current = []
            else:
                current.append(t)
        if out:
            out[-1].gap = STRONG_PAGE
    return out


def letters(page):
    return sum(1 for t in msgscript.tokens(page)
               if t not in SPACES and t != b"$n" and not (t[:1] == b"$" and len(t) > 1))


def _fits(lines, single, width, max_lines):
    if len(lines) > max_lines:
        return False
    size = sum(len(l) for l in lines) + 2 * (len(lines) - 1)
    if size + screen.CENTRE_BYTES * len(lines) + 1 >= screen.PAGE_BUFFER:
        return False
    return all(screen.line_width(msgscript.tokens(l), single) <= width for l in lines)


def wrap(words, single, width, max_lines):
    """The fewest even lines (bytes each) that hold the words, or None."""
    n = len(words)
    sp = screen.SPACE_ADVANCE
    w = [screen.line_width(word.tokens, single) for word in words]

    def line_width(i, j):
        return sum(w[i:j]) + sp * (j - i - 1)

    for count in range(1, max_lines + 1):
        if count > n:
            break
        # best[k][j]: the smallest widest line for words[:j] in k lines
        INF = float("inf")
        best = [[INF] * (n + 1) for _ in range(count + 1)]
        back = [[0] * (n + 1) for _ in range(count + 1)]
        best[0][0] = 0.0
        for k in range(1, count + 1):
            for j in range(k, n + 1):
                for i in range(k - 1, j):
                    if best[k - 1][i] == INF:
                        continue
                    lw = line_width(i, j)
                    if lw > width:
                        continue
                    v = max(best[k - 1][i], lw)
                    if v < best[k][j]:
                        best[k][j], back[k][j] = v, i
        if best[count][n] == INF:
            continue
        cuts, j = [], n
        for k in range(count, 0, -1):
            i = back[k][j]
            cuts.append((i, j))
            j = i
        lines = [b" ".join(word.data for word in words[i:j]) for i, j in reversed(cuts)]
        if _fits(lines, single, width, max_lines):
            return lines
    return None


def targets(english_pages):
    """Cumulative fraction of the English letters at the end of each page."""
    counts = [max(letters(p), 1) for p in english_pages]
    total, run, out = sum(counts), 0, []
    for c in counts:
        run += c
        out.append(run / total)
    return out


def resplit(korean_pages, english_pages, single, width=screen.GROUP_WIDTH["event"],
            max_lines=screen.GROUP_LINES["event"]):
    """Korean text pages (bytes, no '$e' page) laid out over len(english_pages)
    pages; a list of page bytes, or None when no layout fits."""
    words = words_of(korean_pages)
    n, pages = len(words), len(english_pages)
    if pages < 1 or n < pages:
        return None
    total = sum(word.letters for word in words) or 1
    cum = [0]
    for word in words:
        cum.append(cum[-1] + word.letters)
    goal = targets(english_pages)
    cache = {}

    def page_lines(i, j):
        if (i, j) not in cache:
            cache[(i, j)] = wrap(words[i:j], single, width, max_lines)
        return cache[(i, j)]

    INF = float("inf")
    # cost[k][j]: best cost of k pages holding words[:j]
    cost = [[INF] * (n + 1) for _ in range(pages + 1)]
    back = [[0] * (n + 1) for _ in range(pages + 1)]
    cost[0][0] = 0.0
    for k in range(1, pages + 1):
        last = k == pages
        for j in range(k, n + 1):
            if last and j != n:
                continue
            gap = 0.0 if last else abs(cum[j] / total - goal[k - 1]) + GAP_COST[words[j - 1].gap]
            for i in range(k - 1, j):
                if cost[k - 1][i] == INF or page_lines(i, j) is None:
                    continue
                v = cost[k - 1][i] + gap
                if v < cost[k][j]:
                    cost[k][j], back[k][j] = v, i
    if cost[pages][n] == INF:
        return None
    cuts, j = [], n
    for k in range(pages, 0, -1):
        i = back[k][j]
        cuts.append((i, j))
        j = i
    return [b"$n".join(page_lines(i, j)) for i, j in reversed(cuts)]


def spread(total, weights, count):
    """`total` split over `count` text pages in proportion to `weights`
    (integers summing to `total`, the remainder added from the first page)."""
    weights = list(weights[:count]) + [0] * (count - len(weights[:count]))
    if sum(weights) <= 0:
        weights = [1] * count
    base = [total * w // sum(weights) for w in weights]
    for k in range(total - sum(base)):
        base[k % count] += 1
    return base
