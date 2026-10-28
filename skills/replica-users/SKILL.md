---
name: replica-users
description: "Read what the original app's real users say in public reviews (RuStore, App Store, Google Play, Otzovik, Irecommend, Telegram, Habr, VC.ru, or G2, Capterra, Trustpilot, Reddit, Hacker News), rank what they hate, what is missing and what is unsolved, and turn it into a fix plan and a positioning angle. Every quote verbatim and linked. Use for 'what do people hate about X', 'read the reviews', 'find the gap', 'how do I position this'; RU: что бесит пользователей, разбери отзывы, найди нишу, позиционирование."
---

# replica-users

A straight copy has no reason to exist. This finds the reason: what the original's users hate, in
their own words, fixed in yours.

```bash
python3 reviews.py replica/reviews.csv --out replica/feedback.md
```

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## The rules, which are not negotiable

- **Never fabricate.** No invented reviews, quotes, ratings, counts or sources. A source that cannot
  be reached is said to be unreachable. Fourteen reviews are fourteen.
- **Verbatim and linked.** Every quote copied exactly with the URL of the review or thread.
  `reviews.py` drops rows without a URL.
- **Reading, not scraping.** Review pages read the way a person reads them, rows copied into the
  sheet. Official feeds and APIs within their terms are fine (Apple's customer reviews RSS feed, the
  Hacker News Algolia API, Reddit's official API).
- **No fake reviews, ever**, for your app or against theirs. Illegal in the US (the FTC rule of 2024)
  and in many other places.
- **Reviewers are research, not testimonials.** Never on your landing page.

## Step 1: collect

100 or more reviews from at least three sources, recent first, including 3 and 4 stars ("нравится,
но..." is where the best fixes hide). Sources by region: **ru** RuStore, App Store and Google Play
(Russian storefronts), Otzovik, Irecommend, Habr and VC.ru comments, Telegram chats, Yandex Maps and
2GIS for local services; **global** App Store, Google Play, G2, Capterra, Trustpilot, Reddit
("X alternative", "switched from X"), Hacker News, the original's feature-request board. And its
changelog, so you do not "fix" what is already fixed.

Each row in `replica/reviews.csv`: source, url, date, rating, text.

## Step 2: rank

`reviews.py` sorts into themes (`themes.json`, Russian and English, edit it for the category),
weights low ratings and recent reviews, marks thin themes (under 3 reviews or one source), lists
requests in the users' words and low ratings no theme matched. Read that last list by hand.

## Step 3: three lists

What they hate, what is missing, what is unsolved (whole groups the app ignores: "не для
команд", "useless for therapists"). Each item: the problem, how many reviews, how many sources,
one or two linked quotes. Thin is labelled thin.

## Step 4: fix plan and angle

The top 5 to 8 by evidence times cheapness, each with size, the skill that does it, the evidence,
and a new row in `features.csv` with `original` set to `no`. Then three positioning lines:

```
For {who} who {hate this about the original, in plain words},
{your app} {does this instead}.
Evidence: {theme}, {n} reviews across {n} sources.
```

Recommend one. It drives /replica-brand and /replica-launch. The original's name never goes in your
app name, ads or listing; a comparison page is a question for a lawyer in your country.
