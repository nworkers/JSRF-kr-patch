"""Text patches: patch/text/*.tsv, in-place replacement (design 20261021-i002 §3.1).

Columns: file, where, orig_len, orig_sha1, korean, pad
  where  off:0x...               file offset
         va:0x...                virtual address in default.xbe
         norm:<item path>+0x...  offset inside a MULT/NORM data item, e.g. norm:2/0+0x1c
  pad    nul (default; a whole string, so a NUL must follow it)
         space (a message inside a longer string; the rest becomes 0x20)
Lines starting with '#' are comments. No original text is stored: a place is
replaced only when its bytes match orig_sha1.
"""
import glob
import os
from collections import namedtuple

from . import container
from .digest import sha1

XBE = "default.xbe"
COLUMNS = ("file", "where", "orig_len", "orig_sha1", "korean")
PADS = ("nul", "space")

Row = namedtuple("Row", "source line file kind path offset orig_len orig_sha1 korean pad")


class PatchError(Exception):
    pass


def parse_where(text):
    """-> (kind, item path or None, value)."""
    kind, sep, value = text.partition(":")
    if not sep:
        raise ValueError(f"bad place '{text}'")
    if kind in ("off", "va"):
        return kind, None, int(value, 16)
    if kind == "norm":
        path, plus, off = value.partition("+")
        if not plus:
            raise ValueError(f"bad place '{text}' (norm:<path>+0x<offset>)")
        return kind, container.parse_path(path), int(off, 16)
    raise ValueError(f"bad place '{text}'")


def format_where(row):
    if row.kind == "norm":
        return f"norm:{container.format_path(row.path)}+{row.offset:#x}"
    return f"{row.kind}:{row.offset:#x}"


def text_files(path):
    """A .tsv file, or every .tsv in a folder in file-name order."""
    if os.path.isdir(path):
        return sorted(glob.glob(os.path.join(path, "*.tsv")))
    return [path]


def read_rows(paths):
    rows, seen = [], {}
    for path in paths:
        header = None
        with open(path, encoding="utf-8") as f:
            for n, raw in enumerate(f, 1):
                raw = raw.rstrip("\r\n")
                if not raw or raw.startswith("#"):
                    continue
                cols = raw.split("\t")
                where = f"{os.path.basename(path)}:{n}"
                if header is None:
                    header = cols
                    missing = [c for c in COLUMNS if c not in header]
                    if missing:
                        raise PatchError(f"{where}: missing columns {', '.join(missing)}")
                    continue
                if len(cols) > len(header):
                    raise PatchError(f"{where}: {len(cols)} columns, header has {len(header)}")
                d = dict(zip(header, cols))
                try:
                    kind, item, value = parse_where(d["where"])
                    orig_len = int(d["orig_len"])
                except (KeyError, ValueError) as err:
                    raise PatchError(f"{where}: {err}") from None
                pad = d.get("pad") or "nul"
                if pad not in PADS:
                    raise PatchError(f"{where}: unknown pad '{pad}'")
                if kind == "va" and d["file"] != XBE:
                    raise PatchError(f"{where}: va: places are for {XBE} only")
                row = Row(where, n, d["file"], kind, item, value, orig_len, d["orig_sha1"].lower(),
                          d["korean"], pad)
                key = (row.file, format_where(row))
                if key in seen:
                    raise PatchError(f"{where}: {key[0]} {key[1]} is also at {seen[key]}")
                seen[key] = where
                rows.append(row)
    return rows


def replace_at(buf, off, row, encoder, end_terminates=False):
    """Replace row's original string at buf[off:] in place.

    end_terminates: the end of buf also ends a string (a NORM item's data
    length excludes its terminator; analysis containers.md §3)."""
    n = row.orig_len
    label = f"{row.source} {row.file} {format_where(row)}"
    if off < 0 or off + n > len(buf):
        raise PatchError(f"{label}: outside the data ({len(buf)} bytes)")
    if sha1(bytes(buf[off:off + n])) != row.orig_sha1:
        raise PatchError(f"{label}: original bytes do not match orig_sha1")
    at_end = end_terminates and off + n == len(buf)
    if row.pad == "nul" and not at_end and (off + n >= len(buf) or buf[off + n] != 0):
        raise PatchError(f"{label}: no NUL after the string (use pad=space)")
    try:
        enc = encoder.encode(row.korean)
    except ValueError as err:
        raise PatchError(f"{label}: {err}") from None
    if len(enc) > n:
        raise PatchError(f"{label}: Korean is {len(enc)} bytes, more than {n}")
    buf[off:off + n] = enc + (b"\0" if row.pad == "nul" else b" ") * (n - len(enc))
    return len(enc)


def apply(rows, files, load, encoder, xbe=None):
    """Apply rows to `files` (name -> bytearray, filled from `load(name)` on first use).

    `xbe` (jsrfkr.xbe.Xbe of the original) resolves va: places. Returns the XBE
    section names touched and a list of (row, encoded length)."""
    sections, done = set(), []
    trees = {}
    kinds = {}
    for row in rows:
        kinds.setdefault(row.file, set()).add(row.kind == "norm")
    mixed = sorted(name for name, k in kinds.items() if len(k) > 1)
    if mixed:
        raise PatchError("norm: and off:/va: places in the same file: " + ", ".join(mixed))
    for row in rows:
        if row.file not in files:
            files[row.file] = bytearray(load(row.file))
        data = files[row.file]
        if row.kind == "va":
            off = xbe.offset(row.offset)
            if off is None:
                raise PatchError(f"{row.source}: VA {row.offset:#x} has no file data")
            sections.add(xbe.section_at(row.offset).name)
            done.append((row, replace_at(data, off, row, encoder)))
        elif row.kind == "off":
            done.append((row, replace_at(data, row.offset, row, encoder)))
        else:
            if row.file not in trees:
                if not container.is_container(data):
                    raise PatchError(f"{row.source}: {row.file} is not a MULT/NORM container")
                trees[row.file] = container.parse(data)
            tree = trees[row.file]
            try:
                item = tree.get(row.path)
            except KeyError as err:
                raise PatchError(f"{row.source}: {err}") from None
            if isinstance(item, container.Block):
                raise PatchError(f"{row.source}: {container.format_path(row.path)} is a block, not data")
            item = bytearray(item)
            done.append((row, replace_at(item, row.offset, row, encoder, end_terminates=True)))
            tree.set(row.path, item)
    for name, tree in trees.items():
        files[name][:] = container.build(tree)
    return sections, done
