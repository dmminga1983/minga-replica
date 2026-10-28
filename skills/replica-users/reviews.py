#!/usr/bin/env python3
"""reviews.py - what the original app's users hate, ranked, with every quote linked.

    python3 reviews.py replica/reviews.csv
    python3 reviews.py replica/reviews.csv --out replica/feedback.md

reviews.csv columns: source, url, date, rating, text   (text copied exactly, Russian or English)

Rules the tool enforces, because research that cannot be checked is not research:
    every row without a URL is dropped, and the count is printed
    every quote it prints is copied from a row you gave it, with that row's URL
    themes with fewer than 3 reviews, or from one source only, are marked THIN
Low ratings and recent reviews weigh more. Requests in the users' own words ("добавьте",
"хотелось бы", "please add", "I wish") are listed separately, and low ratings that matched no
theme are listed for reading by hand: that is often where the best fix hides.
"""
import csv
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = json.load(open(os.path.join(HERE, "themes.json"), encoding="utf-8"))["themes"]
REQUEST = re.compile(r"(добав\w+|хотелось бы|было бы (здорово|удобно|круто|неплохо)|не хватает|жаль,? что нет|"
                     r"please add|i wish|would be (great|nice)|it would be|missing)", re.I)


def norm(t):
    return t.lower().replace("ё", "е")


def match(text, kws):
    t = norm(text)
    return any(re.search(r"(?<![\wЀ-ӿ])" + re.escape(norm(k)), t) for k in kws)


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(s.strip()[:10], fmt).date()
        except ValueError:
            continue
    return None


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        table = list(csv.reader(f))
    head = [h.strip().lower() for h in table[0]] if table else []
    rows = []
    for cells in table[1:]:
        if not any(c.strip() for c in cells):
            continue
        if len(cells) > len(head):
            # a review text with unquoted commas: glue the extra fields back into the last column
            cells = cells[:len(head) - 1] + [",".join(cells[len(head) - 1:])]
        rows.append({k: (cells[i] if i < len(cells) else "").strip() for i, k in enumerate(head)})
    kept, dropped = [], 0
    for r in rows:
        if not r.get("url", "").startswith(("http://", "https://")) or not r.get("text"):
            dropped += 1
            continue
        try:
            r["rating_n"] = float(r.get("rating", "").replace(",", "."))
        except ValueError:
            r["rating_n"] = None
        r["date_d"] = parse_date(r.get("date", ""))
        kept.append(r)
    return kept, dropped


def weight(r, today):
    w = 1.0
    if r["rating_n"] is not None:
        w *= {1: 2.0, 2: 1.7, 3: 1.3, 4: 1.0, 5: 0.6}.get(int(round(r["rating_n"])), 1.0)
    if r["date_d"]:
        age = (today - r["date_d"]).days
        w *= 1.3 if age <= 180 else 1.0 if age <= 540 else 0.7
    return w


def analyse(rows, today=None):
    today = today or datetime.date.today()
    out = []
    for t in THEMES:
        hits = [r for r in rows if match(r["text"], t["kw"])]
        if not hits:
            continue
        sources = sorted({r.get("source", "?") for r in hits})
        hits.sort(key=lambda r: (-weight(r, today), r.get("date", "")))
        out.append({"id": t["id"], "name": t["name"], "count": len(hits), "sources": sources,
                    "weight": round(sum(weight(r, today) for r in hits), 1),
                    "thin": len(hits) < 3 or len(sources) < 2,
                    "quotes": [{"text": r["text"][:280], "url": r["url"], "source": r.get("source", ""),
                                "rating": r.get("rating", "")} for r in hits[:3]]})
    out.sort(key=lambda t: -t["weight"])
    requests = [r for r in rows if REQUEST.search(r["text"])]
    unmatched = [r for r in rows if (r["rating_n"] or 5) <= 2 and not any(match(r["text"], t["kw"]) for t in THEMES)]
    return {"themes": out, "requests": requests, "unmatched": unmatched, "n": len(rows),
            "sources": sorted({r.get("source", "?") for r in rows})}


def render(res, dropped):
    L = ["# What users say", "",
         "%d reviews with links from %d source(s): %s." % (res["n"], len(res["sources"]), ", ".join(res["sources"]))]
    if dropped:
        L.append("%d row(s) dropped: no URL or no text." % dropped)
    L += ["", "## Themes, strongest first", ""]
    for t in res["themes"]:
        L.append("### %s: %d review(s), %d source(s)%s" % (t["name"], t["count"], len(t["sources"]),
                                                          "  THIN" if t["thin"] else ""))
        for q in t["quotes"]:
            L.append('> "%s"  (%s%s, %s)' % (q["text"], q["source"], ", " + q["rating"] + "*" if q["rating"] else "", q["url"]))
        L.append("")
    L += ["## Requests in their own words (%d)" % len(res["requests"]), ""]
    for r in res["requests"][:15]:
        L.append('- "%s" (%s)' % (r["text"][:200], r["url"]))
    L += ["", "## Low ratings no theme matched (%d): read these by hand" % len(res["unmatched"]), ""]
    for r in res["unmatched"][:15]:
        L.append('- "%s" (%s)' % (r["text"][:200], r["url"]))
    L += ["", "Quotes are research, not testimonials: never put them on your landing page."]
    return "\n".join(L)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    out = None
    if "--out" in a:
        i = a.index("--out")
        out = a[i + 1]
        del a[i:i + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        return 1
    rows, dropped = load(a[0])
    if not rows:
        print("no usable reviews: every row needs a URL and the text")
        return 1
    text = render(analyse(rows), dropped)
    if out:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        open(out, "w", encoding="utf-8").write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
