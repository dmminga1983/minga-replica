---
name: replica-test
description: "Test an app clone for bugs: a test plan from the recon flows with happy paths and edge cases (Cyrillic input, time zones, double submit, a second user's data), Playwright end-to-end specs, a click-through for the rest, and bug reports by severity until no S1 or S2 is open. Use for 'test my clone', 'find bugs', 'QA this', 'write e2e tests'; RU: протестируй, найди баги, тесты, проверь приложение."
---

# replica-test

Reads the flows in `replica/recon.md`. Writes `replica/test-plan.md`, `replica/bugs.md` and specs in
`e2e/` (templates in this folder).

## The rule

**Test your clone, never the original.** No load testing, fuzzing or scripting against the
original's servers. Using it by hand to see how it behaves is fine.

## Step 1: the plan

For every flow: the happy path; the edge cases that apply (empty input, very long input, emoji,
Cyrillic and accents, two tabs, double submit, back and refresh mid-flow, slow network, offline,
expired session, a second user's data must be invisible, time zones and daylight saving, 390px,
keyboard only, screen reader labels); the negative cases (wrong password, payment declined with the
provider's test card, permission denied, deleted record). Number them: F01-H1, F01-E3, F01-N2.

## Step 2: automate

Playwright, one spec per flow, against the local dev server with seed data, selectors by role and
label. Every spec fails on console errors and on any 5xx, and runs an axe accessibility scan on
each screen.

```bash
npm i -D @playwright/test @axe-core/playwright && npx playwright install chromium
npx playwright test
```

## Step 3: click through the rest

Emails arriving, real OAuth, payments end to end, visual glitches: a manual pass, with a browser
tool on the local clone if one is available, screenshots per step, or a checklist for the user.

## Step 4: bugs

`bugs.md` in the `bug-report.md` format. S1 data loss, security, payments, core flow blocked; S2
broken without a workaround; S3 with a workaround or visibly wrong; S4 cosmetic. Only what you
reproduced; "might be" goes to a separate list.

## Step 5: fix loop

S1 and S2 first. Failing test, fix, pass, keep the test, re-run the suite. Ship nothing with an
open S1. Next: /replica-diff.
