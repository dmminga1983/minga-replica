---
name: replica-recon
description: "Reverse-engineer any app into a recon map: screen inventory, user flows, components, inferred data model and a feature matrix, from public pages, store listings, help docs and the user's own account, plus the region it will be sold in. The first step of minga-replica. Use for 'clone this app', 'reverse engineer X', 'map out X', 'build my own version of X'; RU: клон приложения, разбери приложение, сделать аналог, как устроено приложение."
---

# replica-recon

Everything else in the pack builds on what this writes. A bad recon map means a bad clone.

Output in the user's project:

```
replica/region.txt      ru, global or both
replica/recon.md        the recon map (template: recon-map.md in this folder)
replica/features.csv    the feature matrix (template: features.csv in this folder)
replica/screens/        reference screenshots of the original. Never shipped.
```

## The rules, before anything else

This rebuilds **functionality and UX patterns**, clean-room style: what the app does and how a
user moves through it. Never what the app owns.

- **Public sources and the user's own account only.** Never another person's account, never a
  password, never past a paywall or a login by any trick.
- **Reading, not scraping.** No crawlers, bulk downloads or loops. With a browser tool, read at
  human speed with the user present.
- **No source code, no private APIs.** Do not save or read the app's JavaScript bundles, decompile
  its binary or log its network calls to copy endpoints. Public API docs are fine.
- **Check the terms.** If the user's account terms forbid using it to build a competitor, say so and
  work from public sources only.
- **Screenshots are reference**: for layout comparison, never in the clone.

## Step 1: scope, three questions

1. **Which app and platform**: web, iOS, Android.
2. **Which slice.** "All of Notion" is not a project; "pages, blocks and sharing" is. Default to
   the core loop: the one flow users pay for.
3. **Where it will be sold**: Russia (`ru`), the rest of the world (`global`), or both. Write
   `replica/region.txt`. Selling in Russia changes the stack (personal data stored in Russia),
   the payments (54-FZ receipts) and the stores (RuStore; Google Play does not pay Russian
   accounts). Decide it now, not at deploy.

## Step 2: sources table, a URL on every row

Help center and docs (the fullest feature list there is), pricing page (which features matter:
they gate them), changelog, store listings (App Store, Google Play, RuStore), public walkthrough
videos, marketing site, public API docs, the user's own account.

## Step 3 onwards

- **Screens** S01, S02... with route, purpose, components and every state seen: empty, loading,
  filled, error, no permission, mobile. An empty state not recorded is an empty state not built.
- **Flows** F01... as screen sequences with edge cases. Count the clicks on the happy path: the
  number to beat.
- **Components**: name, variants, states, which screens use it.
- **Inferred data model**: entities and fields, each with its evidence and a confidence. Guesses
  are marked as guesses.
- **Feature matrix** `features.csv`: feature, area, priority (must/should/could), original, clone
  (starts at `no`), notes.
- **Out of scope**, honestly, as `skip` rows with a reason: licensed content, the network and its
  users, data the app owns, partner deals, regulated licences.
- **Size**: S a weekend, M weeks, L a quarter, XL rescope. No promise of a perfect clone.

## Output

The files above and five lines: the core loop, screen and flow counts, the three hardest parts,
what is out of scope, the region. Next: /replica-architect.
