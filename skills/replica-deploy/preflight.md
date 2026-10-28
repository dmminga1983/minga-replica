# Preflight: {{your app}}   region: {{ru | global | both}}

Every line is run, not assumed. Paste the output next to it.

## Gates (any failure stops the deploy)

- [ ] tests green: `npx playwright test`
- [ ] parity: all must-haves done, `parity.py` exit 0
- [ ] rebrand sweep clean: `sweep.py . --config replica/brand.json` exit 0
- [ ] store listing lints: `listing.py replica/launch/listing.json` exit 0
- [ ] production build passes
- [ ] no open S1 or S2 bugs
- [ ] secrets only in the host's env vars; `.env*` ignored; `.env.example` lists every name

## Legal pages and duties

- [ ] privacy policy lists every processor (host, database, payments, email, analytics)
- [ ] terms or public offer, refund and cancellation terms; cancelling is one click
- [ ] account deletion works in the app (App Store requires it)
- [ ] ru: personal data stored in databases in Russia (152-FZ), operator notification sent to
      Roskomnadzor, processing policy published, consent collected where needed
- [ ] ru: 54-FZ receipts on for every online payment, including each subscription charge
- [ ] ru: ads labelled and registered (erid) if you run any
- [ ] global: cookie consent for non-essential cookies (EU/UK), DPAs signed with processors
- [ ] trademark screening checks run and dated (replica/brand.md)

## Production

- [ ] separate production database, backups on, migrations run by the deploy
- [ ] payments in live mode, products and prices created by the user, webhook endpoint and its
      signing secret set, one real payment made and refunded
- [ ] OAuth redirect URIs and origins include the production domain
- [ ] sending domain verified: SPF, DKIM, DMARC
- [ ] error tracking, uptime checks, alerts to the user's email or phone
- [ ] the core flow done on the live site by Claude and on a phone by the user
