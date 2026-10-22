"""Make the English places read the Korean (design 20261023-i020 §4, §9).

Runs after jsrfkr.reinsert has written the Korean into the Japanese places:

  event / talk   the language-1 block of each translated message script becomes
                 a copy of the (Korean) language-0 block: fields 0-4, per-page
                 values and pages (branch arguments count pages in the block)
  mission        slot 1 of each text command whose slot 0 points to a Korean
                 string is pointed at that same string
  XBE            each English slot of patch/xbe-en.tsv whose Japanese slot's
                 string was translated takes that Japanese slot's (patched) value

The original English bytes stay in the files; nothing points to them any more.
"""
import fnmatch
import struct
from collections import namedtuple

from . import container, mission, msgscript, reinsert

Pair = namedtuple("Pair", "jp_slot en_slot jp_value en_value rule")
Result = namedtuple("Result", "scripts commands slots sections")


class EnglishError(Exception):
    pass


def read_map(path):
    pairs = []
    header = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.rstrip("\r\n")
            if not raw or raw.startswith("#"):
                continue
            cols = raw.split("\t")
            if header is None:
                header = cols
                continue
            d = dict(zip(header, cols))
            pairs.append(Pair(int(d["jp_slot"], 16), int(d["en_slot"], 16), int(d["jp_value"], 16),
                              int(d["en_value"], 16), d["rule"]))
    return pairs


def copy_language0(data):
    """A message script whose language 1 is a copy of language 0."""
    s = msgscript.parse(data)
    if s.languages < 2:
        raise EnglishError(f"{s.languages} language(s), no English block")
    M = s.messages
    for f in s.fields:
        f[1] = list(f[0])
    for m in range(M):
        s.values[M + m] = list(s.values[m])
    s.pages[1] = [list(msg) for msg in s.pages[0]]
    return msgscript.build(s)


def _script_file(name, data):
    if fnmatch.fnmatchcase(name, reinsert.EVENT):
        tree = container.parse(data)
        tree.set(reinsert.EVENT_ITEM, copy_language0(tree.get(reinsert.EVENT_ITEM)))
        return container.build(tree)
    return copy_language0(data)


def _mission_file(data, is_korean):
    """Point slot 1 at slot 0's string for commands whose slot 0 is Korean; returns the count."""
    n = 0
    for c in mission.text_commands(data):
        p0 = c.pointers[0][1]
        at1, p1 = c.pointers[1]
        if is_korean(p0) and p1 != p0:
            struct.pack_into("<I", data, at1, p0)
            n += 1
    return n


def apply(rows, files, original_size, x, pairs):
    """Apply to `files` (name -> bytearray, already patched by reinsert).

    rows: the translated text rows; original_size(name): the dump file's size;
    x: jsrfkr.xbe.Xbe of the original default.xbe; pairs: read_map(...)."""
    by_file = {}
    for r in rows:
        by_file.setdefault(r.file, []).append(r)
    scripts = commands = slots = 0
    sections = set()
    for name in sorted(by_file):
        group = reinsert.group_of(by_file[name][0])
        data = files[name]
        if group in ("event", "talk"):
            data[:] = _script_file(name, bytes(data))
            scripts += 1
        elif group == "mission":
            # Korean: replaced in place at a row's offset, or appended past the original end
            offsets, size = {r.offset for r in by_file[name]}, original_size(name)
            commands += _mission_file(data, lambda p: p in offsets or p >= size)
    xbe_rows = [r for r in by_file.get(reinsert.XBE, []) if reinsert.group_of(r) == "xbe"]
    if xbe_rows:
        image = files[reinsert.XBE]
        translated = {r.offset for r in xbe_rows}

        def slot(a):
            o = x.offset(a)
            if o is None:
                raise EnglishError(f"slot {a:#x} has no file data")
            return o

        for p in pairs:
            if x.u32(p.jp_slot) != p.jp_value or x.u32(p.en_slot) != p.en_value:
                raise EnglishError(f"xbe-en map: slots {p.jp_slot:#x}/{p.en_slot:#x} do not hold "
                                   f"{p.jp_value:#x}/{p.en_value:#x} in this default.xbe")
            if p.jp_value not in translated:
                continue
            value = struct.unpack_from("<I", image, slot(p.jp_slot))[0]
            struct.pack_into("<I", image, slot(p.en_slot), value)
            sections.add(x.section_at(p.en_slot).name)
            slots += 1
    return Result(scripts, commands, slots, sections)
