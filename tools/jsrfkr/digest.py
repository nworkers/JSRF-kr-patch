"""Hashes and the patch manifest (design 20261021-i002 §3.2).

patch/manifest.json:
  {"format": 1,
   "target": {"file": "default.xbe", "md5": "<Japanese default.xbe>"},
   "inputs": {"<path in the dump>": "<md5>", ...}}
"""
import hashlib
import json
import os

FORMAT = 1


def md5(b):
    return hashlib.md5(b).hexdigest()


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


class ManifestError(Exception):
    pass


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("format") != FORMAT:
        raise ManifestError(f"{path}: format {m.get('format')!r}, expected {FORMAT}")
    if "target" not in m or "inputs" not in m:
        raise ManifestError(f"{path}: needs 'target' and 'inputs'")
    return m


def write_manifest(path, manifest):
    """Write with sorted inputs so the same content gives the same file."""
    m = dict(manifest, inputs=dict(sorted(manifest["inputs"].items())))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")


def check_inputs(manifest, game, needed):
    """Check the target and every input against the dump; `needed` must all be listed.

    Returns nothing; raises ManifestError naming every problem at once."""
    problems = []
    missing = sorted(set(needed) - set(manifest["inputs"]))
    if missing:
        problems.append("not in the manifest (run --update-manifest): " + ", ".join(missing))
    target = manifest["target"]
    items = [(target["file"], target["md5"])] + sorted(manifest["inputs"].items())
    for name, want in items:
        path = os.path.join(game, name)
        if not os.path.isfile(path):
            problems.append(f"{name}: not in the dump")
        elif md5_file(path) != want:
            problems.append(f"{name}: MD5 {md5_file(path)} is not {want}")
    if problems:
        raise ManifestError("\n".join(dict.fromkeys(problems)))
