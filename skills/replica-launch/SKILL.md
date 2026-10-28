---
name: replica-launch
description: "Write the launch of an app clone: the landing page built on the positioning angle, pricing set against the original's public prices and its users' complaints, and the store listings for App Store, Google Play and RuStore linted against each store's limits and copycat rules. Use for 'landing page', 'pricing', 'how much should I charge', 'App Store listing', 'RuStore listing', 'launch plan'; RU: лендинг, цены, сколько брать, описание для RuStore, описание для App Store, план запуска."
---

# replica-launch

Reads `replica/fixes.md`, `replica/brand.md`, `replica/brand.json`. Writes `replica/launch/`:
`landing.md`, `pricing.md`, `listing.json`, `launch-plan.md`.

```bash
python3 listing.py replica/launch/listing.json          # all stores in the file
python3 listing.py replica/launch/listing.json --store rustore
```

Start from `listing.example.json`. Limits live in `stores.json` (checked October 2026).

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## The rules

- **No fake proof.** No invented testimonials, user counts, ratings, press logos or "trusted by".
  An empty proof section beats a fake one. Real beta users, with permission, are fine.
- **No reviewer quotes as testimonials.**
- **The original's name stays out** of your name, listing, keywords and ads.

## Landing page

Hero (the angle as a headline, one line, one button, a real screenshot), the problem (the top two
hate themes, paraphrased), how it works (three steps), features led by the fixes (parity is the
price of entry), pricing, FAQ (the real objections, including importing from the old tool), the
final call to action. In the brand voice, in every language you sell in, contrast-checked.

## Pricing

The original's public pricing and two or three alternatives in one table, with URLs and the date
read; what reviewers said about price, with counts; the model (free plan or trial, flat or per seat,
monthly and annual); three tiers at most, named by who they are for; one-click cancel and clear
renewal emails. Currency and tax by region: roubles with 54-FZ receipts for **ru**; for **global**,
sales tax and VAT handled by you or by a merchant of record.

## Store listings

Fill `listing.json` for every store you ship to, then `listing.py`: App Store (name 30, subtitle 30,
promotional text 170, keywords 100, description 4,000), Google Play (title 30, short 80, full
4,000), RuStore (name 50, short 80, full 4,000), with ranking and price claims, emoji, caps, wasted
keywords and the original's name flagged. Locales lint the same way.

Copycat rules are what review checks: Apple's guideline 4.1, Google Play's impersonation policy,
RuStore moderation. Make your fixes and your brand visible in the first screenshots and the first
lines of the description. Also prepare current screenshot sizes from each console, privacy labels
and Google's data safety form, privacy policy and support URLs, age rating, review notes with a demo
account.

**ru, paid features:** Google Play does not pay out to Russian bank accounts since 26 December 2024.
Ship the free app there if you like; sell through RuStore's payments or the web.

## Launch plan

Waitlist or beta before launch, analytics and error tracking live, where the original's unhappy
users talk (the threads and chats from the research), a launch post that leads with the fix
(Product Hunt or Hacker News for global; VC.ru, Habr and Telegram channels for ru), and the first
ten users talked to by hand.

Next: /replica-deploy.
