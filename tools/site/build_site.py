"""Build the introduction site (design 20261023-i023) into build/site/. Standard library only.

  docs/sites/static/      copied as is; index.html gets three fills:
                            {version}        VERSION
                            <!-- DOWNLOADS -->  buttons for the latest GitHub release's
                                             packages (GitHub Releases API), or a link
                                             to the releases page when there is none
                            <!-- RELEASES -->   a timeline from docs/release-notes/v*.md
                                             (title, summary, resolved issues)
  docs/screenshots/       copied to build/site/screenshots/

GITHUB_TOKEN, when set, is sent to the API (read only). --offline skips the API.

usage: python -I tools/site/build_site.py [--out build/site] [--offline]
"""
import html
import json
import os
import re
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = "nworkers/JSRF-kr-patch"
STATIC = os.path.join(ROOT, "docs", "sites", "static")
SHOTS = os.path.join(ROOT, "docs", "screenshots")
NOTES = os.path.join(ROOT, "docs", "release-notes")
PACKAGES = (                         # asset suffix, css class, OS label, kind
    ("-windows-x64.zip", "dl-win", "Windows", "실행 파일 · Python 필요 없음"),
    ("-linux-x64.tar.gz", "dl-linux", "Linux", "실행 파일 · Python 필요 없음"),
    ("-python.zip", "dl-py", "Python", "스크립트판 · Python 3.10+"),
)
ISSUE = re.compile(r"\[(#\d+)\]\((https://github\.com/[^)]+/issues/\d+)\)\s*\|\s*([^|]+?)\s*\|")


def esc(s):
    return html.escape(s, quote=True)


def semver(name):
    return tuple(int(x) for x in re.findall(r"\d+", name)[:3])


def release_notes():
    """[(version, title, summary, [(issue, url, text)])], newest first, from the Korean half."""
    out = []
    for name in os.listdir(NOTES):
        if not re.fullmatch(r"v\d+\.\d+\.\d+\.md", name):
            continue
        with open(os.path.join(NOTES, name), encoding="utf-8") as f:
            ko = f.read().split("\n---\n")[0]
        lines = [l.strip() for l in ko.splitlines()]
        title = next((l[3:] for l in lines if l.startswith("## ")), name[:-3])
        summary = next((l for l in lines if l and not l.startswith(("#", "|", "*", "-"))), "")
        summary = re.sub(r"\*\*(.+?)\*\*", r"\1", summary).replace("`", "")
        body = ko.split("### 해결된 issue", 1)[1].split("###", 1)[0] if "### 해결된 issue" in ko else ""
        issues = [(m.group(1), m.group(2), m.group(3).replace("`", "")) for m in ISSUE.finditer(body)]
        out.append((name[:-3], title, summary, issues))
    return sorted(out, key=lambda r: semver(r[0]), reverse=True)


def timeline(notes, limit=8):
    parts = []
    for v, title, summary, issues in notes[:limit]:
        items = "".join(f'<li><a href="{esc(u)}">{esc(i)}</a> {esc(t)}</li>' for i, u, t in issues)
        link = f"https://github.com/{REPO}/blob/main/docs/release-notes/{v}.md"
        parts.append(f'      <article class="release"><h3><a href="{esc(link)}">{esc(v)}</a></h3>'
                     f"<p>{esc(summary)}</p><ul>{items}</ul></article>")
    parts.append(f'      <p class="release-more"><a href="https://github.com/{REPO}/tree/main/docs/release-notes">'
                 "전체 릴리스 노트</a> · <a href=\"https://github.com/" + REPO + "/releases\">GitHub 릴리스</a></p>")
    return "\n".join(parts)


def latest_release(offline):
    if offline:
        return None
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "jsrf-kr-site"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as err:            # no release yet (404) or no network: fall back to a link
        print(f"releases API: {err}; using the releases page link", file=sys.stderr)
        return None


def size(n):
    return f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{n / 1024:.0f} KB"


def downloads(release):
    page = f"https://github.com/{REPO}/releases"
    if not release:
        return (f'      <a class="dl dl-wide" href="{page}"><span class="dl-os">Releases</span>'
                '<span class="dl-kind">GitHub 릴리스 페이지에서 받기</span>'
                '<span class="dl-meta">Windows · Linux 실행 파일과 Python판</span></a>')
    assets = {a["name"]: a for a in release.get("assets", [])}
    tag = release.get("tag_name", "")
    parts = []
    for suffix, cls, osname, kind in PACKAGES:
        a = next((a for n, a in assets.items() if n.endswith(suffix)), None)
        if a is None:
            continue
        digest = (a.get("digest") or "").removeprefix("sha256:")
        meta = f"{esc(tag)} · {size(a.get('size', 0))}" + (f" · sha256 {esc(digest[:12])}…" if digest else "")
        parts.append(f'      <a class="dl {cls}" href="{esc(a["browser_download_url"])}">'
                     f'<span class="dl-os">{osname}</span><span class="dl-kind">{kind}</span>'
                     f'<span class="dl-file">{esc(a["name"])}</span><span class="dl-meta">{meta}</span></a>')
    sums = assets.get("SHA256SUMS.txt")
    if sums:
        parts.append(f'      <p class="download-sums">체크섬: <a href="{esc(sums["browser_download_url"])}">SHA256SUMS.txt</a> · '
                     f'<a href="{esc(release.get("html_url", page))}">릴리스 노트</a></p>')
    return "\n".join(parts) if parts else downloads(None)


def main():
    args = sys.argv[1:]
    offline = "--offline" in args
    if offline:
        args.remove("--offline")
    out = os.path.join(ROOT, "build", "site")
    if "--out" in args:
        out = os.path.abspath(args[args.index("--out") + 1])
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(STATIC, out)
    if os.path.isdir(SHOTS):
        shutil.copytree(SHOTS, os.path.join(out, "screenshots"),
                        ignore=shutil.ignore_patterns("README.md"))
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as f:
        version = f.read().strip()
    release = latest_release(offline)
    index = os.path.join(out, "index.html")
    with open(index, encoding="utf-8") as f:
        page = f.read()
    shown = release.get("tag_name", "").removeprefix("v") if release else version
    for marker, fill in (("{version}", shown), ("<!-- DOWNLOADS -->", downloads(release)),
                         ("<!-- RELEASES -->", timeline(release_notes()))):
        if marker not in page:
            raise SystemExit(f"index.html has no {marker}")
        page = page.replace(marker, fill)
    with open(index, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    print(f"wrote {out} (version {shown}, release {'from the API' if release else 'link only'})")


if __name__ == "__main__":
    main()
