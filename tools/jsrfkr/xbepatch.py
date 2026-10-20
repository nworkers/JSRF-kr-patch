"""XBE byte patches: patch/xbe/*.json (design 20261021-i002 §3.3).

  {"reason": "why", "patches": [{"va": "0x...", "orig_sha1": "...", "bytes": "<hex>"}]}

Only bytes we wrote are stored; the original bytes are checked by SHA-1.
"""
import glob
import json
import os

from .digest import sha1


class XbePatchError(Exception):
    pass


def load(folder):
    """Every patch in folder/*.json, in file-name order: (source, va, orig_sha1, bytes)."""
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if not doc.get("reason"):
            raise XbePatchError(f"{name}: needs a 'reason'")
        for i, p in enumerate(doc.get("patches", [])):
            try:
                va, want, data = int(p["va"], 16), p["orig_sha1"].lower(), bytes.fromhex(p["bytes"])
            except (KeyError, ValueError) as err:
                raise XbePatchError(f"{name} patch {i}: {err}") from None
            if not data:
                raise XbePatchError(f"{name} patch {i}: no bytes")
            out.append((f"{name} patch {i}", va, want, data))
    return out


def apply(patches, x, image):
    """Write the patches into image (a bytearray of x); returns the section names touched."""
    sections, taken = set(), []
    for source, va, want, data in patches:
        for other, lo, hi in taken:
            if va < hi and lo < va + len(data):
                raise XbePatchError(f"{source}: overlaps {other}")
        taken.append((source, va, va + len(data)))
        off = x.offset(va)
        if off is None or x.offset(va + len(data) - 1) != off + len(data) - 1:
            raise XbePatchError(f"{source}: VA {va:#x}+{len(data)} is not file data in one section")
        if sha1(x.data[off:off + len(data)]) != want:
            raise XbePatchError(f"{source}: original bytes at {va:#x} do not match orig_sha1")
        image[off:off + len(data)] = data
        sections.add(x.section_at(va).name)
    return sections
