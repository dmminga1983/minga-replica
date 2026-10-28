#!/usr/bin/env python3
"""stack.py - the stack and the compliance checklist for where the app will be sold.

    python3 stack.py --region ru          # Russia
    python3 stack.py --region global      # US, EU and the rest
    python3 stack.py --region both        # both, with the split that needs deciding now
    python3 stack.py --region ru --json

Reads regions.json in this folder. Every legal line carries the date it was checked: re-check
the ones marked "verify" with the official source before launch. Not legal advice.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "regions.json"), encoding="utf-8"))


def profile(region):
    if region == "both":
        return {"ru": DATA["regions"]["ru"], "global": DATA["regions"]["global"], "split": DATA["both"]}
    if region not in DATA["regions"]:
        raise SystemExit("unknown region %r: ru, global or both" % region)
    return {region: DATA["regions"][region]}


def render(p):
    out = []
    for key, r in p.items():
        if key == "split":
            continue
        out += ["", "== %s (checked %s)" % (r["name"], DATA["checked"])]
        for label, field in (("web", "web"), ("database", "database"), ("hosting", "hosting"),
                             ("auth", "auth"), ("payments", "payments"), ("email", "email"),
                             ("analytics", "analytics"), ("files", "files")):
            v = r[field]
            out.append("  %-10s %s" % (label, v if isinstance(v, str) else ", ".join(v)))
        out.append("  %-10s %s" % ("receipts", r["receipts"]))
        out.append("  stores     " + ", ".join(r["stores"]))
        for s, note in r["store_notes"].items():
            out.append("    %-10s %s" % (s, note))
        out.append("  law")
        for l in r["law"]:
            out.append("    [ ] %s: %s" % (l["id"], l["rule"]))
        out.append("  trademark checks to run")
        for t in r["trademark"]:
            out.append("    [ ] %s: %s" % (t["check"], t["where"]))
    if "split" in p:
        out += ["", "== Selling in both", "  " + p["split"]]
    out += ["", "Not legal advice. Re-check every 'verify' line before launch."]
    return "\n".join(out)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    region = "global"
    if "--region" in a:
        region = a[a.index("--region") + 1]
    p = profile(region)
    if "--json" in a:
        print(json.dumps(p, ensure_ascii=False, indent=1))
    else:
        print(render(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
