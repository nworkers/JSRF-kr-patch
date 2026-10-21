"""The glossary docs/kb/glossary.md as data: term hints for translators (design 20261021-i015 §2, §4).

Every Markdown table whose header starts with '| 일본어 | 영어 | 한국어 |'
contributes rows (Japanese, English, Korean); other tables and text are
ignored. Japanese cells may hold several spellings separated by ' / '.
hints() lists the Korean forms of the terms found in a Japanese string,
longest terms first and without overlaps.
"""
import os
from collections import namedtuple

from . import ROOT

PATH = os.path.join(ROOT, "docs", "kb", "glossary.md")
HEADER = ("일본어", "영어", "한국어")

Term = namedtuple("Term", "japanese english korean")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse(text):
    terms, in_table = [], False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            in_table = False
            continue
        cells = _cells(line)
        if tuple(cells[:3]) == HEADER:
            in_table = True
            continue
        if not in_table or set("".join(cells)) <= set("-: "):
            continue
        if len(cells) >= 3 and cells[0] and cells[2]:
            for ja in cells[0].split(" / "):
                ja = ja.strip().strip("`")
                if ja:
                    terms.append(Term(ja, cells[1].strip("`"), cells[2].strip("`")))
    return terms


def load(path=PATH):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return parse(f.read())


def hints(japanese, terms):
    """Korean forms of the terms in `japanese` (a str), in order of appearance."""
    taken, found = [False] * len(japanese), []
    for t in sorted(terms, key=lambda t: -len(t.japanese)):
        start = japanese.find(t.japanese)
        while start >= 0:
            end = start + len(t.japanese)
            if not any(taken[start:end]):
                taken[start:end] = [True] * (end - start)
                found.append((start, t))
                break
            start = japanese.find(t.japanese, start + 1)
    out = []
    for _, t in sorted(found, key=lambda p: p[0]):
        item = f"{t.japanese}={t.korean}"
        if item not in out:
            out.append(item)
    return out
