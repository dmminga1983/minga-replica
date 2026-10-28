#!/usr/bin/env python3
"""contrast.py - WCAG contrast for every text and background pair in your design tokens.

    python3 contrast.py replica/design/tokens.json
    python3 contrast.py --pair "#6b7280" "#ffffff"

tokens.json has "colors" (role -> hex) and "pairs": [{"fg": role, "bg": role, "use": "body"}].
use is body (4.5:1), large (3:1, text 24px+ or 19px+ bold) or ui (3:1, input borders, focus
rings, icons). AA is the floor. Exit 1 on any failure: fix it in the tokens, not per component.
"""
import json
import os
import re
import sys

NEED = {"body": 4.5, "large": 3.0, "ui": 3.0}


def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.match(r"^[0-9a-fA-F]{6}$", h):
        raise ValueError("not a hex colour: #%s" % h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = lum(hex_rgb(fg)), lum(hex_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return round((hi + 0.05) / (lo + 0.05), 2)


def check(tokens):
    colors = tokens.get("colors", {})
    out = []
    for p in tokens.get("pairs", []):
        fg, bg, use = p["fg"], p["bg"], p.get("use", "body")
        if fg not in colors or bg not in colors:
            out.append({"pair": "%s on %s" % (fg, bg), "ok": False, "ratio": None,
                        "need": NEED.get(use, 4.5), "why": "role missing from colors"})
            continue
        r = ratio(colors[fg], colors[bg])
        out.append({"pair": "%s on %s" % (fg, bg), "use": use, "ratio": r, "need": NEED.get(use, 4.5),
                    "ok": r >= NEED.get(use, 4.5)})
    return out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if "--pair" in a:
        i = a.index("--pair")
        r = ratio(a[i + 1], a[i + 2])
        print("%.2f:1  body %s  large/ui %s" % (r, "AA" if r >= 4.5 else "FAIL", "AA" if r >= 3 else "FAIL"))
        return 0 if r >= 4.5 else 1
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    res = check(json.load(open(a[0], encoding="utf-8")))
    fails = 0
    for r in res:
        fails += not r["ok"]
        print("  %-4s %-28s %s  need %.1f" % ("ok" if r["ok"] else "FAIL", r["pair"],
                                              "%5.2f:1" % r["ratio"] if r["ratio"] else "  -   ", r["need"]))
    print("\n  %d pair(s), %d failure(s)" % (len(res), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
