"""Reinsert text whose length may change (design 20261021-i013 §2).

  file and place                             fits (<= orig_len)        longer
  Media/Event/Event/e*.dat  norm:2/0+...     page replaced, message script rebuilt (no padding)
  Media/Event/TalkEvent/TE*.bin  off:...     page replaced, message script rebuilt (no padding)
  Media/Mission/mssn*.bin  off:... (slot 0)  in place, NUL fill        appended at the end of the
                                                                       file, slot 0 repointed
  default.xbe  va:... (an xbetext string)    in place, NUL fill        moved to a new section
                                                                       KRTEXT, every .data slot
                                                                       and push immediate repointed
  anything else                              in place (row.pad)        refused

A change is a row and the new game bytes, so the original bytes can be put
back unencoded (round trip). Page and branch codes must match the original
(page counts never change) and pages must fit the page buffer; both are
errors, collected over all rows. Line width and line count are warnings.
"""
import fnmatch
import struct
from collections import namedtuple

from . import container, mission, msgscript, screen, textpatch, xbeedit, xbetext
from .digest import sha1

EVENT = "Media/Event/Event/e*.dat"
EVENT_ITEM = (2, 0)
TALK = "Media/Event/TalkEvent/TE*.bin"
MISSION = "Media/Mission/mssn*.bin"
XBE = "default.xbe"
SECTION = "KRTEXT"

Change = namedtuple("Change", "row data")             # data: new game bytes
Done = namedtuple("Done", "row size how")             # how: page, in place, appended, moved
Result = namedtuple("Result", "sections done warnings")


def group_of(row):
    """'event', 'talk', 'mission', 'xbe' or None (in place only)."""
    if row.kind == "norm" and row.path == EVENT_ITEM and fnmatch.fnmatchcase(row.file, EVENT):
        return "event"
    if row.kind == "off" and fnmatch.fnmatchcase(row.file, TALK):
        return "talk"
    if row.kind == "off" and fnmatch.fnmatchcase(row.file, MISSION):
        return "mission"
    if row.kind == "va" and row.file == XBE:
        return "xbe"
    return None


class _Run:
    def __init__(self, single):
        self.single, self.errors, self.warnings, self.done = single, [], [], []

    def label(self, row):
        return f"{row.source} {row.file} {textpatch.format_where(row)}"

    def screen(self, row, original, new):
        group = group_of(row)
        for issue in screen.check(group, original, new, self.single):
            text = f"{self.label(row)}: {issue.message}"
            (self.errors if issue.level == "error" else self.warnings).append(text)


def _script(run, data, changes):
    """Replace whole pages of a message script; returns the rebuilt bytes."""
    script = msgscript.parse(data)
    index = {p.offset: (l, m, i) for l, lang in enumerate(script.pages)
             for m, msg in enumerate(lang) for i, p in enumerate(msg)}
    for ch in changes:
        row = ch.row
        if row.offset not in index:
            raise textpatch.PatchError(f"{run.label(row)}: not the start of a page")
        l, m, i = index[row.offset]
        page = script.pages[l][m][i]
        if len(page.data) != row.orig_len or sha1(page.data) != row.orig_sha1:
            raise textpatch.PatchError(f"{run.label(row)}: original bytes do not match orig_sha1 "
                                       f"(the page is {len(page.data)} bytes)")
        run.screen(row, page.data, ch.data)
        script.pages[l][m][i] = page._replace(data=bytes(ch.data))
        run.done.append(Done(row, len(ch.data), "page"))
    return msgscript.build(script)


def _container(run, data, changes):
    tree = container.parse(data)
    pages = [c for c in changes if group_of(c.row) == "event"]
    if pages:
        tree.set(EVENT_ITEM, _script(run, tree.get(EVENT_ITEM), pages))
    for ch in changes:
        if group_of(ch.row) == "event":
            continue
        item, off, end = textpatch.locate(ch.row, data, tree=tree)
        item = bytearray(item)
        run.done.append(Done(ch.row, textpatch.put(item, off, ch.row, ch.data, end), "in place"))
        tree.set(ch.row.path, item)
    return container.build(tree)


def _mission(run, data, changes, always_move):
    slot0 = {}
    for c in mission.text_commands(data):
        at, ptr = c.pointers[0]
        slot0.setdefault(ptr, []).append(at)
    for ch in changes:
        row = ch.row
        textpatch.check_original(row, data)
        original = bytes(data[row.offset:row.offset + row.orig_len])
        if row.offset in slot0:
            run.screen(row, original, ch.data)
        if len(ch.data) <= row.orig_len and not always_move:
            run.done.append(Done(row, textpatch.put(data, row.offset, row, ch.data), "in place"))
            continue
        if row.offset not in slot0:
            raise textpatch.PatchError(f"{run.label(row)}: longer than the original, and not the "
                                       "language-0 string of a text command")
        if data[-1] != 0:
            data += b"\0"
        pos = len(data)
        data += bytes(ch.data) + b"\0"
        for at in slot0[row.offset]:
            struct.pack_into("<I", data, at, pos)
        run.done.append(Done(row, len(ch.data), "appended"))


def _xbe(run, image, changes, x, always_move):
    """In-place strings, then the moved ones into a new section. Returns section names touched."""
    touched, moves, strings = set(), [], None
    for ch in changes:
        row = ch.row
        off = x.offset(row.offset)
        if off is None:
            raise textpatch.PatchError(f"{run.label(row)}: VA {row.offset:#x} has no file data")
        textpatch.check_original(row, image, x)
        original = bytes(image[off:off + row.orig_len])
        if strings is None:
            strings = {s.va: s for s in xbetext.strings(x)}
        s = strings.get(row.offset)
        if s is not None:
            run.screen(row, original, ch.data)
        if len(ch.data) <= row.orig_len and not always_move:
            run.done.append(Done(row, textpatch.put(image, off, row, ch.data), "in place"))
            touched.add(x.section_at(row.offset).name)
            continue
        if s is None:
            raise textpatch.PatchError(f"{run.label(row)}: longer than the original, and not a "
                                       "Japanese .rdata string with known references")
        moves.append((ch, s))
    if not moves:
        return touched
    blob, placed = bytearray(), []
    for ch, s in moves:
        blob += bytes((-len(blob)) % 4)
        placed.append((ch, s, len(blob)))
        blob += bytes(ch.data) + b"\0"
    new_image, va = xbeedit.add_section(image, SECTION, bytes(blob))
    for ch, s, pos in placed:
        for ref in s.data_refs + s.code_refs:
            o = x.offset(ref)
            if struct.unpack_from("<I", new_image, o)[0] != s.va:
                raise textpatch.PatchError(f"{run.label(ch.row)}: the reference at {ref:#x} no longer "
                                           f"holds {s.va:#x}")
            struct.pack_into("<I", new_image, o, va + pos)
        touched |= {x.section_at(ref).name for ref in s.data_refs + s.code_refs}
        run.done.append(Done(ch.row, len(ch.data), "moved"))
    image[:] = new_image
    return touched | {SECTION}


def apply(changes, files, load, x=None, single=None, always_move=False):
    """Apply changes to `files` (name -> bytearray, filled from `load(name)` on
    first use). x: jsrfkr.xbe.Xbe of the original default.xbe (va: places).
    single: screen.single_widths(...) for width checks ({} = default widths).
    always_move: append or move mission and XBE strings even when they fit
    (round-trip test). Returns Result(XBE sections touched, [Done], [warning])."""
    run = _Run(single or {})
    by_file = {}
    for ch in changes:
        by_file.setdefault(ch.row.file, []).append(ch)
    mixed = sorted(f for f, cs in by_file.items() if len({c.row.kind == "norm" for c in cs}) > 1)
    if mixed:
        raise textpatch.PatchError("norm: and off:/va: places in the same file: " + ", ".join(mixed))
    sections = set()
    for name in sorted(by_file):
        cs = sorted(by_file[name], key=lambda c: (c.row.path or (), c.row.offset))
        if name not in files:
            files[name] = bytearray(load(name))
        data = files[name]
        kinds = {group_of(c.row) for c in cs}
        if cs[0].row.kind == "norm":
            if not container.is_container(data):
                raise textpatch.PatchError(f"{cs[0].row.source}: {name} is not a MULT/NORM container")
            data[:] = _container(run, bytes(data), cs)
        elif kinds == {"talk"}:
            data[:] = _script(run, bytes(data), cs)
        elif kinds == {"mission"}:
            _mission(run, data, cs, always_move)
        elif kinds == {"xbe"}:
            if x is None:
                raise textpatch.PatchError(f"{cs[0].row.source}: va: places need the XBE")
            sections |= _xbe(run, data, cs, x, always_move)
        else:
            for ch in cs:
                buf, off, end = textpatch.locate(ch.row, data, x)
                run.done.append(Done(ch.row, textpatch.put(buf, off, ch.row, ch.data, end), "in place"))
                if ch.row.kind == "va":
                    sections.add(x.section_at(ch.row.offset).name)
    if run.errors:
        raise textpatch.PatchError("\n".join(run.errors))
    return Result(sections, run.done, run.warnings)
