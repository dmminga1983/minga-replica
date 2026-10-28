# Architecture: {{your app}}

Region: {{ru | global | both}} (run `python3 stack.py --region <region>`)

## Stack

| layer | choice | why |
| --- | --- | --- |
| web | | |
| mobile | | |
| database | | |
| auth | | |
| payments | | |
| receipts (ru) | | |
| email | | |
| jobs | | |
| files | | |
| hosting | | |
| analytics | | |

## Where personal data lives

{{database location, and for "both": how Russian users' data stays in Russia}}

## Schema

See `replica/schema.sql`. Tables: {{n}}. Hard constraints: {{e.g. no double booking}}.

## API

| method path | does | who can call | input | output | flow |
| --- | --- | --- | --- | --- | --- |

Webhooks in and out, background jobs with their schedule.

## The parts that bite

{{time zones, idempotency, races, rate limits, uploads, search, realtime, offline, email
deliverability, multi-tenancy, deletion}}

## Build order

1. Vertical slice: {{the core loop, end to end}}
2. Must-haves by area
3. Should-haves, then could-haves
4. Fixes from replica-users
