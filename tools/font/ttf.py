"""A small TrueType reader and rasterizer (standard library only).

Supports static fonts with 'glyf' outlines: cmap formats 4 and 12, simple and
composite glyphs, quadratic curves. Variable fonts (gvar) and CFF outlines are
rejected. Rasterization uses the non-zero winding rule with exact horizontal
coverage on a fixed number of sub-scanlines per pixel, so the same font file
always gives the same bitmap on every platform.
"""
import struct

CURVE_STEPS = 8          # line segments per quadratic curve
SUBSCANLINES = 16        # vertical samples per pixel


class Font:
    def __init__(self, path):
        self.data = d = open(path, "rb").read()
        tag = d[:4]
        if tag == b"OTTO":
            raise ValueError(f"{path}: CFF outlines are not supported")
        if tag not in (b"\x00\x01\x00\x00", b"true"):
            raise ValueError(f"{path}: not a TrueType font")
        count = struct.unpack_from(">H", d, 4)[0]
        self.tables = {}
        for i in range(count):
            t, _, off, length = struct.unpack_from(">4sIII", d, 12 + 16 * i)
            self.tables[t.decode("latin-1")] = (off, length)
        for need in ("head", "maxp", "cmap", "loca", "glyf", "hhea", "hmtx"):
            if need not in self.tables:
                raise ValueError(f"{path}: missing table {need}")
        if "gvar" in self.tables:
            raise ValueError(f"{path}: variable fonts are not supported; use a static instance")
        head = self.tables["head"][0]
        self.units_per_em = struct.unpack_from(">H", d, head + 18)[0]
        self.loca_long = struct.unpack_from(">h", d, head + 50)[0] == 1
        self.num_glyphs = struct.unpack_from(">H", d, self.tables["maxp"][0] + 4)[0]
        hhea = self.tables["hhea"][0]
        self.ascender, self.descender = struct.unpack_from(">hh", d, hhea + 4)
        self.num_hmetrics = struct.unpack_from(">H", d, hhea + 34)[0]
        self.cmap = self._read_cmap()

    def _u16(self, off):
        return struct.unpack_from(">H", self.data, off)[0]

    def _read_cmap(self):
        d = self.data
        base = self.tables["cmap"][0]
        n = self._u16(base + 2)
        subs = {}
        for i in range(n):
            pid, eid, off = struct.unpack_from(">HHI", d, base + 4 + 8 * i)
            subs[(pid, eid)] = base + off
        for key in ((3, 10), (0, 4), (0, 6)):
            if key in subs and self._u16(subs[key]) == 12:
                return self._cmap12(subs[key])
        for key in ((3, 1), (0, 3), (0, 1), (0, 0)):
            if key in subs and self._u16(subs[key]) == 4:
                return self._cmap4(subs[key])
        raise ValueError("no usable Unicode cmap (formats 4 or 12)")

    def _cmap4(self, off):
        d = self.data
        segx2 = self._u16(off + 6)
        ends = off + 14
        starts = ends + segx2 + 2
        deltas = starts + segx2
        ranges = deltas + segx2
        m = {}
        for s in range(segx2 // 2):
            end = self._u16(ends + 2 * s)
            start = self._u16(starts + 2 * s)
            delta = struct.unpack_from(">h", d, deltas + 2 * s)[0]
            ro = self._u16(ranges + 2 * s)
            for c in range(start, end + 1):
                if c == 0xFFFF:
                    continue
                if ro == 0:
                    g = (c + delta) & 0xFFFF
                else:
                    g = self._u16(ranges + 2 * s + ro + 2 * (c - start))
                    if g:
                        g = (g + delta) & 0xFFFF
                if g:
                    m[c] = g
        return m

    def _cmap12(self, off):
        n = struct.unpack_from(">I", self.data, off + 12)[0]
        m = {}
        for i in range(n):
            start, end, g = struct.unpack_from(">III", self.data, off + 16 + 12 * i)
            for c in range(start, end + 1):
                m[c] = g + c - start
        return m

    def glyph_index(self, ch):
        return self.cmap.get(ord(ch), 0)

    def _glyph_range(self, g):
        loca = self.tables["loca"][0]
        if self.loca_long:
            a, b = struct.unpack_from(">II", self.data, loca + 4 * g)
        else:
            a, b = (2 * v for v in struct.unpack_from(">HH", self.data, loca + 2 * g))
        return self.tables["glyf"][0] + a, b - a

    def contours(self, g, depth=0):
        """Contours of glyph g as lists of (x, y, on_curve) in font units."""
        if depth > 8:
            raise ValueError("composite glyph nesting too deep")
        off, length = self._glyph_range(g)
        if length == 0:
            return []
        d = self.data
        ncont = struct.unpack_from(">h", d, off)[0]
        p = off + 10
        if ncont >= 0:
            ends = struct.unpack_from(f">{ncont}H", d, p)
            p += 2 * ncont
            npts = ends[-1] + 1 if ncont else 0
            p += 2 + self._u16(p)              # skip instructions
            flags = []
            while len(flags) < npts:
                f = d[p]
                p += 1
                flags.append(f)
                if f & 8:
                    rep = d[p]
                    p += 1
                    flags.extend([f] * rep)
            xs, p = self._coords(flags, p, 2, 16)
            ys, p = self._coords(flags, p, 4, 32)
            out, start = [], 0
            for e in ends:
                out.append([(xs[i], ys[i], bool(flags[i] & 1)) for i in range(start, e + 1)])
                start = e + 1
            return out
        out = []
        while True:
            flags, sub = struct.unpack_from(">HH", d, p)
            p += 4
            if flags & 1:
                a1, a2 = struct.unpack_from(">hh", d, p)
                p += 4
            else:
                a1, a2 = struct.unpack_from(">bb", d, p)
                p += 2
            if not flags & 2:
                raise ValueError("composite point matching is not supported")
            xx, xy, yx, yy = 1.0, 0.0, 0.0, 1.0
            if flags & 8:
                xx = yy = struct.unpack_from(">h", d, p)[0] / 16384
                p += 2
            elif flags & 0x40:
                xx, yy = (v / 16384 for v in struct.unpack_from(">hh", d, p))
                p += 4
            elif flags & 0x80:
                xx, xy, yx, yy = (v / 16384 for v in struct.unpack_from(">hhhh", d, p))
                p += 8
            for c in self.contours(sub, depth + 1):
                out.append([(x * xx + y * yx + a1, x * xy + y * yy + a2, on) for x, y, on in c])
            if not flags & 0x20:
                break
        return out

    def _coords(self, flags, p, short_bit, same_bit):
        d = self.data
        vals, v = [], 0
        for f in flags:
            if f & short_bit:
                dv = d[p]
                p += 1
                v += dv if f & same_bit else -dv
            elif not f & same_bit:
                v += struct.unpack_from(">h", d, p)[0]
                p += 2
            vals.append(v)
        return vals, p


def flatten(contours):
    """Turn TrueType contours into closed polylines of (x, y) points."""
    polys = []
    for c in contours:
        if len(c) < 2:
            continue
        pts = list(c)
        # start at an on-curve point (or an implied midpoint)
        k = next((i for i, q in enumerate(pts) if q[2]), None)
        if k is None:
            a, b = pts[-1], pts[0]
            pts.insert(0, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, True))
            k = 0
        pts = pts[k:] + pts[:k]
        poly = [(pts[0][0], pts[0][1])]
        cur = pts[0]
        ctrl = None
        for q in pts[1:] + [pts[0]]:
            if q[2]:
                if ctrl is None:
                    poly.append((q[0], q[1]))
                else:
                    _curve(poly, cur, ctrl, q)
                    ctrl = None
                cur = q
            else:
                if ctrl is not None:
                    mid = ((ctrl[0] + q[0]) / 2, (ctrl[1] + q[1]) / 2, True)
                    _curve(poly, cur, ctrl, mid)
                    cur = mid
                ctrl = q
        polys.append(poly)
    return polys


def _curve(poly, a, c, b):
    for i in range(1, CURVE_STEPS + 1):
        t = i / CURVE_STEPS
        u = 1 - t
        poly.append((u * u * a[0] + 2 * u * t * c[0] + t * t * b[0],
                     u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]))


def bbox(polys):
    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def rasterize(polys, width, height, transform):
    """Coverage (0.0-1.0) per pixel, row-major, top row first.

    transform(x, y) maps font units to pixel coordinates (y down).
    """
    edges = []
    for poly in polys:
        pts = [transform(x, y) for x, y in poly]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
    cov = [0.0] * (width * height)
    w = 1.0 / SUBSCANLINES
    for row in range(height):
        for s in range(SUBSCANLINES):
            sy = row + (s + 0.5) * w
            xs = []
            for x0, y0, x1, y1 in edges:
                if (y0 <= sy < y1) or (y1 <= sy < y0):
                    xs.append((x0 + (sy - y0) * (x1 - x0) / (y1 - y0), 1 if y1 > y0 else -1))
            if not xs:
                continue
            xs.sort()
            wind = 0
            for i in range(len(xs) - 1):
                wind += xs[i][1]
                if wind != 0:
                    _span(cov, row * width, width, xs[i][0], xs[i + 1][0], w)
    return [min(1.0, c) for c in cov]


def _span(cov, base, width, a, b, weight):
    a = max(a, 0.0)
    b = min(b, float(width))
    if b <= a:
        return
    ia, ib = int(a), int(b)
    if ia == ib:
        cov[base + ia] += (b - a) * weight
        return
    cov[base + ia] += (ia + 1 - a) * weight
    for i in range(ia + 1, min(ib, width)):
        cov[base + i] += weight
    if ib < width:
        cov[base + ib] += (b - ib) * weight
