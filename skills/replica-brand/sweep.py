#!/usr/bin/env python3
"""sweep.py - find anything of the original app left in your code, before launch.

    python3 sweep.py . --avoid "OriginalApp,Its Company" --domains original.com --colors "#006bff"
    python3 sweep.py . --config replica/brand.json

brand.json: {"avoid": [...names], "domains": [...], "colors": [...hex]}

It searches file contents and file names, case-insensitive, for:
    the original's names, also inside identifiers (OriginalAppEmbed, original_app_id,
    original-app.svg) and in Russian transliteration (Calendly also as "Календли")
    its domains, and its brand colours in hex (3 or 6 digits) and rgb() form
It skips node_modules, build output, .git and the replica/ planning folder, where the original's
name belongs. Exit 1 means something is left: replica-deploy will not ship until it is clean.
"""
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "out", ".vercel", ".turbo", "coverage",
             "replica", "__pycache__", ".venv", "venv", "Pods", ".expo", ".gradle"}
TEXT_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".md", ".mdx", ".html", ".css", ".scss",
            ".svg", ".txt", ".yml", ".yaml", ".toml", ".py", ".rb", ".go", ".swift", ".kt", ".java",
            ".xml", ".plist", ".strings", ".env", ".example", ".vue", ".svelte", ".astro", ".sql", ".liquid"}

LAT_CYR = [("sch", "щ"), ("sh", "ш"), ("ch", "ч"), ("zh", "ж"), ("kh", "х"), ("ts", "ц"), ("yu", "ю"),
           ("ya", "я"), ("yo", "ё"), ("ee", "и"), ("oo", "у"), ("a", "а"), ("b", "б"), ("c", "к"),
           ("d", "д"), ("e", "е"), ("f", "ф"), ("g", "г"), ("h", "х"), ("i", "и"), ("j", "дж"),
           ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"), ("q", "к"),
           ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"), ("v", "в"), ("w", "в"), ("x", "кс"),
           ("y", "и"), ("z", "з")]


def translit(name):
    s, out, i = name.lower(), "", 0
    while i < len(s):
        for lat, cyr in LAT_CYR:
            if s.startswith(lat, i):
                out += cyr
                i += len(lat)
                break
        else:
            out += s[i]
            i += 1
    return out


def variants(name):
    base = name.strip()
    if not base:
        return []
    parts = re.split(r"[\s_.-]+", base)
    v = {base.lower(), "".join(parts).lower(), "_".join(parts).lower(), "-".join(parts).lower()}
    if re.search(r"[a-zA-Z]", base):
        t = translit("".join(parts))
        if len(t) >= 4:
            v.add(t)
            if t.endswith("и"):
                v.add(t[:-1] + "ли" if not t.endswith("ли") else t)
    return sorted(x for x in v if len(x) >= 3)


def color_forms(c):
    h = c.strip().lstrip("#").lower()
    if len(h) == 3:
        h = "".join(x * 2 for x in h)
    forms = ["#" + h]
    if h[0] == h[1] and h[2] == h[3] and h[4] == h[5]:
        forms.append("#" + h[0] + h[2] + h[4])
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    forms.append(re.compile(r"rgba?\(\s*%d\s*,\s*%d\s*,\s*%d\b" % (r, g, b)))
    return forms


def build_patterns(avoid=(), domains=(), colors=()):
    pats = []
    for n in avoid:
        for v in variants(n):
            pats.append(("name", n, re.compile(re.escape(v), re.I)))
    for d in domains:
        pats.append(("domain", d, re.compile(re.escape(d.lower().replace("https://", "").replace("http://", "").strip("/")), re.I)))
    for c in colors:
        for f in color_forms(c):
            pats.append(("color", c, f if hasattr(f, "search") else re.compile(re.escape(f) + r"(?![0-9a-f])", re.I)))
    return pats


def sweep(root, pats):
    hits = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            path = os.path.join(base, f)
            rel = os.path.relpath(path, root)
            for kind, what, rx in pats:
                if kind == "name" and rx.search(f):
                    hits.append((rel, 0, kind, what, "in the file name"))
            ext = os.path.splitext(f)[1].lower()
            if ext not in TEXT_EXT and not f.startswith(".env"):
                continue
            try:
                lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for kind, what, rx in pats:
                    if rx.search(line):
                        hits.append((rel, i, kind, what, line.strip()[:90]))
    return hits


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    cfg = {"avoid": [], "domains": [], "colors": []}
    for k in ("avoid", "domains", "colors"):
        if "--" + k in a:
            i = a.index("--" + k)
            cfg[k] = [x.strip() for x in a[i + 1].split(",") if x.strip()]
            del a[i:i + 2]
    if "--config" in a:
        i = a.index("--config")
        data = json.load(open(a[i + 1], encoding="utf-8"))
        for k in cfg:
            cfg[k] += data.get(k, [])
        del a[i:i + 2]
    root = a[0] if a else "."
    if not any(cfg.values()):
        print(__doc__)
        return 2
    hits = sweep(root, build_patterns(**cfg))
    for rel, line, kind, what, text in hits:
        print("  %s:%s  %-6s %-18s %s" % (rel, line, kind, what[:18], text))
    print("\n  %s" % ("CLEAN: nothing of the original left" if not hits else "%d hit(s): fix them, then sweep again" % len(hits)))
    print("  Also check by eye: favicon, page titles, email templates, the share image, the app icon.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
