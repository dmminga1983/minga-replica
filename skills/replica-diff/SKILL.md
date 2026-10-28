---
name: replica-diff
description: "Compare an app clone with the original: a feature parity score from the matrix (must, should, could weighted, partial counted as half, your own additions excluded) and a screenshot layout diff that ignores colour, so the rebrand does not count against you. Use for 'how close is my clone', 'compare with the original', 'what's missing', 'parity check', 'is it ready'; RU: насколько похоже, сравни с оригиналом, чего не хватает, готов ли клон."
---

# replica-diff

```bash
python3 parity.py replica/features.csv
python3 imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --out replica/diffs/S07.png
python3 imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --json > replica/diffs/S07.json
python3 parity.py replica/features.csv --visual "replica/diffs/*.json" --markdown > replica/parity.md
```

## What parity means

**It does the same job, not that it looks the same.** The feature score is the number that matters.
The layout score checks structure, because that is what makes a switcher feel at home, and it
ignores colour on purpose. Never chase pixel parity: the exact look is the original's trade dress.

## Feature parity

Every `clone` cell is yes, partial (with a note), no, or skip (with a reason). Weights must 3,
should 2, could 1, partial half. Skip rows and rows the original does not have are left out. Any
must-have missing means not shippable.

## Layout diff

Two screenshots at the same viewport (1440x900, 390x844), in the same state, with the same shape of
data. Large retina screenshots take a while: the decoder is pure Python. `--mode pixel` is for the
clone against itself last week.

## Behaviour diff

Walk each flow in both: clicks to finish, error handling, what is remembered, which emails arrive.
Fewer clicks than the original is a win. Each difference: flow, original does, clone does, fix or
keep.

## Verdict

Not shippable (a must-have missing or an open S1), shippable (all musts, 80+, no open S1 or S2),
or better than the original (shippable plus fixes from /replica-users: the goal, because a straight
copy has no reason to exist). Honest numbers: 62% is 62%.
