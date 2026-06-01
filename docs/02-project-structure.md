# 02 — Project Structure

A guided tour of the repository. After reading this you should know which
file to open for any given task.

---

## Top-level map

```
Florista/
├── docs/                    # ← you are here. The manual.
├── .agents/                 # Internal Kiro task tracking. Ignore for site work.
├── .github/workflows/       # CI configuration (GitHub Actions).
├── .kiro/steering/          # Long-form team rules referenced by docs.
├── css/                     # The single stylesheet for every page.
│   └── style.css
├── js/                      # The two JavaScript files.
│   ├── main.js              #   nav, mobile menu, FAQ, contact form, consent banner, WA attribution
│   └── quote-cart.js        #   floating multi-product quote cart
├── images/                  # All product photos (WebP) plus favicons.
├── products/                # ← GENERATED. 22 per-product SEO pages.
├── use-cases/               # ← GENERATED. 5 use-case landing pages.
├── tools/                   # The two Python generators + the content module.
│   ├── product_content.py
│   ├── generate_product_pages.py
│   └── generate_use_case_pages.py
│
├── wa-bot/                  # The WhatsApp sales bot (separate Python service).
│   ├── src/florista_bot/    #   Python package (LangGraph agent on FastAPI)
│   ├── apps_script/Code.gs  #   Tool layer that reads/writes the Sales Sheet
│   ├── data/products.json   #   Product catalog the bot recognizes (no prices)
│   ├── Dockerfile           #   Container for Railway / Fly.io / etc
│   ├── pyproject.toml       #   Python dependencies (managed by uv)
│   └── README.md            #   60-second orientation. Full guide: Ch 11.
│
├── index.html               # Home page.
├── products.html            # The catalogue (hand-maintained — see Ch 03).
├── about.html               # About / our story.
├── contact.html             # Contact form + map + phone.
├── wholesale.html           # Wholesale terms & logistics page.
├── privacy.html             # Privacy policy (DPDP Act compliant).
├── terms.html               # Terms of use.
├── refund.html              # Refund / return policy.
├── 404.html                 # Not-found page.
│
├── sitemap.xml              # Lists all 8 customer-facing pages for SEO.
├── robots.txt               # Tells crawlers which paths are allowed.
│
├── ROADMAP.md               # Identified-but-not-shipped work backlog.
├── BUGS_TO_FIX.md           # Known issues from the last audit.
└── florista_wa_bot_part1.json   # WhatsApp bot config (separate side-project).
```

---

## What each top-level page is for

| Page | What it does | Edit when… |
|------|--------------|-----------|
| `index.html` | Home page. Hero, trust strip, best-sellers, testimonials, FAQ, Instagram strip. | Hero copy changes; you have new testimonials; the FAQ needs updating. |
| `products.html` | The full catalogue. All 22 products as filterable cards. | **Adding/editing/removing a product** (see Ch 03). |
| `about.html` | Our story, team, factory note. | Brand story changes; new team photos arrive. |
| `contact.html` | B2B enquiry form, WhatsApp catalogue link, map embed. | Phone number / email / address changes. |
| `wholesale.html` | Logistics, payment terms, shipping policy for B2B buyers. | Payment policy or shipping rules change. |
| `privacy.html` | Privacy Policy. | Data practices change. |
| `terms.html` | Terms of use. | T&Cs change. |
| `refund.html` | Refund and return policy. | Policy changes. |
| `404.html` | Custom not-found page. | Rarely. |

---

## What each generated page is for

The folders `products/` and `use-cases/` are output, not input. **Never
edit files inside them by hand** — your edits will be erased the next time
the generator runs.

### `/products/<slug>.html` (22 files)

One page per SKU. Each one ranks for queries like
"60 inch wedding backdrop flower wholesale Nagpur." They link back to
`products.html#card-<slug>` for buyers who land there from search.

Source of truth: `tools/generate_product_pages.py` (the `PRODUCTS` list)
and `tools/product_content.py` (the per-SKU narrative copy).

### `/use-cases/<slug>.html` (5 files)

`mehndi-decor.html`, `wedding-backdrops.html`, `stage-decor.html`,
`haldi-decor.html`, `theme-party-decor.html`. They rank for intent queries
like "flowers for haldi function decor." Each one is a curated set of
product recommendations.

Source of truth: `tools/generate_use_case_pages.py` (the `USE_CASES` list).

---

## What each script does

### `tools/generate_product_pages.py`

Reads the `PRODUCTS` list (~250 lines of Python data near the top), the
`CONTENT_BY_SLUG` dict from `product_content.py`, and renders 22 HTML
files into `/products/`. Idempotent — re-running overwrites the files.

Run with:
```bash
python3 tools/generate_product_pages.py
```

### `tools/generate_use_case_pages.py`

Reads `USE_CASES` (5 entries) and the `PRODUCTS` data from the sibling
script, renders 5 HTML files into `/use-cases/`.

```bash
python3 tools/generate_use_case_pages.py
```

### `tools/product_content.py`

Pure data module. No executable logic. Holds the rich, hand-written copy
for each product (`narrative`, `built_for`, `pairs_with`, `craft_note`,
`hook_headline`, `contact_hook`). The product generator imports it.

Products **without** an entry here still render — they just use a generic
two-paragraph fallback.

---

## What each JS file does

### `js/main.js`

| Section | What it does |
|---------|-------------|
| Mobile menu toggle | Hamburger icon → expand `.main-nav` on phones |
| Active nav link | Highlights the current page in the header |
| Header scroll effect | Adds `.scrolled` class after 50px scroll |
| Scroll reveal | Adds `.visible` to elements with class `.reveal` as they enter the viewport |
| Lazy image loading | Sets `loading="lazy"` on every `<img>` |
| FAQ accordion | Single-open accordion behaviour |
| Contact form submit | Validates → opens WhatsApp → posts a row to the lead sheet |
| Cookie consent banner | DPDP Act–compliant banner, default-deny analytics |
| WhatsApp click attribution | Tags every `wa.me/...` link with `utm_source` and beacons clicks to the lead sheet |

### `js/quote-cart.js`

The floating "+" button on every product card and the slide-out drawer.
Reads `data-price`, `data-moq`, `data-id` from any `.product-card` on
the page. Items persist in `localStorage`. "Send Quote" opens WhatsApp
with a multi-line itemised message and beacons the cart contents to the
lead sheet.

If you change product prices, you don't need to touch this file — it
reads the data attributes at runtime. (You **do** need to keep those data
attributes in sync. See Ch 03.)

---

## What `css/style.css` does

The single design system for the whole site:

- CSS custom properties (variables) for the brand palette in `:root`
- Reset & base styles
- Header, footer, navigation
- Buttons (primary, outline, WhatsApp green)
- Glassmorphism card style (used everywhere)
- Product card base (extended by per-page styles)
- Lightbox / image zoom
- Responsive breakpoints

Some pages also have a `<style>` block in their `<head>` for page-specific
styles (the home-page hero, the catalogue toolbar, the per-product page
layout). That's a known duplication — see [BUGS_TO_FIX.md item #5](../BUGS_TO_FIX.md)
for the cleanup plan.

---

## What's in `images/`

185 files total:

- **Product photos** — `product_<slug>_<index>.webp`. There are usually
  2–14 photos per SKU. The generator template references them as
  `images/product_<prefix>_1.webp`, `_2.webp`, etc.
- **Favicons** — `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`.

Naming convention is enforced by the `image_prefix` and `image_indices`
fields in the `PRODUCTS` list. See [Chapter 04](./04-images-and-media.md).

---

## What's in `.github/workflows/`

A single file: `validate.yml`. It runs four checks on every push and PR:

1. **HTML well-formedness** — every `*.html` parses cleanly, no unclosed tags.
2. **JSON-LD schema** — every `<script type="application/ld+json">` block
   parses as valid JSON.
3. **Internal-link integrity** — every `href` and `src` in HTML files
   either is external, or points to a file that actually exists.
4. **`sitemap.xml` well-formedness** — parses as valid XML.

If any check fails, the PR is blocked from merging until you fix it. See
[Chapter 09](./09-deployment.md).

---

## What's in `.kiro/`

Persistent project rules. Currently two files:

- `steering/lead-capture.md` — the full Apps Script setup walkthrough for
  the lead-capture sheet on the website. Chapter 08 of this manual links
  to it; you shouldn't need to find it on your own.
- `steering/whatsapp-bot.md` — the click-by-click deployment runbook for
  the WhatsApp sales bot in `wa-bot/`. Chapter 11 of this manual links
  to it.

## What's in `wa-bot/`

The WhatsApp sales bot. Independent of the website — it's a separate
Python program that runs on a hosting platform like Railway and replies
to WhatsApp messages on behalf of Florista.

| Path | Purpose |
|------|---------|
| `wa-bot/src/florista_bot/main.py` | FastAPI app + Meta webhook routes |
| `wa-bot/src/florista_bot/agent.py` | LangGraph build (the AI conversation engine) |
| `wa-bot/src/florista_bot/tools.py` | What the bot can DO (look up prices, log leads, escalate) |
| `wa-bot/src/florista_bot/prompts.py` | What the bot SAYS (tone, rules, escalation policy) |
| `wa-bot/src/florista_bot/whatsapp.py` | Meta WhatsApp Cloud API client |
| `wa-bot/data/products.json` | Product catalog the bot recognizes (slugs + names, **NO prices**) |
| `wa-bot/apps_script/Code.gs` | Tool-layer Google Apps Script — reads the Pricing sheet, writes leads |
| `wa-bot/Dockerfile` | Container definition; works on Railway / Fly / Render |
| `wa-bot/.env.example` | Template for the env vars the bot needs |

The bot's **prices** live in the "Florista Sales" Google Sheet (Pricing
tab), NOT in this folder. That's intentional — see
[Chapter 11](./11-whatsapp-bot.md) for the why and the how.

---

## What's in `.agents/`

Internal task tracking from the AI agent that built the site. Safe to
ignore for day-to-day work.

---

## What's *not* in the repo (intentionally)

- **`node_modules/`** — there are no Node dependencies, so there's no
  `node_modules`.
- **`.env` files** — the site has no secrets in code. The Apps Script
  endpoint URL is configured directly in the JS files (Ch 08), and there
  are no API keys.
- **A build output folder** — the only "build" is the Python generator,
  and its output is committed to Git so the deployment is reproducible.
- **A `package.json`** — same reason. No build tooling.
- **Test files** — there are no automated tests. CI validates structure;
  manual testing handles behaviour.

---

Next chapter: [03 — Managing Products →](./03-managing-products.md)
