# minga-replica

**Eleven Claude skills that rebuild any app clean-room style and make it yours: recon, architecture, design, build, backend, tests, parity scoring, what the original's users hate, a rebrand, the launch and the deploy. With region profiles for Russia and for the rest of the world, and listings for App Store, Google Play and RuStore.**

Part of the [Minga](https://github.com/dmminga1983/minga) ecosystem. One skill reverse-engineers the app you want to rebuild, one rebuilds it, one tests it, and one reads its real reviews and turns the complaints into the reason your version exists. In between: the stack for where you sell, the design system, auth and payments, a parity score, a new name and brand, the landing page and store listings, and a preflight gate before anything goes live. Free, MIT, no API key, nothing to connect.

**It rebuilds what an app does, never what it owns.** Features and flows, written fresh. Not its code, logo, copy or content. The skills enforce it.

[Русская версия →](README.ru.md)

## The eleven

| command | what it does |
| --- | --- |
| `/replica-recon` | Screens, flows, components, data model and a feature matrix from public sources and your own account. Sets the region: `ru`, `global` or `both`. |
| `/replica-architect` | Stack, schema and API for the region. `stack.py` prints the defaults and the legal checklist. |
| `/replica-design` | The design system as tokens and component specs, with open icons and Cyrillic-ready fonts. WCAG contrast checked. |
| `/replica-build` | Screen by screen from the recon map, every state, every line fresh. |
| `/replica-backend` | Auth, database, payments, email, jobs, integrations, a security checklist. |
| `/replica-test` | A test plan from the flows, Playwright specs, bug reports by severity. |
| `/replica-diff` | Parity score from the feature matrix and a screenshot layout diff that ignores colour. |
| `/replica-users` | Real reviews ranked into what users hate, what is missing, what is unsolved. Every quote linked. |
| `/replica-brand` | Name, trademark checks to run, palette, logo brief, voice, and a sweep for anything of the original left. |
| `/replica-launch` | Landing page, pricing, and store listings linted for App Store, Google Play and RuStore. |
| `/replica-deploy` | Preflight gate, production services, DNS, monitoring, mobile builds. Ships only on your go. |

## Regions

`replica/region.txt` decides the stack, stores, laws and checks. `python3 skills/replica-architect/stack.py --region ru|global|both` prints them.

| | Russia (`ru`) | Global (`global`) |
| --- | --- | --- |
| data | personal data recorded and stored in databases in Russia (152-FZ, strict since 1 July 2025) | GDPR in the EU, state privacy laws in the US |
| hosting | Yandex Cloud, Selectel, VK Cloud, Timeweb Cloud | Vercel, Netlify, Fly.io, Render |
| auth | phone or email, VK ID, Yandex ID, Sber ID | email, Google, Sign in with Apple |
| payments | YooKassa, CloudPayments, T-Kassa, Robokassa, with 54-FZ receipts | Stripe, Paddle, Lemon Squeezy |
| stores | RuStore; App Store; Google Play free only (no payouts to Russian bank accounts since 26 December 2024) | App Store, Google Play |
| trademark | FIPS open registers, WIPO | USPTO, EUIPO, WIPO |
| reviews | RuStore, Otzovik, Irecommend, Habr, VC.ru, Telegram, 2GIS | G2, Capterra, Trustpilot, Reddit, Hacker News |

`both` means deciding early where Russian users' data lives and which provider takes which cards. Every legal line in `regions.json` carries the date it was checked.

## Install

**Claude Code**, as a plugin:

```
/plugin marketplace add dmminga1983/minga-replica
/plugin install minga-replica@minga-replica
```

Or copy the folders for plain `/replica-recon` and so on:

```bash
git clone https://github.com/dmminga1983/minga-replica.git
cp -r minga-replica/skills/replica-* ~/.claude/skills/
```

Run them in order; each reads what the last one wrote in `replica/` in your project:

```
recon -> architect -> design -> build -> backend -> test -> diff -> users -> brand -> launch -> deploy
```

Any one runs alone too: `/replica-users` on an app you are only thinking about cloning tells you whether you should.

## The tools

Standard-library Python, no network, Python 3.8 or newer.

```bash
python3 skills/replica-architect/stack.py --region both
python3 skills/replica-diff/parity.py replica/features.csv
python3 skills/replica-diff/imgdiff.py original.png clone.png --out diff.png
python3 skills/replica-users/reviews.py replica/reviews.csv --out replica/feedback.md
python3 skills/replica-design/contrast.py replica/design/tokens.json
python3 skills/replica-brand/sweep.py . --config replica/brand.json
python3 skills/replica-launch/listing.py replica/launch/listing.json
```

- **`imgdiff.py`** decodes PNGs with no libraries, compares edge maps on a grid, and ignores colour, so the rebrand does not count against you.
- **`parity.py`** weights must, should and could, counts partial as half, never scores what you skipped on purpose or added yourself, and says "not shippable" while a must-have is missing.
- **`reviews.py`** drops every review without a link, quotes only rows you gave it, marks themes from under three reviews or one source as thin, and reads Russian and English.
- **`sweep.py`** finds the original's name inside identifiers, in file names and in Cyrillic transliteration, plus its domains and colours, and blocks the deploy until clean.
- **`listing.py`** checks App Store, Google Play and RuStore limits, ranking claims, emoji, wasted keywords and the original's name in every locale.

```bash
python3 -m unittest discover -s tests -v
```

## The fine print

- **Clean room.** It studies what the app does and how people move through it, then writes everything fresh. Never the target's source code, private APIs, assets, logos, trademarks or copy.
- **Only what you may read.** Public pages and your own account. Never someone else's account, never past a login or a paywall, never against a site's terms.
- **Always rebranded before launch.** `/replica-deploy` will not ship until the sweep is clean.
- **"Any app" means the features and the flow**, not the content, network or licences an app owns.
- **No guarantee of a perfect clone.** `/replica-recon` sizes it honestly and `/replica-diff` gives a real number.
- **Nothing is made up.** No invented reviews, quotes, users or numbers, and no fake testimonials on your landing page.
- **You hold the keys.** Claude never creates accounts, enters cards or passwords, or pastes live keys. It writes `.env.example`; you fill `.env.local`.
- **Not legal advice.** Run the trademark checks, read the terms of what you use, and talk to a lawyer before launch when money is at stake. Laws and store rules change: `regions.json` and `stores.json` carry their check dates.

## Credit

Made by [dmminga1983](https://github.com/dmminga1983). Inspired by Jake Schincariol's [replica-skill](https://github.com/Jakeschincariol/replica-skill); the tools, region profiles and skills here are written from scratch.

## License

MIT.
