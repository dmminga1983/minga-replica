---
name: replica-brand
description: "Name and rebrand an app clone so it is the user's own: name candidates with trademark checks to run (Rospatent/FIPS, USPTO, EUIPO, WIPO), domains, store and handle checks, a new palette checked for contrast, a logo brief, a voice, and a sweep tool that finds anything of the original left in the code, including Russian transliterations. Use for 'name my app', 'rebrand', 'make it mine', 'logo brief', 'check for leftovers'; RU: название для приложения, ребрендинг, сделать своим, проверка товарного знака."
---

# replica-brand

Nothing launches under the original's identity. This is the line between a clone and your app.

```bash
python3 sweep.py . --config replica/brand.json
```

Writes `replica/brand.md` and `replica/brand.json` (`avoid`, `domains`, `colors`), used by
`sweep.py`, `listing.py` and /replica-deploy.

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## Step 1: the name

From the angle in `replica/fixes.md`, twenty candidates across styles (descriptive, compound,
invented, metaphor, verb), cut to five: not confusingly similar to the original in sound, look or
meaning (the test trademark offices use: no puns on their name, no one-letter twin); short and
spellable after hearing it once; no awkward meaning in Russian or English; supports the angle.
For **ru** and **both**: it reads well in Cyrillic and in Latin, and the Latin spelling is the one
for the domain.

## Step 2: checks, run and dated, never assumed

Per candidate, one row per check, marked **to run** or with the result and the date it was run.
Never write "available" for a check nobody ran.

| check | where |
| --- | --- |
| Russia trademark | FIPS open registers (fips.ru), classes 9 and 42 |
| US trademark | tmsearch.uspto.gov |
| EU trademark | EUIPO eSearch or TMview |
| worldwide | WIPO Global Brand Database |
| domain | the registrar's search (.ru, .рф, .com, .app) |
| stores | the exact name in RuStore, App Store, Google Play |
| handles | Telegram, VK, X, Instagram, TikTok, GitHub |
| the web | "name + category", in both languages |

These are screening checks, not clearance. Before money goes into the name, a trademark lawyer
runs a proper search.

## Step 3: palette

A primary hue from a different family than the original's, written into the same token roles,
then `../replica-design/contrast.py`: zero AA failures. The original's colours go into
`brand.json` so the sweep catches survivors.

## Step 4: logo brief

The idea in a line, the mark type, works at 16px and as a 1024px app icon, deliverables (SVG,
iOS icon 1024x1024 with no transparency, Android adaptive icon, favicon set, 1200x630 share image),
and it **must not resemble the original's mark**: put both side by side and check.

## Step 5: voice

Three words with what each does not mean ("direct, not blunt"), five do and don't pairs, then the
ten most-seen strings rewritten in that voice, in every language the app ships.

## Step 6: the sweep

Replace every placeholder, then `sweep.py`. It searches contents and file names for the original's
names (also inside identifiers and in Cyrillic transliteration), domains and colours, skipping
`node_modules`, build output and `replica/`. Exit 1 means something is left. Then by eye: favicon,
titles, email templates, share image, app icon.

Next: /replica-launch.
