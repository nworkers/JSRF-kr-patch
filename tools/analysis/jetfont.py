"""List the textures in Media/Font/jetfont.dat and optionally dump their alpha.

jetfont.dat is a NORM container holding a linked list of six textures, not one
512x2304 image. Each record:

  node  (16 bytes): u32 descriptor offset, u32 next node offset (the last
                    one points at the end of the file),
                    u16 data offset from the descriptor, u16 size in 64 KiB,
                    u32 0
  descriptor (32 bytes at the node's descriptor offset): u32 id, ...,
                    u32 width at +0x14, u32 0x106 at +0x18
  pixels: DXT3 (4x4 blocks, 8 bytes explicit 4-bit alpha + 8 bytes colour),
          linear block order, size bytes

The first node sits at 0x10. The game's loader (JP/US 0x2C040) does not test
for the end: it walks a fixed six nodes (immediate 6 at 0x2C04A). Textures 0-3 are the double-byte pages
(512x512, 19x19 cells of 26 px), textures 4-5 the single-byte pages (256x256,
12x7 cells of 21x34 px); see font_tables.py for the descriptors in the XBE.

With --png DIR, writes texN.png (8-bit grey = alpha) and, with --grid, draws the
cell grid. The images are game data: DIR must be under work/.

usage: python -I tools/analysis/jetfont.py <jetfont.dat> [--png work/jetfont [--grid]]
"""
import hashlib
import os
import struct
import sys
import zlib

JETFONT_MD5 = "bc566ef593dbf603e5332a7af346e2c8"
GRIDS = {512: (26, 26), 256: (21, 34)}   # cell w, h per texture width


def records(data):
    if data[:4] != b"NORM":
        raise ValueError("not a NORM file")
    out, node = [], 0x10
    while node:
        desc, nxt, info, _ = struct.unpack_from("<4I", data, node)
        width = struct.unpack_from("<I", data, desc + 0x14)[0]
        start = desc + (info & 0xFFFF)
        size = (info >> 16) * 0x10000
        out.append({"node": node, "descriptor": desc, "id": struct.unpack_from("<I", data, desc)[0],
                    "width": width, "height": size // width, "offset": start, "size": size})
        node = nxt if nxt + 16 <= len(data) else 0
        if len(out) > 64:
            raise ValueError("node list does not end")
    return out


def dxt3_alpha(buf, w, h):
    img = bytearray(w * h)
    p = 0
    for by in range(h // 4):
        for bx in range(w // 4):
            for r in range(4):
                v = buf[p + 2 * r] | buf[p + 2 * r + 1] << 8
                row = (by * 4 + r) * w + bx * 4
                for c in range(4):
                    img[row + c] = ((v >> (4 * c)) & 15) * 17
            p += 16
    return img


def write_png(path, img, w, h):
    raw = b"".join(b"\0" + bytes(img[y * w:(y + 1) * w]) for y in range(h))

    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    args = sys.argv[1:]
    grid = "--grid" in args
    if grid:
        args.remove("--grid")
    out_dir = None
    if "--png" in args:
        i = args.index("--png")
        out_dir = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__)
    data = open(args[0], "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    print(f"{args[0]}: {len(data)} bytes, MD5 {md5}"
          + ("" if md5 == JETFONT_MD5 else f" (expected {JETFONT_MD5})"))
    recs = records(data)
    end = recs[-1]["offset"] + recs[-1]["size"]
    print(f"{len(recs)} textures, data ends at {end:#x} (file size {len(data):#x})")
    for n, r in enumerate(recs):
        print(f"  tex{n}: node {r['node']:#08x} descriptor {r['descriptor']:#08x} id {r['id']:08x} "
              f"{r['width']}x{r['height']} DXT3 pixels {r['offset']:#08x}+{r['size']:#x}")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for n, r in enumerate(recs):
            w, h = r["width"], r["height"]
            img = dxt3_alpha(data[r["offset"]:r["offset"] + r["size"]], w, h)
            if grid and w in GRIDS:
                cw, ch = GRIDS[w]
                for y in range(h):
                    for xx in range(w):
                        if xx % cw == 0 or y % ch == 0:
                            img[y * w + xx] = max(img[y * w + xx], 80)
            path = os.path.join(out_dir, f"tex{n}.png")
            write_png(path, img, w, h)
            print(f"wrote {path} (game data: keep it in work/)")


if __name__ == "__main__":
    main()
