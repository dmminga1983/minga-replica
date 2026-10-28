import datetime
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import warnings
from contextlib import redirect_stdout, redirect_stderr

warnings.simplefilter("ignore", ResourceWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SKILLS = os.path.join(ROOT, "skills")


def load(skill, mod):
    path = os.path.join(SKILLS, skill, mod + ".py")
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("%s_%s" % (skill.replace("-", "_"), mod), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


parity = load("replica-diff", "parity")
imgdiff = load("replica-diff", "imgdiff")
reviews = load("replica-users", "reviews")
contrast = load("replica-design", "contrast")
sweep = load("replica-brand", "sweep")
listing = load("replica-launch", "listing")
stack = load("replica-architect", "stack")


def tmp(text, suffix=".txt"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def quiet(fn, *a):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = fn(*a)
    return code, out.getvalue()


class TestParity(unittest.TestCase):
    def test_weights_partial_skip_added(self):
        csv = ("feature,area,priority,original,clone,notes\n"
               "a,core,must,yes,yes,\nb,core,must,yes,partial,half done\n"
               "c,ui,should,yes,no,\nd,net,could,yes,skip,not ours\nmine,core,must,no,yes,our fix\n")
        res = parity.score(parity.load(tmp(csv, ".csv")))
        self.assertAlmostEqual(res["score"], round(100 * (3 + 1.5) / 8, 1))
        self.assertFalse(res["shippable"])
        self.assertEqual(res["added"], ["mine"])
        self.assertEqual(res["skipped"], ["d"])
        self.assertEqual(res["missing"][0][2], "b")

    def test_template_matrix_parses(self):
        res = parity.score(parity.load(os.path.join(SKILLS, "replica-recon", "features.csv")))
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["skipped"], ["Partner marketplace"])

    def test_skip_needs_reason(self):
        res = parity.score(parity.load(tmp("feature,area,priority,original,clone,notes\nx,a,must,yes,skip,\n", ".csv")))
        self.assertTrue(res["problems"])


class TestImgdiff(unittest.TestCase):
    def page(self, boxes, bg=255, w=240, h=400):
        rows = [[bg] * w for _ in range(h)]
        for x, y, bw, bh, c in boxes:
            for yy in range(y, y + bh):
                for xx in range(x, x + bw):
                    rows[yy][xx] = c
        p = tmp("", ".png")
        imgdiff.write_png(p, w, h, rows)
        return p

    def test_rebrand_is_ignored_layout_change_is_not(self):
        base = [(10, 10, 220, 30, 30), (10, 60, 100, 150, 90), (130, 60, 100, 150, 90), (10, 230, 220, 40, 30)]
        a = self.page(base)
        b = self.page([(x, y, w, h, c + 90) for x, y, w, h, c in base], bg=235)
        c = self.page([(10, 10, 220, 30, 30), (10, 60, 220, 60, 90), (10, 300, 100, 80, 30)])
        self.assertGreaterEqual(imgdiff.compare(a, b)["score"], 90)
        moved = imgdiff.compare(a, c)
        self.assertLess(moved["score"], 60)
        self.assertTrue(moved["regions"])
        self.assertLess(imgdiff.compare(a, b, "pixel")["score"], 100)

    def test_rejects_non_png(self):
        with self.assertRaises(imgdiff.PngError):
            imgdiff.read_png(tmp("not a png"))

    def test_diff_picture_written(self):
        a = self.page([(10, 10, 50, 50, 0)])
        out = tempfile.mktemp(suffix=".png")
        imgdiff.compare(a, a, out=out)
        w, h, _ = imgdiff.read_png(out)
        self.assertEqual(w, imgdiff.WIDTH)


class TestReviews(unittest.TestCase):
    def test_links_required_and_themes(self):
        today = datetime.date(2026, 10, 1)
        csv = ("source,url,date,rating,text\n"
               "RuStore,https://r/1,2026-09-01,1,Приложение постоянно вылетает и дорогая подписка\n"
               "Otzovik,https://o/2,2026-08-01,2,Вылетает при оплате, поддержка не отвечает\n"
               "App Store,https://a/3,2025-01-01,1,Crashes every time, refund please\n"
               "Telegram,,2026-09-01,1,Без ссылки, должно выпасть\n"
               "RuStore,https://r/5,2026-09-10,4,Хорошо, но хотелось бы тёмную тему\n"
               "RuStore,https://r/6,2026-09-11,1,Ужасно, ужасно, ужасно\n")
        rows, dropped = reviews.load(tmp(csv, ".csv"))
        self.assertEqual(dropped, 1)
        res = reviews.analyse(rows, today)
        names = [t["id"] for t in res["themes"]]
        self.assertEqual(names[0], "bugs")
        bugs = res["themes"][0]
        self.assertEqual(bugs["count"], 3)
        self.assertFalse(bugs["thin"])
        for q in bugs["quotes"]:
            self.assertTrue(q["url"].startswith("https://"))
        self.assertTrue(any("тёмную" in r["text"] for r in res["requests"]))
        self.assertTrue(any("Ужасно" in r["text"] for r in res["unmatched"]))
        self.assertTrue(next(t for t in res["themes"] if t["id"] == "support")["thin"])


class TestContrast(unittest.TestCase):
    def test_known_ratios(self):
        self.assertEqual(contrast.ratio("#000000", "#ffffff"), 21.0)
        self.assertEqual(contrast.ratio("#fff", "#fff"), 1.0)

    def test_template_tokens_pass(self):
        res = contrast.check(json.load(open(os.path.join(SKILLS, "replica-design", "tokens.json"))))
        self.assertTrue(all(r["ok"] for r in res), [r for r in res if not r["ok"]])


class TestSweep(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write(self, rel, text):
        p = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)

    def test_finds_identifiers_translit_domains_colors(self):
        self.write("src/embed.tsx", "export const CalendlyEmbed = () => null")
        self.write("src/ru.json", '{"title": "Аналог Календли"}')
        self.write("src/a.css", ".x{color:#006BFF} .y{color: rgb(0, 107, 255)}")
        self.write("src/b.ts", "fetch('https://calendly.com/x')")
        self.write("public/calendly-logo.svg", "<svg/>")
        self.write("replica/recon.md", "Calendly is the original")
        self.write("node_modules/x/index.js", "Calendly")
        hits = sweep.sweep(self.d, sweep.build_patterns(["Calendly"], ["calendly.com"], ["#006bff"]))
        files = {h[0].replace("\\", "/") for h in hits}
        self.assertIn("src/embed.tsx", files)
        self.assertIn("src/ru.json", files)
        self.assertIn("src/a.css", files)
        self.assertIn("public/calendly-logo.svg", files)
        self.assertNotIn("replica/recon.md", files)
        self.assertFalse(any(f.startswith("node_modules") for f in files))
        self.assertEqual(sum(1 for h in hits if h[0].endswith("a.css")), 2)

    def test_clean_exit(self):
        self.write("src/a.ts", "const x = 1")
        code, _ = quiet(sweep.main, [self.d, "--avoid", "Calendly"])
        self.assertEqual(code, 0)


class TestListing(unittest.TestCase):
    def test_example_is_clean(self):
        doc = json.load(open(os.path.join(SKILLS, "replica-launch", "listing.example.json"), encoding="utf-8"))
        errs = [r for r in listing.lint(doc) if r[0] == "ERROR"]
        self.assertEqual(errs, [])

    def test_limits_claims_avoid(self):
        doc = {"avoid": ["Calendly"],
               "appstore": {"name": "Лучший календарь Calendly для всех на свете", "description": "x",
                            "keywords": "календарь, запись,календарь"},
               "googleplay": {"title": "Booking \U0001F680", "full_description": "x"},
               "rustore": {"name": "Запись" * 9, "full_description": "x"}}
        res = listing.lint(doc)
        msgs = " | ".join("%s %s %s" % (r[1], r[2], r[3]) for r in res)
        self.assertIn("appstore name", msgs)
        self.assertIn("limit is 30", msgs)
        self.assertIn("original's name", msgs)
        self.assertIn("ranking or price claim", msgs)
        self.assertIn("spaces after commas", msgs)
        self.assertIn("repeated keywords", msgs)
        self.assertIn("emoji in the title", msgs)
        self.assertIn("limit is 50", msgs)

    def test_cyrillic_counts_as_one(self):
        self.assertEqual(listing.length("Ёлка"), 4)

    def test_store_limits(self):
        s = listing.STORES
        self.assertEqual(s["rustore"]["fields"], {"name": 50, "short_description": 80, "full_description": 4000})
        self.assertEqual(s["googleplay"]["fields"]["title"], 30)
        self.assertEqual(s["appstore"]["fields"]["keywords"], 100)


class TestStack(unittest.TestCase):
    def test_regions(self):
        ru = stack.profile("ru")["ru"]
        self.assertIn("rustore", ru["stores"])
        self.assertTrue(any(l["id"] == "152-fz-localisation" for l in ru["law"]))
        self.assertTrue(any("YooKassa" in p for p in ru["payments"]))
        both = stack.profile("both")
        self.assertIn("split", both)
        code, out = quiet(stack.main, ["--region", "both"])
        self.assertIn("Not legal advice", out)
        self.assertIn("Google Play", stack.render(stack.profile("ru")).replace("googleplay", "Google Play"))


class TestRepo(unittest.TestCase):
    def test_frontmatter(self):
        names = sorted(os.listdir(SKILLS))
        self.assertEqual(len(names), 11)
        for n in names:
            text = open(os.path.join(SKILLS, n, "SKILL.md"), encoding="utf-8").read()
            m = re.match(r'---\nname: (.+)\ndescription: "(.+?)"\n---\n', text, re.S)
            self.assertTrue(m, n)
            self.assertEqual(m.group(1), n)
            self.assertLessEqual(len(m.group(2)), 1024)

    def test_skill_files_referenced_exist(self):
        for n in os.listdir(SKILLS):
            text = open(os.path.join(SKILLS, n, "SKILL.md"), encoding="utf-8").read()
            for f in re.findall(r"`([\w.-]+\.(?:py|json|md|csv|ts))`", text):
                if f in ("SKILL.md",) or "/" in f:
                    continue
                here = os.path.exists(os.path.join(SKILLS, n, f))
                anywhere = any(os.path.exists(os.path.join(SKILLS, d, f)) for d in os.listdir(SKILLS))
                user_file = f in ("recon.md", "features.csv", "architecture.md", "schema.sql", "backend.md",
                                  "test-plan.md", "bugs.md", "parity.md", "reviews.csv", "feedback.md",
                                  "fixes.md", "brand.md", "brand.json", "landing.md", "pricing.md",
                                  "listing.json", "launch-plan.md", "deploy.md", "components.md",
                                  "tokens.css", "build-log.md", "region.txt", "S07.png", "S07.json")
                self.assertTrue(here or anywhere or user_file, "%s mentions %s" % (n, f))

    def test_no_long_dashes(self):
        for base, _, files in os.walk(ROOT):
            if ".git" in base:
                continue
            for f in files:
                if f.endswith((".md", ".json", ".txt", ".py", ".csv", ".ts")):
                    self.assertNotIn(chr(0x2014), open(os.path.join(base, f), encoding="utf-8").read(),
                                     os.path.join(base, f))

    def test_manifests(self):
        p = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json")))
        self.assertEqual(p["name"], "minga-replica")
        json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))


if __name__ == "__main__":
    unittest.main()
