---
name: replica-deploy
description: "Ship an app clone live on the user's own domain after a preflight gate: tests green, must-haves done, rebrand sweep clean, listings linted, legal duties for the region (152-FZ data in Russia and Roskomnadzor notice, 54-FZ receipts, or GDPR and cookie consent), production database and keys, DNS for the domain and email, live payments, monitoring, and mobile builds to TestFlight, Google Play and RuStore. Use for 'deploy it', 'ship it', 'put it live', 'connect my domain', 'publish the app'; RU: задеплой, запусти в прод, подключи домен, опубликуй в RuStore."
---

# replica-deploy

Reads everything in `replica/`. Writes `replica/deploy.md` from `preflight.md` in this folder.

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## The rules

- **Nothing goes live without the user's go.** Show the preflight results and ask.
- **The user buys and signs in.** Claude never buys a domain, enters a card, types a password or
  pastes a live key. Claude writes the exact DNS records, env var names and commands; the user does
  the account steps.
- **Not until it is rebranded**: the sweep must be clean.

## Step 1: preflight

Run every gate in `preflight.md` and paste the output into `deploy.md`:

```bash
npx playwright test
python3 ~/.claude/skills/replica-diff/parity.py replica/features.csv
python3 ~/.claude/skills/replica-brand/sweep.py . --config replica/brand.json
python3 ~/.claude/skills/replica-launch/listing.py replica/launch/listing.json
npm run build
```

(Paths depend on where the pack is installed.) Then the legal duties for the region in
`preflight.md`. Any failure stops the deploy: say which and why.

## Step 2: production services

A separate production database with backups, migrations run by the deploy. Env vars in the host,
matching `.env.example`, live keys only there. Payments in live mode: products and prices recreated
by the user, the production webhook and its secret, one real payment made and refunded, and for
**ru** the receipt service confirmed by finding the receipt of that test payment. OAuth redirect
URIs and origins with the production domain. The email sending domain verified.

## Step 3: host and domain

**ru**: Yandex Cloud, Selectel, VK Cloud or Timeweb Cloud, so the app and its personal data run in
Russia. **global**: Vercel for Next.js, otherwise Netlify, Fly or Render. The repo connected so main
deploys and pull requests get previews.

DNS after the user buys the domain: the host's A or ALIAS record for the apex and CNAME for www (the
host shows the exact values), any verification TXT record, then email DNS from the provider: SPF,
DKIM, and DMARC starting at `v=DMARC1; p=none; rua=mailto:...`, tightened to `quarantine` once the
reports are clean. One canonical host, the other redirected, HTTPS checked.

## Step 4: watch it

Error tracking, uptime checks on the home page and the core flow's API, logs, privacy-friendly
analytics (Yandex Metrica for ru, Plausible or PostHog for global), an alert to the user. Do the
core flow on the live site yourself and ask the user to do it on their phone.

## Step 5: mobile

Expo: `eas build`, then TestFlight and Google Play internal testing; RuStore through its developer
console (the APK or AAB, then moderation). Native: Xcode archive to App Store Connect, a Gradle
bundle to Play Console and RuStore. The user owns every developer account. Beta first, then review
with the listings from /replica-launch.

Output: `deploy.md` with every check and result, the live URL, the DNS records set, what to watch in
the first week.
