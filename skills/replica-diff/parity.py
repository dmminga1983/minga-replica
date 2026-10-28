#!/usr/bin/env python3
"""parity.py - how much of the original your clone can actually do.

    python3 parity.py replica/features.csv
    python3 parity.py replica/features.csv --visual replica/diffs/*.json --markdown > replica/parity.md

features.csv columns: feature, area, priority, original, clone, notes
    priority   must / should / could
    original   yes, or no for something the clone adds that the original does not have
    clone      yes / partial / no / skip   (skip needs a reason in notes)

Weights must 3, should 2, could 1; partial counts as half. Rows the original does not have
(your own fixes) and skip rows are left out of the score: you are not penalised for not copying
what you chose not to copy, and not rewarded for what you added. Any must-have not done means
not shippable, and the report says so.
"""
import csv
import glob
import json
import os
import sys

W = {"must": 3, "should": 2, "could": 1}
DONE = {"yes": 1.0, "partial": 0.5, "no": 0.0}


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return [{k.strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def score(rows):
    total = got = 0.0
    areas, missing, must_left, skipped, added, problems = {}, [], [], [], [], []
    for r in rows:
        pr, orig, cl = r.get("priority", "").lower(), r.get("original", "yes").lower(), r.get("clone", "no").lower()
        name = r.get("feature", "?")
        if pr not in W:
            problems.append("%s: priority %r is not must, should or could" % (name, pr))
            continue
        if orig == "no":
            added.append(name)
            continue
        if cl == "skip":
            if not r.get("notes"):
                problems.append("%s: skip without a reason in notes" % name)
            skipped.append(name)
            continue
        if cl not in DONE:
            problems.append("%s: clone %r is not yes, partial, no or skip" % (name, cl))
            cl = "no"
        w = W[pr]
        total += w
        got += w * DONE[cl]
        a = areas.setdefault(r.get("area") or "general", [0.0, 0.0])
        a[0] += w * DONE[cl]
        a[1] += w
        if cl != "yes":
            missing.append((pr, r.get("area", ""), name, cl))
            if pr == "must":
                must_left.append(name)
    musts = [r for r in rows if r.get("priority", "").lower() == "must"
             and r.get("original", "yes").lower() != "no" and r.get("clone", "").lower() != "skip"]
    order = {"must": 0, "should": 1, "could": 2}
    missing.sort(key=lambda m: (order[m[0]], m[3] != "partial", m[1], m[2]))
    pct = round(100 * got / total, 1) if total else 0.0
    return {"score": pct, "musts_done": len(musts) - len(must_left), "musts": len(musts),
            "areas": {k: round(100 * v[0] / v[1], 1) for k, v in areas.items()},
            "missing": missing, "skipped": skipped, "added": added, "problems": problems,
            "shippable": not must_left and not problems}


def verdict(res, visual=None):
    if not res["shippable"]:
        return "NOT SHIPPABLE: %d must-have(s) missing" % (res["musts"] - res["musts_done"]) \
            if res["musts"] != res["musts_done"] else "NOT SHIPPABLE: fix the matrix problems first"
    if res["score"] < 80:
        return "NOT YET: all must-haves done, feature score under 80"
    if res["added"]:
        return "BETTER THAN THE ORIGINAL: shippable, plus %d fix(es) of your own" % len(res["added"])
    return "SHIPPABLE, but a straight copy has no reason to exist: run /replica-users"


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    md = "--markdown" in a
    a = [x for x in a if x != "--markdown"]
    visual = []
    if "--visual" in a:
        i = a.index("--visual")
        files = []
        for x in a[i + 1:]:
            files += glob.glob(x)
        a = a[:i]
        for f in files:
            try:
                visual.append(json.load(open(f, encoding="utf-8")))
            except (OSError, ValueError):
                pass
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    res = score(load(a[0]))
    h = "## " if md else ""
    print("%sPARITY  features %.1f%%  must-haves %d/%d" % (h, res["score"], res["musts_done"], res["musts"]))
    print("\n%sBy area, weakest first" % h)
    for k, v in sorted(res["areas"].items(), key=lambda kv: kv[1]):
        print("  %-20s %5.1f%%" % (k, v))
    if visual:
        print("\n%sLayout (structure only, colour ignored)" % h)
        for v in visual:
            print("  %-24s %5.1f  %s" % (os.path.basename(v.get("b", "?")), v.get("score", 0), v.get("band", "")))
    print("\n%sMissing, in build order" % h)
    for pr, area, name, cl in res["missing"][:40]:
        print("  %-6s %-14s %s%s" % (pr, area[:14], name, " (partial)" if cl == "partial" else ""))
    if res["skipped"]:
        print("\n%sLeft out on purpose: %s" % (h, ", ".join(res["skipped"])))
    if res["added"]:
        print("%sYour own additions: %s" % (h, ", ".join(res["added"])))
    for p in res["problems"]:
        print("  MATRIX  " + p)
    print("\n%sVERDICT  %s" % (h, verdict(res)))
    return 0 if res["shippable"] else 1


if __name__ == "__main__":
    sys.exit(main())
