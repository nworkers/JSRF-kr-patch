"""DXT3 (BC2) alpha decode and encode for jetfont pages.

jetfont.dat keeps the glyph shapes in the explicit 4-bit alpha; every colour
block is the same white block, so encoding is lossless for 4-bit alpha images.
Images here are bytearrays of 4-bit values (0-15), row-major.
"""

WHITE_BLOCK = bytes.fromhex("0000ffff55555555")   # c0=0x0000, c1=0xFFFF, all indexes 1


def decode_alpha(buf, w, h):
    img = bytearray(w * h)
    p = 0
    for by in range(h // 4):
        for bx in range(w // 4):
            for r in range(4):
                v = buf[p + 2 * r] | buf[p + 2 * r + 1] << 8
                row = (by * 4 + r) * w + bx * 4
                for c in range(4):
                    img[row + c] = (v >> (4 * c)) & 15
            p += 16
    return img


def colour_blocks(buf):
    """Set of distinct 8-byte colour blocks in a DXT3 buffer."""
    return {bytes(buf[p + 8:p + 16]) for p in range(0, len(buf), 16)}


def encode_alpha(img, w, h):
    out = bytearray()
    for by in range(h // 4):
        for bx in range(w // 4):
            for r in range(4):
                row = (by * 4 + r) * w + bx * 4
                v = 0
                for c in range(4):
                    v |= (img[row + c] & 15) << (4 * c)
                out += bytes((v & 0xFF, v >> 8))
            out += WHITE_BLOCK
    return bytes(out)
