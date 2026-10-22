"""Build the release packages (design 20261023-i022 §2, §3, §8).

  notes  [--tag vX.Y.Z]            check VERSION (and the tag) and that
                                   docs/release-notes/v<VERSION>.md lists resolved
                                   issues in both languages
  python <dir> [--tag vX.Y.Z]      jsrf-kr-patch-v<VERSION>-python.zip: tools/patch.py,
                                   the modules it imports, patch data, documents
  binary <dir> [--tag vX.Y.Z]      jsrf-kr-patch-v<VERSION>-<os>-x64.zip (Windows) or
                                   .tar.gz (Linux): a standalone executable built
                                   with Nuitka 2.8.10 (tools/release-requirements.txt),
                                   the patch data built in, documents, licenses/
  sums   <dir>                     SHA256SUMS.txt for the packages in <dir>

Archives are deterministic (sorted entries, fixed times and owners). Every
package is unpacked again and checked: the patcher prints its usage, and no
game data (.xbe, .iso, roms/, out/, work/) is inside. Nothing here reads a dump.

usage: python -I tools/release.py notes|python|binary|sums ...
"""
import gzip
import hashlib
import importlib.metadata
import io
import modulefinder
import os
import re
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = "nworkers/JSRF-kr-patch"
NAME = "jsrf-kr-patch"
NUITKA = "2.8.10"                # the last Apache-2.0 release (design §8.2)
EPOCH = (1980, 1, 1, 0, 0, 0)
SEARCH = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "font"), os.path.join(ROOT, "tools", "analysis")]
DOCS = ["LICENSE", "THIRD_PARTY_NOTICES.md", "VERSION"]
FORBIDDEN = re.compile(r"(\.xbe|\.iso|\.xiso)$|(^|/)(roms|out|work)/", re.I)
ISSUE_LINK = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/issues/\d+")


class ReleaseError(Exception):
    pass


# ---- version and notes

def version():
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as f:
        v = f.read().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        raise ReleaseError(f"VERSION must be major.minor.patch, found '{v}'")
    return v


def check_tag(v, tag):
    if tag is not None and tag.removeprefix("v") != v:
        raise ReleaseError(f"VERSION {v} and tag {tag} disagree")


def section(text, heading):
    """Lines under a '### heading' up to the next heading."""
    m = re.search(rf"^###\s+{re.escape(heading)}\s*$(.*?)(?=^#{{1,3}}\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def check_notes(text):
    """Both resolved-issue sections exist and link at least one issue; returns the links."""
    links = []
    for heading in ("해결된 issue", "Resolved issues"):
        body = section(text, heading)
        if body is None:
            raise ReleaseError(f"release notes: no '### {heading}' section")
        found = ISSUE_LINK.findall(body)
        if not found:
            raise ReleaseError(f"release notes: '### {heading}' links no issue")
        links += found
    return sorted(set(links))


def notes_text(v):
    path = os.path.join(ROOT, "docs", "release-notes", f"v{v}.md")
    if not os.path.isfile(path):
        raise ReleaseError(f"no release notes {os.path.relpath(path, ROOT)}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    check_notes(text)
    return text


# ---- contents

def patcher_modules():
    """Repository files tools/patch.py imports; stops on any third-party module."""
    finder = modulefinder.ModuleFinder(path=SEARCH + sys.path)
    finder.run_script(os.path.join(ROOT, "tools", "patch.py"))
    # The standard library: anything under the base installation (Lib/, DLLs/,
    # lib/pythonX.Y/, lib-dynload/) outside site-packages.
    bases = {os.path.normcase(os.path.abspath(p)) + os.sep for p in (sys.base_prefix, sys.base_exec_prefix)}
    files, third = [os.path.join(ROOT, "tools", "patch.py")], []
    for name, mod in finder.modules.items():
        path = getattr(mod, "__file__", None)
        if not path:
            continue
        p = os.path.normcase(os.path.abspath(path))
        if p.startswith(os.path.normcase(ROOT) + os.sep):
            files.append(os.path.abspath(path))
        elif "site-packages" in p or "dist-packages" in p or not any(p.startswith(b) for b in bases):
            third.append(name)
    if third:
        raise ReleaseError("the patcher imports modules outside the standard library: " + ", ".join(sorted(third)))
    return sorted(set(files))


def data_files():
    rel = ["patch/manifest.json", "patch/xbe-en.tsv"]
    for sub, pattern in (("patch/text", r".*\.tsv$|README\.md$"), ("patch/xbe", r".*"), ("patch/font", r".*")):
        for n in sorted(os.listdir(os.path.join(ROOT, sub))):
            if re.fullmatch(pattern, n) and os.path.isfile(os.path.join(ROOT, sub, n)):
                rel.append(f"{sub}/{n}")
    return rel


def read(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return f.read()


def documents(v):
    with open(os.path.join(ROOT, "release", "README.md"), encoding="utf-8") as f:
        readme = f.read().replace("{version}", v)
    out = {"README.md": readme.encode("utf-8"), "RELEASE_NOTES.md": notes_text(v).encode("utf-8")}
    for d in DOCS:
        out[d] = read(d)
    return out


# ---- deterministic archives

def write_zip(path, entries):
    """entries: {name: (bytes, mode)}."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(entries):
            data, mode = entries[name]
            info = zipfile.ZipInfo(name, EPOCH)
            info.external_attr = (0o100000 | mode) << 16
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)


def write_targz(path, entries):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as t:
        for name in sorted(entries):
            data, mode = entries[name]
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), mode, 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            t.addfile(info, io.BytesIO(data))
    with open(path, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
        g.write(buf.getvalue())


def unpack(path, dest):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            for info in z.infolist():
                z.extract(info, dest)
                mode = (info.external_attr >> 16) & 0o777
                if mode:
                    os.chmod(os.path.join(dest, info.filename), mode)
    else:
        with tarfile.open(path) as t:
            names = t.getnames()
            t.extractall(dest, filter="data")
    return names


def check_names(names):
    bad = [n for n in names if FORBIDDEN.search(n)]
    if bad:
        raise ReleaseError("game data or output paths in the package: " + ", ".join(bad[:5]))


def check_usage(cmd, cwd, expect):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    if r.returncode != 1 or "usage:" not in out or expect not in out:
        raise ReleaseError(f"{' '.join(cmd)}: expected the usage text (exit 1, '{expect}'), got exit "
                           f"{r.returncode}:\n{out[-800:]}")


# ---- packages

def build_python(dest, v):
    top = f"{NAME}-v{v}-python"
    entries = {f"{top}/{n}": (d, 0o644) for n, d in documents(v).items()}
    for path in patcher_modules():
        entries[f"{top}/{os.path.relpath(path, ROOT).replace(os.sep, '/')}"] = (read(path), 0o644)
    for rel in data_files():
        entries[f"{top}/{rel}"] = (read(rel), 0o644)
    out = os.path.join(dest, f"{top}.zip")
    write_zip(out, entries)
    with tempfile.TemporaryDirectory() as tmp:
        check_names(unpack(out, tmp))
        check_usage([sys.executable, "-I", "tools/patch.py"], os.path.join(tmp, top), "tools/patch.py")
    return out


def platform_name():
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    raise ReleaseError(f"no executable build for {sys.platform}")


def runtime_licenses():
    """License texts of what the executable carries (design §8.2)."""
    out = {"licenses/DoHyeon-OFL.txt": read("patch/font/OFL.txt")}
    for cand in (os.path.join(sys.base_prefix, "LICENSE.txt"),
                 os.path.join(sysconfig.get_paths()["stdlib"], "LICENSE.txt")):
        if os.path.isfile(cand):
            with open(cand, "rb") as f:
                out["licenses/Python-LICENSE.txt"] = f.read()
            break
    else:
        raise ReleaseError("Python's LICENSE.txt not found")
    dist = importlib.metadata.distribution("nuitka")
    if dist.version != NUITKA:
        raise ReleaseError(f"Nuitka {dist.version} installed; {NUITKA} (Apache-2.0) is required "
                           "(pip install -r tools/release-requirements.txt)")
    wanted = {"LICENSE.txt": "licenses/Nuitka-LICENSE.txt", "LICENSE": "licenses/Nuitka-LICENSE.txt"}
    for f in dist.files or []:
        name = str(f).replace("\\", "/")
        base = name.rsplit("/", 1)[-1]
        if ".dist-info/" in name and base in wanted:
            out[wanted[base]] = f.read_binary() if hasattr(f, "read_binary") else open(dist.locate_file(f), "rb").read()
        elif name.endswith("inline_copy/zstd/LICENSE.txt"):
            out["licenses/zstd-LICENSE.txt"] = open(dist.locate_file(f), "rb").read()
    missing = {"licenses/Nuitka-LICENSE.txt", "licenses/zstd-LICENSE.txt"} - set(out)
    if missing:
        raise ReleaseError("license files not found in the Nuitka installation: " + ", ".join(sorted(missing)))
    return out


def nuitka_build(work, exe_name):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(SEARCH))
    cmd = [sys.executable, "-m", "nuitka", "--onefile", "--assume-yes-for-downloads",
           f"--output-dir={work}", f"--output-filename={exe_name}"]
    if sys.platform.startswith("win"):
        cmd.append("--msvc=latest")
    for rel in data_files():
        cmd.append(f"--include-data-files={os.path.join(ROOT, rel)}={rel}")
    cmd.append(os.path.join(ROOT, "tools", "patch.py"))
    print(" ".join(cmd[:6]) + " ...", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env=env)
    if r.returncode:
        raise ReleaseError(f"Nuitka failed (exit {r.returncode})")
    path = os.path.join(work, exe_name)
    if not os.path.isfile(path):
        raise ReleaseError(f"Nuitka made no {exe_name}")
    return path


def build_binary(dest, v, exe=None):
    osname = platform_name()
    exe_name = NAME + (".exe" if osname == "windows" else "")
    top = f"{NAME}-v{v}-{osname}-x64"
    licenses = runtime_licenses()
    with tempfile.TemporaryDirectory() as work:
        path = exe or nuitka_build(work, exe_name)
        with open(path, "rb") as f:
            binary = f.read()
    entries = {f"{top}/{n}": (d, 0o644) for n, d in documents(v).items()}
    entries.update({f"{top}/{n}": (d, 0o644) for n, d in licenses.items()})
    entries[f"{top}/{exe_name}"] = (binary, 0o755)
    out = os.path.join(dest, f"{top}.zip" if osname == "windows" else f"{top}.tar.gz")
    (write_zip if osname == "windows" else write_targz)(out, entries)
    with tempfile.TemporaryDirectory() as tmp:
        check_names(unpack(out, tmp))
        check_usage([os.path.join(tmp, top, exe_name)], os.path.join(tmp, top), NAME)
    return out


def build_sums(dest):
    names = sorted(n for n in os.listdir(dest) if n.startswith(NAME + "-v") and n.endswith((".zip", ".tar.gz")))
    if not names:
        raise ReleaseError(f"no packages in {dest}")
    lines = []
    for n in names:
        with open(os.path.join(dest, n), "rb") as f:
            lines.append(f"{hashlib.sha256(f.read()).hexdigest()}  {n}\n")
    out = os.path.join(dest, "SHA256SUMS.txt")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)
    return out


def main():
    args = sys.argv[1:]
    tag = exe = None
    if "--tag" in args:
        i = args.index("--tag")
        tag = args[i + 1]
        del args[i:i + 2]
    if "--exe" in args:                  # package an executable built elsewhere
        i = args.index("--exe")
        exe = args[i + 1]
        del args[i:i + 2]
    if not args or args[0] not in ("notes", "python", "binary", "sums") or len(args) != (1 if args[0] == "notes" else 2):
        raise SystemExit(__doc__)
    try:
        v = version()
        check_tag(v, tag)
        if args[0] == "notes":
            links = check_notes(notes_text(v))
            print(f"v{v}: release notes list {len(links)} resolved issue(s): {', '.join(links)}")
            return
        dest = os.path.abspath(args[1])
        os.makedirs(dest, exist_ok=True)
        if args[0] == "python":
            out = build_python(dest, v)
        elif args[0] == "binary":
            out = build_binary(dest, v, exe)
        else:
            out = build_sums(dest)
    except ReleaseError as err:
        raise SystemExit(f"release: {err}")
    with open(out, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"wrote {out} ({os.path.getsize(out)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
