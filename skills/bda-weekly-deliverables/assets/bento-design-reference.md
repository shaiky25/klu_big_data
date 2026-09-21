# Design Reference: Bento-Grid Apple Keynote Style

Source: a Canva/SlidesCarnival "Apple Keynote"-inspired template (bio/product-marketing
content, 15 slides, not reusable as-is — kept here as palette/layout inspiration only, not
wired into the build pipeline).

## Palette

| Role | Hex | Notes |
|------|-----|-------|
| Background | `#FFFFFF` | Solid white |
| Primary text | `#000000` | Solid black |
| Secondary text/shape | `#1A1A1A` | Near-black, used for dense body copy |
| Muted text | `#595959` | Captions, fine print |
| Border/muted | `#AAAAAA` | Dividers |
| Accent — lime | `#B1FF4E` | Sparingly, one highlight per bento cell |
| Accent — cyan | `#48F4FF` | Sparingly, one highlight per bento cell |
| Accent — tan/gold | `#E5BD79` | Sparingly, one highlight per bento cell |

Our own template's accent stays Apple-blue `#0071E3` — don't import these accents into the
session deck; they're here only if a specific slide needs a second accent color and blue
would be ambiguous (e.g. two side-by-side callouts that must read as distinct).

## Font

Inter (Light / Regular / SemiBold). Our deck stays on Helvetica Neue for the confirmed
Keynote/PowerPoint/Google-Slides cross-platform guarantee — don't switch fonts to match this
reference.

## Structural idea worth borrowing

"Bento grid" layout: a stat/fact slide built from many small rounded-rectangle cards of
varying size tiled across the slide (seen on the "Welcome" and "Statistics" slides — 30+
shapes each), each card holding one short fact, number, or icon. Useful as a mental model for
a dense Stat or Key Points slide that needs more than 3 items, but keep density far below this
template's example — the class deck's rule is ≤3 short phrases per Key Points slide.

## Slide inventory (for reference only, not layout indices to build from)

1. Title card
2. Section intro + numbered topic list
3. Section divider ("Introduction")
4. Bio bento grid (photo + stat cards + bullet list)
5. Company stats bento grid
6. Section divider ("About Us")
7. History/timeline bento grid
8. Full-bleed image + caption ("Gallery")
9. Section divider ("Our Products")
10. Product spec bento grid
11. Second product spec bento grid
12. Full-bleed image + one-line quote
13. Contact/closing card
14. Template credits (fonts/colors) — Canva boilerplate, not content
15. Template credits (photo attribution) — Canva boilerplate, not content
