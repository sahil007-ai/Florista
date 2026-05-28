# Florista — Site Use-Case Manual

A practical, end-to-end guide to **what every part of the Florista website
does, and why**. Written so a new owner, freelancer, or future agent can sit
down with the repo and immediately understand the moving parts.

---

## Table of Contents

1. [What the site is](#1-what-the-site-is)
2. [Architecture at a glance](#2-architecture-at-a-glance)
3. [Site map — every page and its role](#3-site-map--every-page-and-its-role)
4. [Core user journeys (use cases)](#4-core-user-journeys-use-cases)
5. [Lead capture — the conversion engine](#5-lead-capture--the-conversion-engine)
6. [Quote Cart system](#6-quote-cart-system)
7. [Analytics & Consent Mode](#7-analytics--consent-mode)
8. [SEO infrastructure](#8-seo-infrastructure)
9. [Performance optimizations](#9-performance-optimizations)
10. [Accessibility & compliance](#10-accessibility--compliance)
11. [Build tools — how product pages are generated](#11-build-tools--how-product-pages-are-generated)
12. [Continuous Integration](#12-continuous-integration)
13. [Configuration cheat-sheet](#13-configuration-cheat-sheet)
14. [Owner runbook — common operations](#14-owner-runbook--common-operations)

---

## 1. What the site is

**Florista** (`theflorista.in`) is a B2B brochure + catalogue website for a
Nagpur-based manufacturer of handcrafted organza and fabric flowers used in
event decor — wedding backdrops, sangeet stages, mandap pillars, theme
parties, etc.

| Attribute              | Value                                                  |
| ---------------------- | ------------------------------------------------------ |
| Site type              | Static HTML (no backend)                               |
| Primary CTA            | WhatsApp enquiry → `+91 75884 47595`                   |
| Audience               | Wedding decorators, event planners, retailers (B2B)    |
| Geography              | PAN India shipping from Nagpur                          |
| Hosting model          | Static files (HTML/CSS/JS/images), no server logic     |
| External dependencies  | Google Analytics 4, Google Apps Script (lead sheet), Font Awesome CDN, Google Fonts |
| Total pages            | 36 HTML files (9 root + 22 products + 5 use-cases)     |

The site has **no backend, no database, no login**. Every conversion path
ends at WhatsApp. Lead capture is layered onto WhatsApp clicks via a
fire-and-forget beacon to a Google Sheet.

---

## 2. Architecture at a glance

```
Florista/
├── index.html              # home
├── products.html           # catalogue grid + filter/sort
├── about.html              # founder story, philosophy
├── contact.html            # B2B enquiry form + WhatsApp catalogue link
├── wholesale.html          # MOQ, payment, logistics policies
├── privacy.html            # DPDP Act privacy policy
├── terms.html              # terms of use
├── refund.html             # cancellation/return policy
├── 404.html                # custom not-found page
│
├── products/               # 22 per-product SEO landing pages
│   ├── 12-inch-regular-ornela.html
│   ├── ...
│   └── 60-inch-giant-flora.html
│
├── use-cases/              # 5 event-intent landing pages
│   ├── wedding-backdrops.html
│   ├── stage-decor.html
│   ├── mehndi-decor.html
│   ├── haldi-decor.html
│   └── theme-party-decor.html
│
├── css/style.css           # global styles (page-specific styles inline in <style>)
├── js/
│   ├── main.js             # nav, FAQ, contact form, consent banner, WA attribution
│   └── quote-cart.js       # multi-product quote builder (localStorage)
│
├── images/                 # 185 assets — 182 WebP product photos + favicons
├── tools/                  # generators (Python, run only when catalogue changes)
│   ├── generate_product_pages.py
│   ├── generate_use_case_pages.py
│   └── product_content.py
│
├── sitemap.xml             # search-engine sitemap
├── robots.txt              # crawler directives
├── florista_wa_bot_part1.json   # (legacy WA bot config — not deployed)
│
└── SITE_MANUAL.md          # this file
```

### Layering model

1. **Content layer** — HTML pages, hand-written or generated.
2. **Style layer** — `css/style.css` (global) + page-scoped inline `<style>`
   blocks for one-off layouts.
3. **Behaviour layer** — `js/main.js` (every page) + `js/quote-cart.js`
   (every page that has product cards).
4. **Tracking layer** — Google Analytics 4 with Consent Mode v2 + Apps
   Script beacon for lead capture.

Each layer fails gracefully if a higher layer breaks — a buyer with
JavaScript disabled can still browse the site, see prices, and click
through to WhatsApp.

---

## 3. Site map — every page and its role

### Root pages

| Page             | Job to be done                                                                               | Key sections                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `index.html`     | First-impression brochure; convert curious visitors to WhatsApp enquiry                       | Hero, trust strip, best sellers, stats strip, testimonials, AI-reference callout, Instagram, FAQ |
| `products.html`  | Browse the full catalogue with sort/filter and direct-to-product navigation                  | Size guide (collapsible), sticky sort/filter toolbar, 22-card grid                            |
| `about.html`     | Build trust — who is behind the brand, philosophy, working style                              | Founder story, photo grid, quality features list                                              |
| `contact.html`   | Capture a structured B2B lead — name, company, phone, city, interest                         | B2B enquiry form, WhatsApp catalogue link (`wa.me/c/...`), call-and-WA shortcuts             |
| `wholesale.html` | Set MOQ + payment + logistics expectations before buyer asks                                  | MOQ policy, advance-payment policy (100% first / 50-50 from third order), volumetric shipping |
| `privacy.html`   | DPDP Act compliance — what data we collect, retention, contact for grievance                  | Static legal copy                                                                              |
| `terms.html`     | Use-of-site terms and disclaimers                                                            | Static legal copy                                                                              |
| `refund.html`    | Cancellation & returns policy — set expectations on a custom-made product                    | Static legal copy                                                                              |
| `404.html`       | Friendly fallback for broken or stale links                                                  | Logo, "page not found" message, link back to home                                              |

### Product pages — `products/<slug>.html` (22 total)

All generated by `tools/generate_product_pages.py`. Each page:

- Hero image with click-to-zoom lightbox.
- Thumbnail gallery (where multiple photos exist).
- Spec grid (size, MOQ, shades, price).
- Expressive narrative (`tools/product_content.py` per-product copy).
- Use-case bullets, "pairs with" recommendations, craft note.
- WhatsApp enquiry CTA with product-specific pre-filled message.
- "Related products" sibling section.
- JSON-LD `Product` + `BreadcrumbList` schemas for rich SERP results.

The 22 products span four categories:

1. **Organza flowers** (12" through 60", named: Ornela, Lumora, Wedding
   Touch, Premium Collection, Wedding Bloom, Pure Bliss, Premium Blooms,
   Decor Blooms, Majestic, Big Flora, Giant Flora).
2. **Specialty pieces** (Aura Flower 3ft, Glowing Flower 3ft, Dream Wings
   90", Tri-Petal Flower 2.5ft, Cinderella Flowers, Blooming Dales,
   Fluffy Bloom).
3. **Fabric flowers** (Premium Fabric, Printed Fabric, Organza Butterfly).
4. **Theme** (Theme Party Fish).

### Use-case pages — `use-cases/<slug>.html` (5 total)

Generated by `tools/generate_use_case_pages.py`. Each page targets a single
event-intent search query (e.g. "wedding backdrop flowers wholesale") and
funnels readers into the matching subset of products.

| Slug                  | Target intent                                |
| --------------------- | -------------------------------------------- |
| `wedding-backdrops`   | "wedding backdrop flowers"                   |
| `stage-decor`         | "stage decoration flowers"                   |
| `mehndi-decor`        | "mehndi function decor"                      |
| `haldi-decor`         | "haldi function decor"                       |
| `theme-party-decor`   | "theme party decor flowers"                  |

---

## 4. Core user journeys (use cases)

### UC-1: First-time wholesaler researches pricing

1. Lands on home from Google search or Instagram.
2. Scrolls past hero → trust strip → best sellers (sees per-piece prices).
3. Clicks **"View All Products"** → browses `products.html`.
4. Uses sort/filter toolbar to filter by MOQ ≤ 10 (small starter order).
5. Clicks a product card → reads `products/<slug>.html` detail.
6. Clicks **"Enquire on WhatsApp"** → WhatsApp opens with a pre-filled,
   product-specific message.
7. Sends message → enters Florista's WhatsApp inbox as a tagged lead with
   `utm_source=product_<slug>_enquire`.

**Tracking captured:** GA4 `select_content` event with `item_id =
product_<slug>_enquire`, plus a fire-and-forget row in the Apps Script
sheet labelled `[product_<slug>_enquire]`.

### UC-2: Buyer planning a 12-foot backdrop

1. Reads use-case landing page `/use-cases/wedding-backdrops.html`.
2. Sees recommended product mix (60" anchor + 24" focal + 12" filler).
3. Clicks the **+** button on each product card to add to quote.
4. Floating quote button (bottom-right) appears with badge count.
5. Opens quote drawer → adjusts quantities with MOQ-aware steppers.
6. Clicks **"Send Quote on WhatsApp"** → consolidated message opens with:
   - Bullet list of items × quantity × per-piece price.
   - Estimated total at base prices.
   - `— via: quote_cart_send` marker for source tracking.

**Tracking captured:** GA4 `generate_lead` (method=`quote_cart`,
items_count, value, currency=INR), plus an anonymous row in the Apps
Script sheet tagged `[quote_cart_send]`.

### UC-3: Decorator with a Pinterest reference

1. Lands on `index.html`.
2. Reads the AI-reference callout: "Send a Reference Image — AI,
   Pinterest, or sketch. We craft it real."
3. Clicks the **WhatsApp** CTA → WhatsApp opens with a pre-filled custom-
   order message.
4. Attaches reference image inside WhatsApp and sends.

**Tracking captured:** GA4 `select_content` with `item_id =
home_hero` (or whichever CTA they clicked), Apps Script row with
`[home_hero]` tag.

### UC-4: Owner reviews leads (admin journey)

The owner does **not** need to log in to the site. All lead activity
flows into a single Google Sheet via an Apps Script `/exec` endpoint:

- **Form submissions** appear as fully-named rows tagged `[contact_form]`.
- **WhatsApp clicks** appear as anonymous rows tagged `[<utm_source>]`
  (e.g. `[home_hero]`, `[products_card_60-inch-giant-flora]`).
- **Quote sends** appear with the consolidated SKU list, tagged
  `[quote_cart_send]`.

The owner cross-references each row with their actual WhatsApp inbox to
attribute conversions to source.

> **Setup status**: `FORM_ENDPOINT_URL` is currently empty in both
> `js/main.js` and `js/quote-cart.js`. Until the owner pastes the
> deployed Apps Script URL into both files, leads still flow to WhatsApp
> but anonymous beacon rows are not written. See
> [`.kiro/steering/lead-capture.md`](.kiro/steering/lead-capture.md) (if
> present) for the Apps Script setup steps.

### UC-5: Buyer abandons after WhatsApp opens

This is the most common failure mode for the conversion funnel: the user
clicks the WhatsApp button, WhatsApp opens, but they never tap **Send**.

The site is designed to capture **even this case**:

- Before opening WhatsApp, the click handler fires:
  1. A GA4 `generate_lead` (form submit) or `select_content` (anchor click) event.
  2. A `navigator.sendBeacon()` POST to the Apps Script endpoint, which
     survives the impending page navigation.
- The Apps Script row is labelled "(WhatsApp click — anonymous; awaiting
  reply)" so the owner can spot abandoned funnels in the sheet.

This is why `navigator.sendBeacon()` is preferred over `fetch()` — fetch
would be cancelled when the wa.me tab opens; sendBeacon is specifically
designed to outlive the navigation.

---

## 5. Lead capture — the conversion engine

The lead-capture pipeline is the most important piece of behavioural code
on the site. There are **three sources** that all funnel into the same
Apps Script sheet:

### 5.1 The B2B enquiry form (`contact.html`)

**File**: `js/main.js`, function bound to `#b2b-enquiry-form`.

**Fields** (all `maxlength`-capped to prevent quota abuse):

| Field         | maxlength | Required | Validation                                                |
| ------------- | --------- | -------- | --------------------------------------------------------- |
| `companyName` | 120       | Yes      | Non-empty after `.trim()`                                  |
| `phone`       | 25        | Yes      | ≥10 digits after Unicode normalization                     |
| `city`        | 80        | Yes      | Non-empty after `.trim()`                                  |
| `interest`    | 200       | No       | Free text (e.g. "Giant Flora 60 inch, Theme Party Fish")  |

**Multi-script digit handling.** The phone validator uses
`toAsciiDigits()` to convert Devanagari, Tamil, Bengali, Arabic-Indic,
Gujarati, Punjabi, Kannada, Malayalam, Telugu, and Oriya digits to ASCII
**before** stripping non-digits. An Indian buyer typing on a Hindi
keyboard (`९८७६५४३२१०`) would otherwise have every digit rejected as
"non-digit" by `\D/g`.

**On submit** the handler:

1. Fires GA4 `generate_lead` event (`method=contact_form`, includes city +
   interest).
2. Calls `postLeadCapture()` — a `sendBeacon`-preferred POST to the Apps
   Script `/exec` URL with company, phone, city, interest, page,
   userAgent, and timestamp.
3. Synchronously opens `wa.me/917588447595?text=<pre-filled message>` in
   a new tab. The synchronous open is critical — popup blockers only
   trust direct user gestures.
4. Falls back to `window.location.href` navigation if the popup is
   blocked, so the lead can still complete.
5. Updates the submit button to "WhatsApp opened — tap Send to finish"
   for 5 seconds. **Honest** — the message is not yet sent until the
   user taps Send inside WhatsApp.

### 5.2 WhatsApp click attribution (every `wa.me/...` anchor)

**File**: `js/main.js`, IIFE at bottom that exposes `window.FloristaWA`.

Every `<a href="wa.me/...">` link on every page is automatically tagged
on `DOMContentLoaded` (and re-tagged any time `quote-cart.js` injects
new ones).

**Three attribution layers per click:**

| Layer | Mechanism                                                 | Survives           | Where the source ends up                  |
| ----- | --------------------------------------------------------- | ------------------ | ----------------------------------------- |
| 1     | URL-tagged with `?utm_source=<x>&utm_medium=whatsapp`    | wa.me hop          | GA4 outbound-link click attribution       |
| 2     | Fire-and-forget `sendBeacon` POST to Apps Script         | page navigation    | Lead-capture sheet, even if Send never tapped |
| 3     | `\n\n— via: <source>` appended to the pre-filled text    | wa.me → WhatsApp   | Visible in the actual WhatsApp message    |

**Source slug taxonomy** (auto-derived per anchor by `deriveSource()`):

| Anchor location                              | Source slug                              |
| -------------------------------------------- | ---------------------------------------- |
| `[data-wa-source="..."]` attribute (override) | (uses the explicit value)                |
| `.floating-whatsapp` (the FAB)               | `<page>_floating`                        |
| Inside `.footer-social`                      | `<page>_footer_social`                   |
| Inside a `.product-card`                     | `<page>_card_<slug>` (data-id or extracted from href) |
| Inside `.uc-final-cta`                       | `<page>_final_cta`                       |
| Inside `.uc-hero`                            | `<page>_hero`                            |
| Inside `.size-guide`                         | `<page>_size_guide`                      |
| Inside `.cat-sidebar` / `.sidebar-cta`       | `<page>_sidebar`                         |
| Inside `.pd-cta` (per-product page)          | `<page>_enquire`                         |
| Anything else                                | `<page>_unknown` (TODO list for tagging) |

`<page>` derivation:

| URL path                                    | Slug                          |
| ------------------------------------------- | ----------------------------- |
| `/` or `/index.html`                        | `home`                        |
| `/products.html`                            | `products`                    |
| `/products/<x>.html`                        | `product_<x>`                 |
| `/use-cases/<x>.html`                       | `use_case_<x>`                |
| anything else                               | filename without `.html`      |

A `<body data-wa-page="...">` attribute can override page derivation per
file.

### 5.3 Quote cart send (`js/quote-cart.js`, `sendQuote()`)

When the user clicks **"Send Quote on WhatsApp"** in the drawer:

1. Fires GA4 `generate_lead` (`method=quote_cart`, `items_count`,
   `value`, `currency=INR`, `source=quote_cart_send`).
2. POSTs an anonymous lead row to Apps Script tagged `[quote_cart_send]`
   with the bulleted SKU list and estimated total in the `interest`
   field.
3. Opens WhatsApp synchronously (popup-blocker safe) with the
   consolidated message and `utm_source=quote_cart_send`.
4. Closes the drawer but **keeps the cart populated** so the buyer can
   tweak and re-send (or reuse the list for a follow-up event).

### 5.4 The two `FORM_ENDPOINT_URL` constants

The Apps Script URL is duplicated on purpose, in two files:

- `js/main.js` line ~16
- `js/quote-cart.js` line ~52

Both must be set to the same `/exec` URL when wiring up Apps Script. The
duplication is intentional (each file is small, only two callsites). If
the URL is empty, lead-capture beacons no-op silently and WhatsApp
redirects still work — graceful degradation.

---

## 6. Quote Cart system

**File**: `js/quote-cart.js` (~860 lines, self-contained).

### 6.1 What it does

Lets a wholesale buyer assemble a multi-SKU quote across the catalogue
and send a single consolidated WhatsApp message. Without this, every
product needs its own back-and-forth — three SKUs = three message
threads = three chances for the buyer to give up.

### 6.2 Storage model

`localStorage['florista-quote-cart']` is a JSON object keyed by product
slug:

```js
{
  "60-inch-giant-flora":     { id, name, price, moq, qty },
  "24-inch-wedding-touch":   { id, name, price, moq, qty },
  ...
}
```

`loadCart()` is **defensively** typed: it accepts the parsed value only
if it's a non-array object, otherwise returns `{}`. This guards against
the corruption-by-`null` bug (someone sets the key to `"null"`, which is
valid JSON but breaks downstream property writes).

`saveCart()` wraps `localStorage.setItem` in `try/catch` — iOS Safari in
private mode historically had a 0-byte quota and would throw
`QuotaExceededError`. Modern Safari fixed this, but legacy iPhones still
exist among older buyer demographics.

### 6.3 Catalogue indexing

On `DOMContentLoaded`, `indexProductCards()` scans every
`.product-card[data-price]` on the page, reads:

- `data-id` (slug) — set explicitly on most cards; auto-derived from the
  card's `<h3>` text by `slugify()` if missing.
- `data-price` — base per-piece price in INR.
- `data-moq` — minimum order quantity.
- `<img>` src — product photo.
- `<h3>` text — product name.

Then it **injects a circular `+` button** in the top-right of each card.
Click → `addToCart()`. Second click on an already-added card removes it.

### 6.4 Drawer UI

Built once on first open by `buildDrawer()`, then rendered fresh each
time by `renderDrawer()`:

- Slide-in from the right (440px max width on desktop, full-width on mobile).
- Each item shows: name, base price/pc, MOQ, qty stepper (–/input/+),
  and an `×` remove button.
- Footer: estimated total at base prices + WhatsApp send button + clear
  all.

**Defensive rendering**: every numeric field uses defaulted reads
(`typeof item.price === 'number' ? item.price : 0`) so an old
localStorage entry missing a field doesn't crash the whole drawer.

**Quantity bounds**:

- Lower bound: clamped to MOQ.
- Upper bound: 100,000 (sane cap — prevents `Infinity`, `1e15`, or
  pasted-in absurd values from sailing into the WhatsApp message).
- HTML input also has `max="100000"` for browser-side validation.

### 6.5 Accessibility

- `role="dialog"` + `aria-modal="true"` on the drawer.
- Focus trap: Tab and Shift-Tab cycle within the drawer's focusable
  elements. ESC closes.
- Focus moves into the drawer's close button on open (via `requestAnimationFrame` so it fires after the element is visible).
- Focus returns to the cart trigger button on close.

### 6.6 Hash-based deep linking

URLs like `products.html#card-60-giant-flora` will:

1. Scroll the matching card into view (`block: 'center'`).
2. Apply a brief "spotlight pulse" CSS animation so the buyer's eye
   lands immediately on the card.

Used by the home-page best-seller cards' "View Details" buttons. The
slug rule (`slugify()`) is identical to the one used to derive
`data-id`, so JS-derived IDs match hardcoded hrefs perfectly.

### 6.7 Public debugging API

```js
FloristaCart.add('60-inch-giant-flora')
FloristaCart.remove('60-inch-giant-flora')
FloristaCart.setQty('60-inch-giant-flora', 50)
FloristaCart.clear()
FloristaCart.openDrawer()
FloristaCart.closeDrawer()
FloristaCart.getItems()
```

All exposed on `window.FloristaCart` for console testing.

---

## 7. Analytics & Consent Mode

### 7.1 Google Analytics 4

- **Property ID**: `G-T5GR1DL2G0`
- **Loader**: `<script async src="googletagmanager.com/gtag/js?id=...">`
  in every page's `<head>`.
- **Default state**: `analytics_storage: 'denied'`, `ad_storage:
  'denied'` — set **before** `gtag('config', ...)` so no hits fire
  before consent is established.

### 7.2 Consent Mode v2 (DPDP Act compliance)

India's Digital Personal Data Protection Act 2023 requires explicit
consent before non-essential tracking. The implementation:

1. **Page load**: every page reads `localStorage['florista-consent']`
   inline and emits the appropriate `gtag('consent', 'default', ...)`
   call before GA4 ships its first beacon.
2. **First visit** (no stored choice): banner builds itself in
   `js/main.js` IIFE, slides up from the bottom, offers Accept/Decline.
3. **Accept**: stores `'accepted'` for 365 days, calls `gtag('consent',
   'update', { analytics_storage: 'granted' })`. GA4 starts tracking.
4. **Decline**: stores `'declined'`, GA4 stays disabled.
5. **Returning visitor**: banner skipped, prior choice respected.

### 7.3 Custom GA4 events

The site fires three event names beyond GA4's auto-collected
`page_view`/`scroll`/`click`:

| Event             | When                                   | Parameters                                                  |
| ----------------- | -------------------------------------- | ----------------------------------------------------------- |
| `select_content`  | Any `wa.me/...` anchor clicked         | `content_type='whatsapp_cta'`, `item_id=<utm_source slug>`  |
| `generate_lead`   | B2B form submitted                     | `method='contact_form'`, `form_id`, `city`, `interest`      |
| `generate_lead`   | Quote-cart sent                        | `method='quote_cart'`, `source`, `items_count`, `value`, `currency='INR'` |

`generate_lead` is GA4's recommended B2B conversion event and is
**one-click promotable to a Key Event** in the GA4 admin UI.

### 7.4 What this looks like in practice

| GA4 report                      | Reads                                                                       |
| ------------------------------- | --------------------------------------------------------------------------- |
| Acquisition → Traffic acquisition | UTM-tagged WA clicks show up as outbound source in the session stack          |
| Engagement → Events             | Counts of `select_content` (soft signal) vs `generate_lead` (hard signal)    |
| Engagement → Conversions        | Once `generate_lead` is promoted to Key Event, conversion rate per source   |

---

## 8. SEO infrastructure

### 8.1 Per-page metadata

Every page has:

- `<title>` (target ≤60 chars — some pages currently exceed)
- `<meta name="description">` (target ≤160 chars — some pages currently exceed)
- `<link rel="canonical">` (present on product/use-case pages; some root pages still missing)
- Open Graph: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`

### 8.2 Structured data (JSON-LD)

| Page                     | Schema types                                |
| ------------------------ | ------------------------------------------- |
| `index.html`             | `Manufacturer`                              |
| `products.html`          | `ItemList` of all 22 products               |
| `products/<slug>.html`   | `Product` + `BreadcrumbList`                |
| `use-cases/<slug>.html`  | `BreadcrumbList`                            |

This unlocks rich-result eligibility in Google SERPs (price chips,
breadcrumbs, image carousel).

### 8.3 Sitemap & robots

- `sitemap.xml` lists all customer-facing URLs with `<lastmod>` /
  `<changefreq>` / `<priority>` hints.
- `robots.txt` allows everything and points crawlers to the sitemap.
- The CI workflow validates that `sitemap.xml` is well-formed XML and
  that every URL it declares actually exists on disk.

### 8.4 Image SEO

Every `<img>` has:

- Descriptive `alt` text (B2B-keyword-aware: e.g. *"60-inch Giant Flora
  organza event flower by Florista, Nagpur"*).
- `loading="lazy"` for below-the-fold, `loading="eager"
  fetchpriority="high"` for the hero LCP image (set on most landing
  pages; a couple of secondary pages still inherit the default).
- `decoding="async"` to keep main-thread free.

---

## 9. Performance optimizations

| Optimization                                | Impact                                                         |
| ------------------------------------------- | -------------------------------------------------------------- |
| 184 PNG → WebP conversion (PR #2)           | `images/` 88 MB → 5.8 MB (93% saving)                          |
| Hero `<img>` `loading=eager fetchpriority=high` | Faster LCP on home + product pages                          |
| Explicit hero `width`/`height` attributes   | Prevents Cumulative Layout Shift                               |
| `<link rel="preconnect">` to Google Fonts   | Saves the TLS handshake on font requests                       |
| Lazy-loaded `<img>` for below-the-fold      | Browser doesn't download offscreen images                      |
| `IntersectionObserver` reveal animations    | No expensive scroll-event listeners                             |
| Passive scroll listener (`{ passive: true }`) | Allows browser to optimize scroll performance                |
| Font Awesome from CDN                       | Cached across sites; no local asset weight                     |
| WebP `srcset` (deferred)                    | Per-device image variants would shave more KB                  |

---

## 10. Accessibility & compliance

| Concern                  | Implementation                                                     |
| ------------------------ | ------------------------------------------------------------------ |
| Mobile menu              | `aria-label="Toggle menu"`, swaps `fa-bars` ↔ `fa-times`            |
| FAQ accordion            | `aria-expanded` toggled per item                                    |
| Quote drawer             | `role="dialog"`, `aria-modal="true"`, focus trap, ESC closes, focus restore |
| Lightbox                 | ESC closes (full `role="dialog"` semantics still pending)         |
| Consent banner           | `role="dialog"`, `aria-label="Cookie consent"`                      |
| Reduced-motion           | Reveal animations respect `prefers-reduced-motion` via CSS          |
| Form errors              | Visual border + placeholder hint + auto-focus first invalid field   |
| `:focus-visible`         | Currently browser default — global treatment pending              |
| Color contrast           | Body text meets WCAG AA on cream; brand-pink-on-cream is AA-large only |

**Legal compliance:**

- DPDP Act 2023 — analytics consent banner, default-deny, choice persisted.
- Privacy / Terms / Refund pages linked from footer of every page.
- No GST claims (Florista is not GST-registered).

---

## 11. Build tools — how product pages are generated

The 22 product pages and 5 use-case pages are **generated**, not
hand-written. The generator scripts live in `tools/`.

### 11.1 `tools/generate_product_pages.py`

**Reads** (hardcoded in the script):

- Product catalogue list (slug, name, size, price, MOQ, shades, category,
  use case, image filenames).

**Imports**:

- `tools/product_content.py` — per-product expressive copy (narrative,
  use-case bullets, "pairs with", craft note, contact hook).

**Emits** for each product, into `products/<slug>.html`:

1. Standard `<head>` with title, description, canonical, OG tags, GA4.
2. Breadcrumb nav (Home → Products → product name).
3. Image gallery with thumbnail row + click-to-zoom lightbox.
4. Spec grid (size, MOQ, shades, price).
5. Long-form description from `product_content.py` (with graceful
   fallback to a generic template if no per-product entry exists).
6. Per-product WhatsApp CTA with a tailored pre-filled message.
7. "Related products" section showing 3 sibling SKUs from the same category.
8. JSON-LD `Product` + `BreadcrumbList` schema blocks.
9. Standard footer.

**Run when**: catalogue changes (price update, new product, copy edit
in `product_content.py`).

```bash
python3 tools/generate_product_pages.py
```

### 11.2 `tools/generate_use_case_pages.py`

Builds the 5 event-intent landing pages from a similar template. Each
page hand-picks 4–6 products from the full catalogue that are relevant
to that event type, and writes them into a recommended-grid section.

```bash
python3 tools/generate_use_case_pages.py
```

### 11.3 `tools/product_content.py`

Pure data module — a single dict `CONTENT_BY_SLUG` keyed by product
slug. Each entry has six fields:

```python
{
    "narrative":     [str, str, ...],   # 2-3 paragraphs, story/voice
    "built_for":     [str, ...],        # 3-4 product-specific use-case bullets
    "pairs_with":    str,               # one-sentence layering recommendation
    "craft_note":    str,               # tactile/process detail
    "hook_headline": str,               # warm contact headline
    "contact_hook":  str,               # 1-2 sentence WA invite
}
```

This is the single source of truth for the *expressive* copy on each
product page. The generator falls back to a generic template if a slug
isn't represented here, so the build never breaks when a new SKU is
added before its copy is written.

---

## 12. Continuous Integration

**File**: `.github/workflows/validate.yml`

Runs on every push to `main` and every PR. Four checks, all in plain
Python (no install step beyond `actions/setup-python@v5`):

| Check                       | What it catches                                                    |
| --------------------------- | ------------------------------------------------------------------ |
| HTML well-formedness        | Unclosed tags, mismatched closing tags                              |
| JSON-LD schema validity     | Malformed `<script type="application/ld+json">` blocks              |
| Internal-link integrity     | Broken `href` / `src` references (incl. `../`-relative from subdirs) |
| `sitemap.xml` validity      | Malformed XML or missing URLs                                       |

If any check fails, the PR is blocked until fixed. This is deliberately
strict because the site is hand-authored static HTML — it's easy for a
typo to ship a broken page that would only surface as a 404 in
production.

---

## 13. Configuration cheat-sheet

| Setting                          | Where                                      | Current value                                       |
| -------------------------------- | ------------------------------------------ | --------------------------------------------------- |
| WhatsApp phone (international)   | Hardcoded in every wa.me anchor + JS files | `917588447595` (= +91 75884 47595)                  |
| GA4 property                     | Every HTML page header                     | `G-T5GR1DL2G0`                                      |
| Lead-capture endpoint (form)     | `js/main.js` `FORM_ENDPOINT_URL`            | **empty** — paste Apps Script `/exec` URL here      |
| Lead-capture endpoint (cart)     | `js/quote-cart.js` `FORM_ENDPOINT_URL`     | **empty** — must match the one in `main.js`         |
| Brand colours                    | `css/style.css` CSS custom properties      | `--color-primary` pink, `--color-dark` plum         |
| Consent storage key              | `js/main.js`                                | `florista-consent` (values: `accepted` / `declined`) |
| Cart storage key                 | `js/quote-cart.js`                          | `florista-quote-cart` (JSON object)                 |
| Cart MAX_QTY                     | `js/quote-cart.js` `setQty()`              | `100000`                                            |
| Instagram handle                 | `index.html` IG strip                       | [@thefloristaflowerss](https://www.instagram.com/thefloristaflowerss/) |

---

## 14. Owner runbook — common operations

### Update a product's price

1. Edit the price in `tools/generate_product_pages.py` (the catalogue
   list at the top).
2. Edit the same price in the matching `data-price` attribute on
   `products.html` and `index.html` best-seller cards (if applicable).
3. Run `python3 tools/generate_product_pages.py` to regenerate the
   detail page.
4. Commit + push. CI validates the result.

### Add a new product

1. Add a new entry to the catalogue list in
   `tools/generate_product_pages.py`.
2. Drop product photos into `images/` (WebP, named
   `product_<slug>_<n>.webp`).
3. Optionally add an entry in `tools/product_content.py` for richer copy
   (otherwise the generic fallback is used).
4. Add a card to `products.html` in the appropriate category section.
5. Add the product to `sitemap.xml`.
6. Run `python3 tools/generate_product_pages.py`.
7. Commit + push.

### Wire up the Apps Script lead-capture endpoint

1. Set up a Google Apps Script project that writes incoming POST bodies
   to a Sheet (template lives in `.kiro/steering/lead-capture.md` if
   present).
2. Deploy as a web app → copy the `/exec` URL.
3. Paste the URL into **both**:
   - `js/main.js` line ~16 (`const FORM_ENDPOINT_URL = '...'`)
   - `js/quote-cart.js` line ~52 (`const FORM_ENDPOINT_URL = '...'`)
4. Commit + push.
5. Test by clicking any WhatsApp button → verify a row lands in the
   sheet within 5 seconds.

### Replace placeholder testimonials

`index.html` has three `<div class="testimonial-card">` blocks with
`[REPLACE]` placeholders. The collection process is documented inline
as an HTML comment above the testimonials section: ask 2–3 long-running
decorator clients for a 1–2 sentence quote + first name + city + role,
then paste each into a card.

### Read the lead-capture sheet

Each row carries:

- `company` — the buyer's company (or `(WhatsApp click — anonymous; …)` for unattributed clicks)
- `phone` — buyer's WhatsApp number (form-only)
- `city` — buyer's city (form-only)
- `interest` — `[<source-tag>] <free text>`
- `page` — full URL the click came from
- `userAgent` — browser/device fingerprint
- `timestamp` — ISO 8601

Filter by the `[<source-tag>]` prefix in `interest` to attribute leads
to entry point.

### Update the privacy / terms / refund pages

Edit `privacy.html` / `terms.html` / `refund.html` directly. They are
plain HTML with the standard header + footer. CI will validate
well-formedness on push.

---

_Last updated: 28 May 2026 — covers the codebase as of the current
`main` branch._
