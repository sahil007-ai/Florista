# 07 — Styling & Branding

Everything visual on the site comes from `css/style.css`. This chapter
explains the design system and how to change it without breaking pages.

---

## The brand palette

All colours are CSS custom properties (variables) declared at the top of
`css/style.css` in the `:root` block:

```css
:root {
  /* Richer Pastel Palette */
  --color-primary:        #f5d5e4;   /* light pink — backgrounds, soft accents */
  --color-primary-dark:   #c97ea0;   /* brand pink — buttons, headings, links */
  --color-primary-light:  #fdeef5;   /* very light pink — hover states */
  --color-secondary:      #d4edd9;   /* soft mint — MOQ chip background */
  --color-accent:         #b8d4f0;   /* light blue — used sparingly */
  --color-dark:           #18202e;   /* near-black — body text, headings */
  --color-gray:           #5a6477;   /* muted gray — secondary text */
  --color-light:          #faf9fb;   /* page background base */
  --color-white:          #ffffff;
  ...
}
```

> **The single biggest leverage point for a rebrand:** change these
> seven colour values, and the entire site shifts to the new palette.

### Semantic colour usage

| Variable | Used for |
|----------|----------|
| `--color-primary-dark` | Primary buttons, headings (occasional accents), active nav, focus rings |
| `--color-primary` | Card borders, soft backgrounds |
| `--color-primary-light` | Hover states, badge backgrounds, the AI callout gradient |
| `--color-secondary` | The mint MOQ chip on every product card |
| `--color-dark` | Body text, h1/h2 |
| `--color-gray` | Captions, descriptions, secondary text |

If you change `--color-primary-dark`, every CTA and link colour shifts
together. That's the design intent — keep it that way.

### What's NOT a CSS variable

A few colours are hardcoded because they're semantic, not brand:

| Hardcoded | Used for | Where |
|-----------|----------|-------|
| `#25D366` | WhatsApp green | `.btn-whatsapp`, the floating WA button |
| `#128C7E` | WhatsApp green hover | same |
| `#1f6b3a` | MOQ chip text | `css/style.css` |
| `#e74c3c` | (Sale tag — added in Ch 05) | (proposed) |
| `#f5b948` | Star ratings on testimonials | `index.html` inline style |
| `#e05c5c` | Form-error red border | `js/main.js` |

These shouldn't change with a rebrand.

---

## Typography

Two fonts, both loaded from Google Fonts:

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif: 'Playfair Display', serif;
}
```

| Use | Font | Defined in |
|-----|------|-----------|
| Body text, navigation, buttons | Inter | `--font-sans` |
| Headings (h1–h6), big numbers (stats, prices) | Playfair Display (italic + bold variants) | `--font-serif` |

The `<link>` to Google Fonts lives in every page's `<head>`:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
```

If you change fonts:
1. Update the Google Fonts URL in **every** page's `<head>` (root pages
   directly; per-product / per-use-case pages via the generator templates).
2. Update `--font-sans` and `--font-serif` in `css/style.css`.
3. Sanity-check: pages might shift slightly in size — Inter and Playfair
   are well-balanced; replacements may need to be tested for vertical
   rhythm.

---

## Layout tokens

Other variables in `:root`:

```css
--max-width: 1200px;        /* the .container max width */
--border-radius: 18px;      /* the standard card / button corner */
--transition: all 0.32s cubic-bezier(0.25, 0.8, 0.25, 1);   /* the standard ease */
```

If you want a tighter site:
```css
--max-width: 1100px;
--border-radius: 12px;
```

…and every container, card, and button updates together.

### Glassmorphism tokens

```css
--glass-bg: rgba(255, 255, 255, 0.72);
--glass-border: rgba(255, 255, 255, 0.5);
--glass-shadow: 0 8px 32px rgba(80, 30, 60, 0.08);
```

Used by `.glass-card`, the testimonials, the cat sidebar, the size guide,
the toolbar, the FAQ items, and most of the visible "frosted" surfaces.
If your design moves away from glassmorphism, lower the `0.72` alpha or
swap `--glass-bg` for a solid colour.

---

## The design system in one diagram

```
─────────────────  <header class="site-header">  ─────────────────

      .container                      .main-nav           .mobile-menu-btn
      max-width 1200px                horizontal links    hamburger (≤768px)


─────────────────  <main>  ─────────────────

  .section-title          .section-label (eyebrow pill)
                          h2
                          subtitle paragraph

  Cards everywhere:       .glass-card  ┐
                          .product-card├── share frosted-glass styling
                          .testimonial-card
                          .faq-item    ┘

  Buttons:                .btn .btn-primary       (filled)
                          .btn .btn-outline       (bordered)
                          .btn .btn-whatsapp      (WhatsApp green)


─────────────────  <footer class="site-footer">  ─────────────────
```

---

## Responsive breakpoints

Three main breakpoints, used across the site:

| Width | Triggers |
|-------|----------|
| ≤ 900 px | Hero stacks vertically; catalogue sidebar collapses to top strip |
| ≤ 768 px | Mobile nav menu activates; toolbars un-stick |
| ≤ 600 px / ≤ 480 px | Single-column grids; smaller padding |

Convention: `@media (max-width: <px>)`. We don't use `min-width` (mobile-first)
in this codebase — most styles are desktop-first with mobile overrides.

If you add a new component, pick one of these existing breakpoints rather
than introducing a new one. Consistency > perfection here.

---

## How to add a new component (CSS)

The site is small enough that there's no formal component library. The
convention is:

1. **Pick a unique class prefix** for the component (e.g. `.promo-strip`).
2. **Add a CSS block** at the bottom of `css/style.css` (or in a `<style>`
   block in the page that uses it, if it's truly page-specific).
3. **Use design tokens** (`var(--color-primary-dark)`, etc.) so the
   component picks up brand changes for free.
4. **Match the responsive pattern**: stack on `≤900px` if it's a multi-column
   layout, simplify on `≤480px`.
5. **Use the existing card patterns** (glass-card style) where it makes
   sense, so it visually fits.

Template for a new card-style component:

```css
/* ── Promo strip (e.g. monsoon offer card) ────────────────── */
.promo-strip {
    background: var(--glass-bg);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    box-shadow: var(--glass-shadow);
    padding: 28px 32px;
    transition: var(--transition);
}
.promo-strip:hover {
    transform: translateY(-3px);
    border-color: rgba(201, 126, 160, 0.3);
}
@media (max-width: 600px) {
    .promo-strip { padding: 20px 22px; }
}
```

---

## How to add a new button style

Buttons all extend `.btn`. Define a new modifier:

```css
.btn-secondary {
    background: var(--color-secondary);
    color: #1f6b3a;
    border: 1px solid #1f6b3a;
}
.btn-secondary:hover {
    background: #1f6b3a;
    color: white;
}
```

Use as `<a class="btn btn-secondary">…</a>`.

---

## Animation conventions

All transitions use the `--transition` custom property
(`all 0.32s cubic-bezier(0.25, 0.8, 0.25, 1)`). This curve is "ease-out
with a soft landing" — tactile but quick.

For one-off animations (the consent banner slide-up, the cart flash,
spotlight pulses), define a `@keyframes` block scoped to the component:

```css
@keyframes promo-pulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.04); }
}
.promo-strip.is-pulsing { animation: promo-pulse 0.6s ease; }
```

Don't use the global `--transition` for keyframe animations — the variable
is for transitions only.

---

## Dark mode

The site does **not** have a dark mode today. The pastel palette doesn't
translate cleanly to dark.

If you want one:
1. Use CSS `@media (prefers-color-scheme: dark)` to flip variable values:

   ```css
   @media (prefers-color-scheme: dark) {
       :root {
           --color-light: #1a1622;
           --color-dark: #faf9fb;
           --glass-bg: rgba(40, 30, 50, 0.72);
           ...
       }
   }
   ```

2. Test every page. Glassmorphism and pastel pinks will need rework — the
   palette was designed for cream-on-pink readability.

This is a meaningful redesign, not a quick toggle. Estimate ~1 week of
design + implementation.

---

## Print styles

There are no print-specific styles today. If you add them, scope them to
`@media print` and:

- Hide the floating WhatsApp button, cart button, consent banner.
- Use a serif font for body text (better print readability).
- Hide images that aren't critical (saves toner).

```css
@media print {
    .floating-whatsapp,
    #florista-quote-btn,
    #florista-consent { display: none !important; }
    body { font-family: var(--font-serif); }
}
```

---

## Brand asset checklist for a rebrand

If you're doing a full rebrand (e.g. business name change, palette
overhaul), here's everything to update in priority order:

1. **Logo and favicons** — replace the files in `images/` ([Ch 04](./04-images-and-media.md)).
2. **`<title>` tags** — open every HTML file, find `<title>`, update.
3. **The brand name in copy** — `grep -rl "Florista" --include="*.html" --include="*.py"`.
4. **The footer brand line** — duplicated across every page.
5. **CSS palette** — the seven variables in `:root`.
6. **Fonts** — `--font-sans` and `--font-serif` + Google Fonts URL.
7. **Logo CSS** — search `.logo` in `style.css`, the brand-name styling
   pattern (`Florista<span>.</span>`) is set there.
8. **JSON-LD `Organization` / `Manufacturer`** — search across all HTML
   files for `"name": "The Florista Flowers"` and `"@type": "Manufacturer"`.
9. **Open Graph `og:site_name`** — same.
10. **Email signatures, exported PDFs, business cards** — out of repo
    scope but worth a checklist.

The cookbook ([Ch 10](./10-cookbook.md)) has shell one-liners for the
bulk text-replacement steps.

---

Next chapter: [08 — Analytics & Lead Capture →](./08-analytics-and-leads.md)
