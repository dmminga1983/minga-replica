---
name: replica-design
description: "Rebuild an app's design system for a clone as tokens and component specs: colour roles, type scale, spacing, radius, shadows and every component with its states, with open icons and fonts instead of the original's assets, checked by a WCAG contrast tool. Use for 'match the design', 'design system', 'get the colours and fonts', 'make it look like X', 'design tokens'; RU: дизайн-система, повтори дизайн, токены, цвета и шрифты как у."
---

# replica-design

Reads `replica/recon.md` and `replica/screens/`. Writes `replica/design/tokens.json` (template in
this folder), `tokens.css`, the Tailwind mapping and `replica/design/components.md`.

```bash
python3 contrast.py replica/design/tokens.json
```

## What you rebuild and what you never take

Rebuild the **system**: roles, scales, patterns, how a form or a modal behaves. Never take logos,
icons, illustrations, photos, sounds (use Lucide, Phosphor, Heroicons, Tabler), licensed fonts
(use Inter, Geist, IBM Plex, Manrope, PT Sans or Golos for Cyrillic), the copy, or the brand
colour: record it as the `accent` role with a neutral placeholder, /replica-brand picks yours.
A signature colour plus a signature layout is trade dress, and it changes before launch.

Fonts for a Russian audience must have full Cyrillic. Check before choosing.

## Step 1: measure, do not guess

From the screenshots: colour **roles** (bg, surface, border, border-input, text, text-muted,
accent, on-accent, danger, success, warning: most apps use 5 to 7 greys), the type scale snapped
to a scale, spacing on a 4 or 8 base, two or three radii, shadows and motions, layout widths and
breakpoints.

## Step 2: tokens and contrast

Fill `tokens.json`, keep the role names, list every text and background pair under `pairs`, run
`contrast.py`. AA is the floor: 4.5:1 for body text, 3:1 for large text, input borders and focus
rings. Fix failures in the tokens, not per component.

## Step 3: component specs

One block per component in `components.md`: variants, sizes, every state (default, hover, active,
focus-visible, disabled, loading, error, empty), the tokens, keyboard and screen reader behaviour,
which screens use it.

## Step 4: primitives in code

Build them once, in isolation (a `/design` route or Storybook), on an accessible base if the stack
has one (Radix, shadcn/ui, React Aria). Screenshot that page: it is the design system check.

Next: /replica-build.
