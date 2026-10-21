"""Text units of the dump: every on-screen Japanese string with its place (design 20261021-i011 §3).

  group    unit                                    where              pad
  event    a language-0 page of e###.dat item 2/0  norm:2/0+0x...     space
  talk     a language-0 page of TE###.bin          off:0x...          space
  mission  the language-0 string of a text command off:0x...          nul
  xbe      a Japanese .rdata string                va:0x...           nul

Pages that steer (branch, choice) or hold no letters, and empty or
letterless mission strings are left out. Every unit is a valid
patch/text/*.tsv place; check() reads each back through textpatch.
"""
import glob
import os
from collections import namedtuple

from . import container, mission, msgscript, textpatch, xbetext
from .digest import sha1

GROUPS = ("event", "talk", "mission", "xbe")
EVENT_GLOB = "Media/Event/Event/e*.dat"
TALK_GLOB = "Media/Event/TalkEvent/TE*.bin"
MISSION_GLOB = "Media/Mission/mssn*.bin"
XBE = "default.xbe"
EVENT_ITEM = (2, 0)
MISSION_KIND = {0xEF: "objective", 0xBF: "message", 0xC0: "message"}

# japanese/english: original bytes (english may be None); ref: structural position
Unit = namedtuple("Unit", "group file where orig_len orig_sha1 pad kind ref japanese english")


class Census:
    """Counts per group for the report."""

    def __init__(self):
        self.files = dict.fromkeys(GROUPS, 0)       # files holding units
        self.records = dict.fromkeys(GROUPS, 0)     # scripts / text commands / strings
        self.skipped = dict.fromkeys(GROUPS, 0)     # pages or strings left out
        self.notes = {}


def _rel(game, path):
    return os.path.relpath(path, game).replace("\\", "/")


def _parts(block):
    """Part number of each page of a language block: '$e' pages counted before it."""
    out, part = [], 0
    for p in block:
        out.append(part)
        if p.data == b"$e":
            part += 1
    return out


def _english(script, part):
    """The shown English pages of a part (language 1), joined with '$r'."""
    if script.languages < 2:
        return None
    block = script.block(1)
    pages = [p.data for p, k in zip(block, _parts(block))
             if k == part and not msgscript.is_control(p.data) and msgscript.has_letters(p.data)]
    return b"$r".join(pages) if pages else None


def _script_units(group, name, script, where, census):
    block = script.block(0)
    for i, (page, part) in enumerate(zip(block, _parts(block))):
        if msgscript.is_control(page.data) or not msgscript.has_letters(page.data):
            census.skipped[group] += 1
            continue
        yield Unit(group, name, where(page.offset), len(page.data), sha1(page.data), "space", "page",
                   f"part {part} page {i}", page.data, _english(script, part))


def event_units(game, census):
    for path in sorted(glob.glob(os.path.join(game, EVENT_GLOB))):
        name = _rel(game, path)
        with open(path, "rb") as f:
            tree = container.parse(f.read())
        try:
            item = tree.get(EVENT_ITEM)
        except KeyError:
            continue
        if isinstance(item, container.Block) or b"$e" not in item:
            census.notes["event_other"] = census.notes.get("event_other", 0) + 1
            continue
        script = msgscript.parse(item)
        if msgscript.build(script) != item:
            raise msgscript.FormatError(f"{name}: message script does not round-trip")
        census.records["event"] += 1
        units = list(_script_units("event", name, script,
                                   lambda off: f"norm:{container.format_path(EVENT_ITEM)}+{off:#x}", census))
        census.files["event"] += bool(units)
        yield from units


def talk_units(game, census):
    for path in sorted(glob.glob(os.path.join(game, TALK_GLOB))):
        name = _rel(game, path)
        with open(path, "rb") as f:
            data = f.read()
        try:
            script = msgscript.parse(data)
        except msgscript.FormatError as err:
            raise msgscript.FormatError(f"{name}: {err}") from None
        if msgscript.build(script) != data:
            raise msgscript.FormatError(f"{name}: message script does not round-trip")
        census.records["talk"] += 1
        units = list(_script_units("talk", name, script, lambda off: f"off:{off:#x}", census))
        census.files["talk"] += bool(units)
        yield from units


def mission_units(game, census):
    for path in sorted(glob.glob(os.path.join(game, MISSION_GLOB))):
        name = _rel(game, path)
        with open(path, "rb") as f:
            data = f.read()
        try:
            commands = mission.text_commands(data)
        except mission.FormatError as err:
            raise mission.FormatError(f"{name}: {err}") from None
        n = 0
        for c in commands:
            census.records["mission"] += 1
            ptr = c.pointers[0][1]
            s = mission.string_at(data, ptr) if ptr else b""
            if b"$e" in s:
                census.notes["mission_e0"] = census.notes.get("mission_e0", 0) + 1
            if not msgscript.has_letters(s):
                census.skipped["mission"] += 1
                continue
            en = c.pointers[1][1]
            n += 1
            yield Unit("mission", name, f"off:{ptr:#x}", len(s), sha1(s), "nul",
                       MISSION_KIND.get(c.op, "text"), f"sec {c.section:#x} rec {c.index} op {c.op:#x}",
                       s, mission.string_at(data, en) if en else None)
        census.files["mission"] += bool(n)


def xbe_units(game, x, census):
    found = xbetext.strings(x)
    census.records["xbe"] = len(found)
    census.files["xbe"] = 1 if found else 0
    census.notes["xbe"] = (sum(len(s.data_refs) for s in found), sum(len(s.code_refs) for s in found),
                           sum(len(s.stray) for s in found), sum(1 for s in found if not (s.data_refs or s.code_refs)))
    for s in found:
        yield Unit("xbe", XBE, f"va:{s.va:#x}", len(s.data), sha1(s.data), "nul", "string",
                   f"refs {len(s.data_refs)} data + {len(s.code_refs)} code", s.data, None)


def units(game, x):
    """(units by group, Census). x: jsrfkr.xbe.Xbe of the dump's default.xbe."""
    census = Census()
    out = {
        "event": list(event_units(game, census)),
        "talk": list(talk_units(game, census)),
        "mission": list(mission_units(game, census)),
        "xbe": list(xbe_units(game, x, census)),
    }
    return out, census


def as_row(u, source="extract"):
    kind, path, value = textpatch.parse_where(u.where)
    return textpatch.Row(source, 0, u.file, kind, path, value, u.orig_len, u.orig_sha1, "", u.pad)


def check(game, x, by_group):
    """Read every unit back through textpatch's place resolution; returns the count."""
    n, cache = 0, {}
    for group in GROUPS:
        for u in by_group[group]:
            if u.file not in cache:
                with open(os.path.join(game, u.file), "rb") as f:
                    data = f.read()
                tree = container.parse(data) if container.is_container(data) else None
                cache = {u.file: (data, tree)}
            data, tree = cache[u.file]
            textpatch.check_original(as_row(u), data, x, tree)
            n += 1
    return n
