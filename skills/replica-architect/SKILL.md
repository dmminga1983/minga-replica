---
name: replica-architect
description: "Plan the stack, database schema and API for an app clone from the recon map, for the region it will be sold in: Russia (data stored in Russia, YooKassa or CloudPayments with 54-FZ receipts, VK ID or Yandex ID), global (Stripe or Paddle, Supabase, Vercel) or both. Use for 'plan the clone', 'what stack', 'design the database', 'write the schema', 'plan the API'; RU: архитектура, какой стек, схема базы, спроектируй API."
---

# replica-architect

Reads `replica/recon.md`, `replica/features.csv` and `replica/region.txt`. Writes
`replica/architecture.md` (template in this folder) and `replica/schema.sql`.

```bash
python3 stack.py --region ru        # or global, or both
```

No recon map: stop and run /replica-recon. Planning from memory misses half the app.

## Region

Read `replica/region.txt` (written by /replica-recon): `ru`, `global` or `both`. It decides the
stack, the stores, the laws and the trademark checks. `python3 ../replica-architect/stack.py
--region <region>` prints them. No file yet: ask where the app will be sold and write it.

## Step 1: the stack

Use what the user already knows. Otherwise take the defaults `stack.py` prints for the region,
each with one line of why. One database. No microservices: the clone needs the original's
features, not its architecture.

- **ru**: database and every store of personal data (form answers, CRM, email lists, analytics
  with user ids) on servers in Russia. Since 1 July 2025 recording or storing Russian users'
  personal data in foreign databases is prohibited, including at collection. Payments through a
  Russian provider with fiscal receipts.
- **global**: managed and cheap at zero users: Postgres on Supabase or Neon, Vercel, Stripe or a
  merchant of record (Paddle, Lemon Squeezy) if the user does not want to handle sales tax.
- **both**: decide now where Russian users' data lives (a separate deployment in Russia, or a
  separate region of the same app) and which payment provider serves which cards. Write it in the
  "Where personal data lives" section.

## Step 2: the schema

For every table: `id uuid primary key default gen_random_uuid()`, `created_at`, `updated_at`; an
owner column on everything a user owns; foreign keys with a decided `on delete`; indexes on every
foreign key and every filter or sort column; enums or check constraints for statuses; times as
`timestamptz` in UTC; money as integer minor units plus a currency column; access rules (row level
security, or one authorisation check per query in the data layer: write which). Hard constraints
the recon found (two people booking one slot) belong in the database, not the UI.

## Step 3: the API

One table per flow: `method path | does | who can call | input | output | flow`. Webhooks in and
out, background jobs with schedules. Official public APIs with the user's own keys only, never the
original's private endpoints.

## Step 4: the parts that bite

One line each where it applies: time zones and daylight saving, idempotency (webhooks arrive
twice), races, rate limits, uploads, search, realtime, offline, email deliverability, tenancy,
account deletion, data export.

## Step 5: build order

The vertical slice first (the core loop end to end, ugly), then must-haves by area, then the rest,
then the fixes from /replica-users.

Output: the files, the stack in one line, table and route counts, the three riskiest parts.
Next: /replica-design.
