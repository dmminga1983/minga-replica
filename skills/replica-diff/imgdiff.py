#!/usr/bin/env python3
"""imgdiff.py - compare a screenshot of the original with one of your clone. No libraries.

    python3 imgdiff.py original.png clone.png                      # layout score and regions
    python3 imgdiff.py original.png clone.png --out diff.png       # picture of where they differ
    python3 imgdiff.py original.png clone.png --json > S07.json    # for parity.py --visual
    python3 imgdiff.py before.png after.png --mode pixel           # your own regressions

Layout mode (the default) turns both images into edge maps, scales them to the same width, cuts
them into a grid and compares how much structure each cell holds. Colour does not count, so your
rebrand does not count against you: the question is whether the information sits in the same
places with the same hierarchy. Pixel mode is an exact comparison, for the clone today against
the clone last week, never against the original.

Score bands: 90+ matches, 75+ close, 50+ partly, under 50 different. Regions are reported in the
first image's pixel coordinates, biggest first. Take both screenshots at the same viewport, in
the same state, with the same shape of data. Reads 8 and 16-bit PNGs, not interlaced ones.
"""
import json
import os
import struct
import sys
import zlib

WIDTH = 240
CELL = 8
EDGE = 22


class PngError(Exception):
    pass


def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PngError("%s is not a PNG" % path)
    pos, idat, plte = 8, [], None
    w = h = depth = ctype = inter = None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            plte = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
    if inter:
        raise PngError("%s is interlaced: save it again without interlacing" % path)
    if depth not in (8, 16):
        raise PngError("%s uses %d-bit colour: save it as 8-bit" % (path, depth))
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if ch is None:
        raise PngError("unsupported PNG colour type %s" % ctype)
    bpp = ch * depth // 8
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        ft = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ft == 1:
                line[x] = (line[x] + a) & 255
            elif ft == 2:
                line[x] = (line[x] + b) & 255
            elif ft == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[x] = (line[x] + pr) & 255
        rows.append(line)
        prev = line
    step = depth // 8
    gray = []
    for line in rows:
        out = []
        for x in range(w):
            px = line[x * bpp:(x + 1) * bpp]
            vals = px[::step]
            if ctype == 3:
                r, g, b = plte[vals[0]] if plte else (vals[0],) * 3
            elif ch in (1, 2):
                r = g = b = vals[0]
            else:
                r, g, b = vals[0], vals[1], vals[2]
            if ch in (2, 4):
                alpha = vals[-1] / 255.0
                r, g, b = [255 - (255 - v) * alpha for v in (r, g, b)]
            out.append(0.299 * r + 0.587 * g + 0.114 * b)
        gray.append(out)
    return w, h, gray


def write_png(path, w, h, rows):
    raw = b"".join(b"\x00" + bytes(int(max(0, min(255, v))) for v in r) for r in rows)
    def chunk(k, b):
        return struct.pack(">I", len(b)) + k + b + struct.pack(">I", zlib.crc32(k + b) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def scale(w, h, gray, width=WIDTH):
    f = w / float(width)
    nh = max(1, int(h / f))
    out = []
    for y in range(nh):
        y0, y1 = int(y * f), max(int(y * f) + 1, int((y + 1) * f))
        row = []
        for x in range(width):
            x0, x1 = int(x * f), max(int(x * f) + 1, int((x + 1) * f))
            s = n = 0
            for yy in range(y0, min(y1, h)):
                r = gray[yy]
                for xx in range(x0, min(x1, w)):
                    s += r[xx]
                    n += 1
            row.append(s / n if n else 255)
        out.append(row)
    return out, f


def edges(img):
    h, w = len(img), len(img[0])
    e = [[0] * w for _ in range(h)]
    for y in range(h - 1):
        for x in range(w - 1):
            if abs(img[y][x + 1] - img[y][x]) + abs(img[y + 1][x] - img[y][x]) > EDGE:
                e[y][x] = 1
    return e


def cells(e, h):
    rows = (h + CELL - 1) // CELL
    cols = (len(e[0]) + CELL - 1) // CELL
    d = [[0.0] * cols for _ in range(rows)]
    for cy in range(rows):
        for cx in range(cols):
            s = n = 0
            for y in range(cy * CELL, min(h, (cy + 1) * CELL)):
                for x in range(cx * CELL, min(len(e[0]), (cx + 1) * CELL)):
                    s += e[y][x]
                    n += 1
            d[cy][cx] = s / n if n else 0.0
    return d


def band(s):
    return "matches" if s >= 90 else "close" if s >= 75 else "partly" if s >= 50 else "different"


def compare(path_a, path_b, mode="layout", out=None):
    wa, ha, ga = read_png(path_a)
    wb, hb, gb = read_png(path_b)
    sa, fa = scale(wa, ha, ga)
    sb, _ = scale(wb, hb, gb)
    h = min(len(sa), len(sb))
    height_diff = round(100.0 * (len(sb) - len(sa)) / len(sa), 1)
    if mode == "pixel":
        diff = [[abs(sa[y][x] - sb[y][x]) for x in range(WIDTH)] for y in range(h)]
        mean = sum(map(sum, diff)) / float(h * WIDTH)
        score = round(max(0.0, 100 - mean / 2.55), 1)
        bad = [[1 if v > 32 else 0 for v in r] for r in diff]
        grid = cells(bad, h)
        mism = [[g > 0.05 for g in r] for r in grid]
    else:
        da, db = cells(edges(sa[:h]), h), cells(edges(sb[:h]), h)
        num = den = 0.0
        mism = []
        for ra, rb in zip(da, db):
            mr = []
            for a, b in zip(ra, rb):
                if max(a, b) < 0.02:
                    mr.append(False)
                    continue
                sim = min(a, b) / max(a, b)
                num += sim
                den += 1
                mr.append(sim < 0.5)
            mism.append(mr)
        score = round(100 * num / den, 1) if den else 100.0
    regions = blobs(mism, fa)
    if out:
        pic = [[(sa[y][x] * 0.35 + (0 if mism[y // CELL][x // CELL] else 160)) for x in range(WIDTH)]
               for y in range(h)]
        write_png(out, WIDTH, h, pic)
    if abs(height_diff) > 15:
        score = round(score * 0.9, 1)
    return {"a": path_a, "b": path_b, "mode": mode, "score": score, "band": band(score),
            "regions": regions[:8], "height_diff_pct": height_diff}


def blobs(mask, f):
    seen, out = set(), []
    for y, r in enumerate(mask):
        for x, v in enumerate(r):
            if not v or (y, x) in seen:
                continue
            stack, pts = [(y, x)], []
            seen.add((y, x))
            while stack:
                cy, cx = stack.pop()
                pts.append((cy, cx))
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < len(mask) and 0 <= nx < len(mask[0]) and mask[ny][nx] and (ny, nx) not in seen:
                        seen.add((ny, nx))
                        stack.append((ny, nx))
            ys, xs = [p[0] for p in pts], [p[1] for p in pts]
            k = CELL * f
            out.append({"x": int(min(xs) * k), "y": int(min(ys) * k), "w": int((max(xs) - min(xs) + 1) * k),
                        "h": int((max(ys) - min(ys) + 1) * k), "cells": len(pts)})
    out.sort(key=lambda b: -b["cells"])
    return out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    mode, out = "layout", None
    if "--mode" in a:
        i = a.index("--mode")
        mode = a[i + 1]
        del a[i:i + 2]
    if "--out" in a:
        i = a.index("--out")
        out = a[i + 1]
        del a[i:i + 2]
    if len(a) < 2 or not all(os.path.exists(x) for x in a[:2]):
        print(__doc__)
        return 1
    try:
        r = compare(a[0], a[1], mode, out)
    except PngError as e:
        print("imgdiff: %s" % e, file=sys.stderr)
        return 2
    if as_json:
        print(json.dumps(r, indent=1))
        return 0
    print("%s  %s vs %s" % (mode.upper(), os.path.basename(a[0]), os.path.basename(a[1])))
    print("  score %.1f  %s" % (r["score"], r["band"]))
    if abs(r["height_diff_pct"]) > 5:
        print("  height: the second page is %+.0f%% %s" % (r["height_diff_pct"], "longer" if r["height_diff_pct"] > 0 else "shorter"))
    for g in r["regions"]:
        print("  differs at x=%d y=%d  %dx%d px" % (g["x"], g["y"], g["w"], g["h"]))
    if out:
        print("  picture: %s (bright cells differ)" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
