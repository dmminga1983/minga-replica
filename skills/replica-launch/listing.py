#!/usr/bin/env python3
"""listing.py - lint your store listing for App Store, Google Play and RuStore.

    python3 listing.py replica/launch/listing.json
    python3 listing.py replica/launch/listing.json --store rustore

listing.json (start from listing.example.json):
    {"avoid": ["OriginalApp"],
     "appstore":   {"name", "subtitle", "promotional_text", "keywords", "description", "whats_new"},
     "googleplay": {"title", "short_description", "full_description"},
     "rustore":    {"name", "short_description", "full_description"},
     "locales": {"ru": {...same shape...}}}          (optional, linted the same way)

Limits come from stores.json. Characters are counted the way a person counts them, so Cyrillic
and emoji count as one. It also flags: ranking and price claims in short fields ("№1", "лучший",
"best", "free"), emoji and all caps in titles, App Store keywords that waste characters (spaces,
repeats, words already in the name or subtitle), and any name from "avoid" anywhere, which is
the fastest way to a copycat rejection or a takedown. Exit 1 on any error.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
STORES = json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))["stores"]
CLAIMS = re.compile(r"(№\s?1|#1|\bno\.?\s?1\b|\bnumber one\b|\bbest\b|\btop\b|\bfree\b|лучш\w*|\bтоп\b|"
                    r"бесплатн\w*|самый|самое|самая|\b1-й\b)", re.I)
SHORT = {"name", "title", "subtitle", "short_description", "promotional_text"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def length(s):
    return sum(1 for ch in unicodedata.normalize("NFC", s) if unicodedata.category(ch) not in ("Mn", "Cf"))


def lint_store(store, fields, avoid, label=""):
    spec = STORES[store]["fields"]
    out = []
    for f, limit in spec.items():
        v = fields.get(f, "")
        if not v:
            if f in ("name", "title", "full_description", "description"):
                out.append(("ERROR", store, f, "missing"))
            continue
        n = length(v)
        if n > limit:
            out.append(("ERROR", store, f, "%d characters, the limit is %d" % (n, limit)))
        if f in SHORT:
            m = CLAIMS.findall(v)
            if m:
                out.append(("WARN", store, f, "ranking or price claim (%s): stores reject or demote these" % ", ".join(sorted({x if isinstance(x, str) else x[0] for x in m}))))
            if f in ("name", "title") and EMOJI.search(v):
                out.append(("ERROR", store, f, "emoji in the title"))
            caps = [w for w in re.findall(r"\b[A-ZА-ЯЁ]{3,}\b", v)]
            if f in ("name", "title") and len(caps) >= 2:
                out.append(("WARN", store, f, "all-caps words: %s" % ", ".join(caps)))
        for name in avoid:
            if name and re.search(re.escape(name), v, re.I):
                out.append(("ERROR", store, f, "contains the original's name %r: copycat rejection risk" % name))
    if store == "appstore" and fields.get("keywords"):
        kw = fields["keywords"]
        if ", " in kw:
            out.append(("WARN", store, "keywords", "spaces after commas waste characters"))
        words = [k.strip().lower() for k in kw.split(",") if k.strip()]
        if len(words) != len(set(words)):
            out.append(("WARN", store, "keywords", "repeated keywords"))
        named = set(re.findall(r"[\wЀ-ӿ]+", (fields.get("name", "") + " " + fields.get("subtitle", "")).lower()))
        dup = sorted({w for w in words if w in named})
        if dup:
            out.append(("WARN", store, "keywords", "already in the name or subtitle, wasted: %s" % ", ".join(dup)))
    return [(lvl, st + label, f, msg) for lvl, st, f, msg in out]


def lint(doc, only=None):
    avoid = doc.get("avoid", [])
    res = []
    for store in STORES:
        if only and store != only:
            continue
        if store in doc:
            res += lint_store(store, doc[store], avoid)
        for loc, d in (doc.get("locales") or {}).items():
            if store in d:
                res += lint_store(store, d[store], avoid, " [%s]" % loc)
    return res


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    only = None
    if "--store" in a:
        i = a.index("--store")
        only = a[i + 1]
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    res = lint(json.load(open(a[0], encoding="utf-8")), only)
    for lvl, store, f, msg in res:
        print("  %-5s %-18s %-18s %s" % (lvl, store, f, msg))
    errors = sum(1 for r in res if r[0] == "ERROR")
    print("\n  %s" % ("READY" if not res else "%d error(s), %d warning(s)" % (errors, len(res) - errors)))
    for s in STORES.values():
        if not only or s["name"].lower().replace(" ", "") == only:
            print("  %s rules to read before submitting: %s" % (s["name"], "; ".join(s["rules"])))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
