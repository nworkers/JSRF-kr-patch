"""Unit tests for tools/site/build_site.py (no network: the API is not called)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "site"))
import build_site  # noqa: E402

RELEASE = {
    "tag_name": "v9.9.9", "html_url": "https://github.com/o/r/releases/tag/v9.9.9",
    "assets": [
        {"name": "jsrf-kr-patch-v9.9.9-windows-x64.zip", "size": 2 * 1048576,
         "digest": "sha256:abcdef0123456789", "browser_download_url": "https://dl/w.zip"},
        {"name": "jsrf-kr-patch-v9.9.9-python.zip", "size": 4096, "browser_download_url": "https://dl/p.zip"},
        {"name": "SHA256SUMS.txt", "size": 10, "browser_download_url": "https://dl/s.txt"},
    ],
}


class SiteTest(unittest.TestCase):
    def test_release_notes(self):
        notes = build_site.release_notes()
        self.assertTrue(notes)
        versions = [v for v, *_ in notes]
        self.assertEqual(versions, sorted(versions, key=build_site.semver, reverse=True))
        for v, title, summary, issues in notes:
            with self.subTest(v):
                self.assertTrue(issues, "every release lists a resolved issue")
                self.assertNotIn("`", summary)
                self.assertNotIn("**", summary)

    def test_downloads(self):
        out = build_site.downloads(RELEASE)
        self.assertIn('href="https://dl/w.zip"', out)
        self.assertIn("2.0 MB", out)
        self.assertIn("sha256 abcdef012345", out)
        self.assertIn('href="https://dl/p.zip"', out)
        self.assertIn("SHA256SUMS.txt", out)
        self.assertNotIn("Linux", out)                  # absent asset, no button

    def test_downloads_without_release(self):
        out = build_site.downloads(None)
        self.assertIn("https://github.com/nworkers/JSRF-kr-patch/releases", out)

    def test_build_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            argv = sys.argv
            sys.argv = ["build_site.py", "--offline", "--out", os.path.join(tmp, "site")]
            try:
                build_site.main()
            finally:
                sys.argv = argv
            with open(os.path.join(tmp, "site", "index.html"), encoding="utf-8") as f:
                page = f.read()
            for marker in ("{version}", "<!-- DOWNLOADS -->", "<!-- RELEASES -->"):
                self.assertNotIn(marker, page)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "site", "screenshots", "talk-ko.jpg")))


if __name__ == "__main__":
    unittest.main()
