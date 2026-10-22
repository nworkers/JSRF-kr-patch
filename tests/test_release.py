"""Unit tests for tools/release.py (no game data, no Nuitka)."""
import os
import sys
import tarfile
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import release  # noqa: E402

NOTES = """## X v1.2.3

### 해결된 issue

| issue | 내용 | 커밋 |
|---|---|---|
| [#7](https://github.com/o/r/issues/7) | a | `abc` |

### 바뀐 것

* x

---

## X v1.2.3

### Resolved issues

| Issue | Content | Commits |
|---|---|---|
| [#7](https://github.com/o/r/issues/7) | a | `abc` |

### Changes
"""


class NotesTest(unittest.TestCase):
    def test_both_sections(self):
        self.assertEqual(release.check_notes(NOTES), ["https://github.com/o/r/issues/7"])

    def test_missing_or_empty(self):
        for broken in (NOTES.replace("### Resolved issues", "### Fixed"),
                       NOTES.replace("[#7](https://github.com/o/r/issues/7) | a | `abc` |\n\n### 바뀐", "x |\n\n### 바뀐")):
            with self.subTest(broken[:0]), self.assertRaises(release.ReleaseError):
                release.check_notes(broken)

    def test_tag(self):
        release.check_tag("1.2.3", "v1.2.3")
        release.check_tag("1.2.3", None)
        with self.assertRaises(release.ReleaseError):
            release.check_tag("1.2.3", "v1.2.4")

    def test_repository_notes(self):
        # every committed release note keeps both resolved-issue sections
        folder = os.path.join(release.ROOT, "docs", "release-notes")
        for name in sorted(os.listdir(folder)):
            with self.subTest(name), open(os.path.join(folder, name), encoding="utf-8") as f:
                release.check_notes(f.read())


class ContentsTest(unittest.TestCase):
    def test_modules_are_repository_files_only(self):
        files = [os.path.relpath(p, release.ROOT).replace(os.sep, "/") for p in release.patcher_modules()]
        self.assertIn("tools/patch.py", files)
        self.assertIn("tools/jsrfkr/english.py", files)
        self.assertIn("tools/font/build_font.py", files)
        self.assertFalse([f for f in files if f.startswith(("tests/", "tools/analysis/en_slots", "tools/poc/"))])

    def test_data_files(self):
        data = release.data_files()
        self.assertIn("patch/manifest.json", data)
        self.assertIn("patch/xbe-en.tsv", data)
        self.assertIn("patch/font/OFL.txt", data)
        self.assertFalse([d for d in data if d.startswith("patch/poc/")])
        release.check_names(data)

    def test_forbidden_names(self):
        for bad in ("x/default.xbe", "x/game.iso", "x/roms/a", "x/out/b", "x/work/c"):
            with self.subTest(bad), self.assertRaises(release.ReleaseError):
                release.check_names([bad])


class ArchiveTest(unittest.TestCase):
    ENTRIES = {"top/b.txt": (b"b", 0o644), "top/a.bin": (b"\x00\x01", 0o755)}

    def test_zip_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = os.path.join(tmp, "a.zip"), os.path.join(tmp, "b.zip")
            release.write_zip(a, self.ENTRIES)
            release.write_zip(b, dict(reversed(list(self.ENTRIES.items()))))
            self.assertEqual(open(a, "rb").read(), open(b, "rb").read())
            with zipfile.ZipFile(a) as z:
                self.assertEqual(z.namelist(), ["top/a.bin", "top/b.txt"])
                self.assertEqual((z.getinfo("top/a.bin").external_attr >> 16) & 0o777, 0o755)

    def test_targz_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = os.path.join(tmp, "a.tar.gz"), os.path.join(tmp, "b.tar.gz")
            release.write_targz(a, self.ENTRIES)
            release.write_targz(b, self.ENTRIES)
            self.assertEqual(open(a, "rb").read(), open(b, "rb").read())
            with tarfile.open(a) as t:
                info = t.getmember("top/a.bin")
                self.assertEqual((info.mode, info.mtime, info.uid), (0o755, 0, 0))


if __name__ == "__main__":
    unittest.main()
