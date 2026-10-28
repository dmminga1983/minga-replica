---
name: replica-build
description: "Rebuild an app clone screen by screen from the recon map: the shell first, then the core flow as a vertical slice, then every screen with all its states, ticking off the feature matrix, every line written fresh. Use for 'build the clone', 'build screen S07', 'start building', 'implement this page'; RU: собери клон, сверстай экран, начинай разработку, сделай этот экран."
---

# replica-build

Reads `replica/recon.md`, `replica/architecture.md`, `replica/design/`. Updates the `clone` column
of `replica/features.csv` and keeps `replica/build-log.md`.

## The rules

- **Clean room.** Every line is written here from the recon map and the specs. Never paste the
  original's HTML, CSS, JavaScript, SVGs or images, never load anything from its domain or CDN,
  never "view source and adapt".
- **Your words.** Every label, button, empty state and email written fresh. Matching what a button
  does is parity; matching its sentence is copying. Russian interface text written by a native
  speaker's standard, not translated word for word.
- **Tokens only.** No raw hex or pixel values in components.

## Step 1: the shell

Routing for every screen (stubs are fine), the layout, tokens wired in, the primitives, seed data
with realistic fake records (no real people). Commit.

## Step 2: the vertical slice

The core loop end to end before anything else. Ugly is fine, working is the point. If the backend
is not there yet, a fake data layer with the same function signatures, so swapping it changes no
screen code.

## Step 3: screen by screen

For each screen in the order of `architecture.md`: read its recon row; look at the reference for
layout and hierarchy, not pixels; build it with the primitives; every state (empty, loading,
filled, error, no permission, a 60-character name, 390px wide); semantic HTML, labels, keyboard,
visible focus, alt text; update `features.csv`; screenshot at the reference viewport into
`replica/clone-screens/S07.png`; one commit per screen.

## Definition of done, per screen

- [ ] every state from the recon map, plus empty, error, loading
- [ ] works at 390px and 1440px
- [ ] the flow completes with the keyboard only
- [ ] no console errors
- [ ] no copy borrowed from the original
- [ ] features.csv updated, screenshot saved

When a feature is bigger than it looked, say so in the log and in the chat. Never quietly ship
half of it. Stuck on behaviour: use the original as a user (help article, walkthrough, the user's
own account), never its code or network calls.

Next: /replica-backend if the data is still fake, else /replica-test.
