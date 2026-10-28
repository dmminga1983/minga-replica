---
name: replica-backend
description: "Build the backend of an app clone for its region: auth (VK ID, Yandex ID, Sber ID or Sign in with Apple and Google), database migrations and access rules, payments (YooKassa or CloudPayments with 54-FZ receipts, or Stripe), email, jobs and official integrations, plus a security checklist. Use for 'add login', 'set up auth', 'wire up the database', 'add payments', 'connect YooKassa', 'connect Stripe'; RU: авторизация, подключи оплату, ЮKassa, база данных, бэкенд."
---

# replica-backend

Reads `replica/architecture.md`. Writes migrations and server code, keeps `replica/backend.md`.

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## The rules

- **Official, public APIs with the user's own keys.** Never the original's private endpoints or
  OAuth client.
- **The user creates accounts and keys.** Claude never signs up for services, never types a
  password, a card or a live key. The user creates the YooKassa, CloudPayments, Stripe, Yandex
  Cloud or Supabase project and puts keys in `.env.local`. Claude writes `.env.example` with every
  variable name and no values, and checks that `.env*` is in `.gitignore`.
- **Test mode first**, with the provider's test shop or test keys and published test cards, until
  /replica-deploy.

## Auth

- **ru**: phone with an SMS code or email with a magic link, plus VK ID, Yandex ID or Sber ID with
  the user's own developer apps.
- **global**: email with verification and reset, Google, Apple. On iOS, an app that offers a
  social login must also offer an equivalent privacy-focused one such as Sign in with Apple.
- Everywhere: http-only secure cookies, sign out everywhere, roles if the recon has them (one
  function answers "can this user do this to this record"), and **account deletion that actually
  deletes** (the App Store requires it in the app).

## Database

Migrations from `architecture.md`, checked in, run by a script. Access rules on every table,
tested with a second user who must get nothing back. Backups on. **ru**: the database, the
backups and every copy of personal data in Russia.

## Payments

- **ru**: YooKassa, CloudPayments or T-Kassa through their hosted payment page or widget, never a
  hand-built card form. **Fiscal receipts under 54-FZ for every payment**, including each
  subscription renewal: turn on the provider's receipt service or connect an online cash register.
  Recurring payments only with the customer's explicit agreement and a visible way to switch them
  off. In-app purchases in RuStore through its own payments SDK.
- **global**: Stripe Checkout and the Customer Portal (or Paddle, Lemon Squeezy as merchant of
  record). Digital goods sold inside an iOS or Android app usually have to use the store's billing:
  check the store's current rules for the user's case.
- Everywhere: verify webhook signatures, store event ids, make handlers idempotent (providers
  retry), keep subscription status in your database, never trust the client, and **cancel in one
  click**.

## Email and jobs

Transactional email from the user's own domain (Unisender Go or Yandex Cloud Postbox for ru;
Resend or Postmark for global), templates written fresh. Jobs with retries and a dead-letter log,
times in UTC, shown in the user's zone.

## Security checklist

- [ ] secrets only in env vars, `.env*` ignored, nothing in client bundles
- [ ] server-side validation on every route
- [ ] authorisation on every read and write, tested with a second user
- [ ] rate limits on auth, sign up and anything that sends SMS or email
- [ ] webhooks verify signatures
- [ ] uploads: size and type limits, served from a separate domain or bucket
- [ ] no personal data in URLs or logs
- [ ] dependencies audited
- [ ] privacy policy lists every processor

Next: /replica-test.
