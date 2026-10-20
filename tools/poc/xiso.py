"""Read an Xbox disc image (XDVDFS) and overwrite files in place at the same size.

XDVDFS: 2048-byte sectors. The volume descriptor is at sector 32 of the game
partition: "MICROSOFT*XBOX*MEDIA", u32 root directory sector, u32 root
directory size. A directory is a binary tree of entries: u16 left and u16
right child offsets (in 4-byte units, 0 = none), u32 start sector, u32 size,
u8 attributes (0x10 = directory), u8 name length, name; entries are padded
to 4 bytes and 0xFF fills the rest of a sector.

A plain xiso has the game partition at offset 0; a full disc image (redump)
has it at 0x18300000.

usage: python -I tools/poc/xiso.py <image.iso> [path]   (list the root, or show one file)
"""
import hashlib
import struct
import sys

SECTOR = 2048
MAGIC = b"MICROSOFT*XBOX*MEDIA"
PARTITIONS = (0, 0x18300000)
ATTR_DIR = 0x10


class Entry:
    def __init__(self, name, sector, size, attr):
        self.name, self.sector, self.size, self.attr = name, sector, size, attr

    @property
    def is_dir(self):
        return bool(self.attr & ATTR_DIR)


class Image:
    def __init__(self, path, mode="rb"):
        self.path = path
        self.f = open(path, mode)
        for base in PARTITIONS:
            self.f.seek(base + 32 * SECTOR)
            vd = self.f.read(28)
            if vd[:20] == MAGIC:
                self.base = base
                self.root = struct.unpack_from("<II", vd, 20)
                break
        else:
            raise ValueError(f"{path}: no XDVDFS volume descriptor")

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _read(self, sector, size, offset=0):
        self.f.seek(self.base + sector * SECTOR + offset)
        return self.f.read(size)

    def listdir(self, sector, size):
        if size == 0:
            return []
        table = self._read(sector, size)
        out, todo, seen = [], [0], set()
        while todo:
            off = todo.pop()
            if off in seen or off + 14 > len(table):
                continue
            seen.add(off)
            left, right, start, length, attr, n = struct.unpack_from("<HHIIBB", table, off)
            if left == 0xFFFF:          # padding
                continue
            out.append(Entry(table[off + 14:off + 14 + n].decode("latin-1"), start, length, attr))
            for child in (left, right):
                if child:
                    todo.append(child * 4)
        return sorted(out, key=lambda e: e.name.lower())

    def find(self, path):
        sector, size = self.root
        parts = [p for p in path.replace("\\", "/").split("/") if p]
        entry = None
        for i, part in enumerate(parts):
            entry = next((e for e in self.listdir(sector, size) if e.name.lower() == part.lower()), None)
            if entry is None:
                raise FileNotFoundError(f"{path}: '{part}' not in {self.path}")
            if i < len(parts) - 1:
                if not entry.is_dir:
                    raise NotADirectoryError(path)
                sector, size = entry.sector, entry.size
        return entry

    def read(self, path):
        e = self.find(path)
        return self._read(e.sector, e.size)

    def replace(self, path, data):
        """Overwrite a file's contents; the size must stay the same."""
        e = self.find(path)
        if len(data) != e.size:
            raise ValueError(f"{path}: size {len(data)} differs from {e.size} in the image")
        self.f.seek(self.base + e.sector * SECTOR)
        self.f.write(data)


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    with Image(sys.argv[1]) as img:
        print(f"partition at {img.base:#x}, root sector {img.root[0]}, size {img.root[1]}")
        if len(sys.argv) == 2:
            for e in img.listdir(*img.root):
                print(f"{'d' if e.is_dir else '-'} {e.size:>12} {e.name}")
        else:
            d = img.read(sys.argv[2])
            print(f"{sys.argv[2]}: {len(d)} bytes, MD5 {hashlib.md5(d).hexdigest()}")


if __name__ == "__main__":
    main()
