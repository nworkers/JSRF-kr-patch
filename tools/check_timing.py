"""Check the English-mode cutscene subtitle timing of a patched build (design 20261023-i026).

Builds the patched files in memory from the dump (as tools/patch.py does, no
output folder) and checks every event message (e###.dat item 2/0):

  * language 1 has the original English page count, fields 1-4 and
    per-page values (or, where no layout fitted, the English total)
  * its Korean words are those of language 0, in the same order
  * every page fits the window (lines, width, page buffer; jsrfkr.screen)

and counts the kinds of page break the re-split chose (sentence, clause,
particle, other) and how far each break is from its English target. Prints
counts only, no text. --review writes work/text/timing-review.txt with the
English and Korean pages side by side (original text: never commit it).

usage: python -I tools/check_timing.py <dump folder> [--review]
Exit code 1 when a check fails.
"""
import contextlib
import io
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jsrfkr import ROOT, container, msgscript, pipeline, resplit, screen  # noqa: E402
from jsrfkr.xbe import Xbe  # noqa: E402
import hangul  # noqa: E402  (tools/font, on sys.path through jsrfkr)
import patch  # noqa: E402

EVENT_DIR = "Media/Event/Event/"
KINDS = {resplit.STRONG_PAGE: "sentence", resplit.STRONG_SENTENCE: "sentence",
         resplit.STRONG_CLAUSE: "clause", resplit.STRONG_PHRASE: "particle", resplit.STRONG_SPACE: "other"}


def decode(b):
    out = []
    for t in msgscript.tokens(b):
        code = t[0] << 8 | t[1] if len(t) == 2 else None
        out.append(hangul.SYLLABLE_OF[code] if code in hangul.SYLLABLE_OF else t.decode("cp932", "replace"))
    return "".join(out)


def words(pages):
    return [w.data for w in resplit.words_of(pages)]


def main():
    args = sys.argv[1:]
    review = "--review" in args
    if review:
        args.remove("--review")
    if len(args) != 1:
        raise SystemExit(__doc__)
    game = args[0]
    rows = patch.read_text(os.path.join(patch.PATCH, "text"))
    with contextlib.redirect_stdout(io.StringIO()):
        files = patch.build_files(game, rows, patch.xbepatch.load(os.path.join(patch.PATCH, "xbe")), False, True)
    single = pipeline.single_widths(Xbe(os.path.join(game, patch.XBE)))
    problems, kinds, errors = [], dict.fromkeys(("sentence", "clause", "particle", "other"), 0), []
    counts = {"same": 0, "resplit": 0, "spread": 0}
    lines = []
    for name in sorted(n for n in files if n.startswith(EVENT_DIR)):
        with open(os.path.join(game, name), "rb") as f:
            orig = msgscript.parse(container.parse(f.read()).get((2, 0)))
        new = msgscript.parse(container.parse(files[name]).get((2, 0)))
        M = orig.messages
        for m in range(M):
            where = f"{name} message {m}"
            ko0, en, ko1 = new.pages[0][m], orig.pages[1][m], new.pages[1][m]
            en_values, values = orig.values[M + m], new.values[M + m]
            if [f[1][m] for f in new.fields[1:]] != [f[1][m] for f in orig.fields[1:]]:
                problems.append(f"{where}: fields 1-4 are not the English ones")
            if len(ko1) == len(en):
                kind = "same" if len(ko0) == len(en) else "resplit"
                if values != en_values:
                    problems.append(f"{where}: per-page values are not the English ones")
            else:
                kind = "spread"
                if sum(values) != sum(en_values):
                    problems.append(f"{where}: total time {sum(values)} is not the English {sum(en_values)}")
            counts[kind] += 1
            if words([p.data for p in ko1]) != words([p.data for p in ko0]):
                problems.append(f"{where}: the Korean words differ from language 0")
            for k, p in enumerate(ko1):
                for issue in screen.check("event", p.data, p.data, single):
                    problems.append(f"{where} page {k}: {issue.message}")
            if kind != "resplit":
                continue
            text = [p.data for p in ko1[:-1]]
            goal, total, run = resplit.targets([p.data for p in en[:-1]]), sum(map(resplit.letters, text)), 0
            for g, page in zip(goal[:-1], text[:-1]):
                run += resplit.letters(page)
                errors.append(abs(run / total - g))
                kinds[KINDS[resplit.gap_after(resplit.words_of([page])[-1].tokens)]] += 1
            if review:
                lines.append(f"== {where}: {len(ko0)} -> {len(ko1)} pages")
                for k, e in enumerate(en):
                    lines.append(f"  EN{k}: {decode(e.data)}")
                    lines.append(f"  KO{k}: {decode(ko1[k].data)}")
    n = sum(counts.values())
    print(f"event messages: {n} ({counts['same']} same page count, {counts['resplit']} re-split, "
          f"{counts['spread']} English total spread)")
    if errors:
        print(f"re-split breaks: {sum(kinds.values())} ({', '.join(f'{v} {k}' for k, v in kinds.items())}); "
              f"distance from the English targets: median {statistics.median(errors):.3f}, max {max(errors):.2f}")
    if review:
        path = os.path.join(ROOT, "work", "text", "timing-review.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        print(f"wrote {os.path.relpath(path, ROOT)} (original text: never commit it)")
    for p in problems[:20]:
        print(f"error: {p}")
    print(f"problems: {len(problems)}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
