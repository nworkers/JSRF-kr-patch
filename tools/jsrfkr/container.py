"""MULT/NORM containers: parse into a tree, rebuild from the tree (analysis containers.md §1).

  header (16 bytes): magic ('MULT' or 'NORM'), u32 count, u32 0, u32 0
  link (16 bytes, relative to the container's header): u32 start, end, size, flag
    The first link follows the header; item i is [start, end) and starts right
    after its link; the next link sits at end.
  MULT items are blocks (size = end - start, flag 0).
  NORM items are data of `size` bytes, zero-padded to a 16-byte boundary
  (relative to the container); flag is 1 for an empty item, else 0.

build() computes every link, padding byte and flag, so a tree holds no
original bytes beyond the item data. Item paths are tuples of item indexes
from the top-level block, e.g. (2, 0) = item 0 of item 2; a path to data ends
at a NORM item.
"""
import struct

HEADER = 0x10
LINK = 0x10
MAGICS = (b"MULT", b"NORM")


class FormatError(ValueError):
    pass


class Block:
    """A MULT (items are Blocks) or NORM (items are bytes)."""

    def __init__(self, magic, items):
        if magic not in MAGICS:
            raise ValueError(f"unknown container magic {magic!r}")
        self.magic, self.items = magic, list(items)

    def __eq__(self, other):
        return isinstance(other, Block) and (self.magic, self.items) == (other.magic, other.items)

    def __repr__(self):
        return f"Block({self.magic!r}, {len(self.items)} items)"

    def get(self, path):
        """The item at a path (a Block or bytes)."""
        node = self
        for i in path:
            if not isinstance(node, Block):
                raise KeyError(f"path {format_path(path)}: passes through data")
            if not 0 <= i < len(node.items):
                raise KeyError(f"path {format_path(path)}: no item {i} in a {node.magic.decode()} "
                               f"of {len(node.items)}")
            node = node.items[i]
        return node

    def set(self, path, data):
        """Replace the NORM data item at a path."""
        if not path:
            raise KeyError("an empty path names the top-level block, not data")
        parent = self.get(path[:-1])
        if not isinstance(parent, Block) or parent.magic != b"NORM":
            raise KeyError(f"path {format_path(path)}: not a NORM data item")
        parent.get((path[-1],))
        parent.items[path[-1]] = bytes(data)


def is_container(data):
    return bytes(data[:4]) in MAGICS


def parse(data):
    """Parse a whole file; raises FormatError when it does not follow the format exactly."""
    data = bytes(data)
    block, end = _parse(data, 0, len(data))
    if end != len(data):
        raise FormatError(f"{len(data) - end} bytes after the top-level block")
    return block


def _parse(data, base, limit):
    if limit - base < HEADER:
        raise FormatError(f"block at {base:#x}: shorter than a header")
    magic, count, z1, z2 = struct.unpack_from("<4sIII", data, base)
    if magic not in MAGICS:
        raise FormatError(f"block at {base:#x}: magic {magic!r}")
    if z1 or z2:
        raise FormatError(f"block at {base:#x}: non-zero header fields")
    link = base + HEADER
    items = []
    for i in range(count):
        if link + LINK > limit:
            raise FormatError(f"block at {base:#x}: link {i} past the end")
        start, end, size, flag = struct.unpack_from("<4I", data, link)
        if base + start != link + LINK or end < start or base + end > limit:
            raise FormatError(f"block at {base:#x}: link {i} ({start:#x}, {end:#x}) out of place")
        if magic == b"MULT":
            if size != end - start or flag:
                raise FormatError(f"block at {base:#x}: MULT link {i} size or flag")
            child, child_end = _parse(data, base + start, base + end)
            if child_end != base + end:
                raise FormatError(f"block at {base + start:#x}: ends before its link's end")
            items.append(child)
        else:
            item = data[base + start:base + start + size]
            if size > end - start or _padded(start, size) != end:
                raise FormatError(f"block at {base:#x}: NORM link {i} size {size:#x} in [{start:#x}, {end:#x})")
            if flag != (1 if size == 0 else 0):
                raise FormatError(f"block at {base:#x}: NORM link {i} flag {flag}")
            if any(data[base + start + size:base + end]):
                raise FormatError(f"block at {base:#x}: NORM item {i} has non-zero padding")
            items.append(item)
        link = base + end
    return Block(magic, items), link


def _padded(start, size):
    end = start + size
    return end + (-end) % 16


def build(block):
    """The bytes of a block; links, padding and flags are computed."""
    out = bytearray(struct.pack("<4sIII", block.magic, len(block.items), 0, 0))
    for item in block.items:
        start = len(out) + LINK
        if block.magic == b"MULT":
            if not isinstance(item, Block):
                raise TypeError("MULT items must be blocks")
            body = build(item)
            size, flag, end = len(body), 0, start + len(body)
        else:
            if isinstance(item, Block):
                raise TypeError("NORM items must be bytes")
            body = bytes(item)
            size, flag, end = len(body), (1 if not body else 0), _padded(start, len(body))
            body += bytes(end - start - size)
        out += struct.pack("<4I", start, end, size, flag)
        out += body
    return bytes(out)


def parse_path(text):
    """'2/0' -> (2, 0)."""
    try:
        path = tuple(int(p) for p in text.split("/"))
    except ValueError:
        raise ValueError(f"bad item path '{text}'") from None
    if not path or any(i < 0 for i in path):
        raise ValueError(f"bad item path '{text}'")
    return path


def format_path(path):
    return "/".join(str(i) for i in path)


def walk(block, path=()):
    """Yield (path, data) for every NORM data item, in file order."""
    for i, item in enumerate(block.items):
        if isinstance(item, Block):
            yield from walk(item, path + (i,))
        else:
            yield path + (i,), item
