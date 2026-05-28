# Florista

The website for **The Florista Flowers** — a Nagpur-based wholesale
manufacturer of handcrafted organza and fabric flowers, serving event
decorators and wholesalers across India.

🌐 Live site: <https://www.theflorista.in>

---

## What this repo is

A static website. Plain HTML, CSS, and vanilla JavaScript. No backend,
no database, no framework. The "build step" is two small Python scripts
that generate per-product and per-use-case landing pages from a single
source-of-truth list.

---

## Where to start

### 👉 If you've never worked on this site before, **read [`docs/`](./docs/README.md) first.**

The `docs/` folder is a complete operating manual covering everything
from local setup through to running sales, adding products, and
deploying changes. It's structured so you can read it cover-to-cover or
jump to a chapter.

| Chapter | What it covers |
|---------|---------------|
| [01 — Getting Started](./docs/01-getting-started.md) | Local setup. ~10 minutes. |
| [02 — Project Structure](./docs/02-project-structure.md) | Map of every folder and file. |
| [03 — Managing Products](./docs/03-managing-products.md) | **Add, edit, remove, rename, reprice products.** The single most important chapter. |
| [04 — Images & Media](./docs/04-images-and-media.md) | How product photos are named and added. |
| [05 — Sales & Discounts](./docs/05-sales-and-discounts.md) | Run a sale: banners, strikethrough prices, slab pricing, coupon codes. |
| [06 — Editing Site Content](./docs/06-editing-content.md) | Hero, FAQ, testimonials, footer, contact info, About page. |
| [07 — Styling & Branding](./docs/07-styling-and-branding.md) | Colours, fonts, the design system. |
| [08 — Analytics & Lead Capture](./docs/08-analytics-and-leads.md) | GA4, WhatsApp click attribution, the Apps Script lead sheet. |
| [09 — Deployment & CI](./docs/09-deployment.md) | How changes go live. What CI checks do. |
| [10 — Cookbook](./docs/10-cookbook.md) | One-page quick reference of common tasks. **Bookmark this.** |

---

## Quick links

- **Day-to-day reference:** [Cookbook (Ch 10)](./docs/10-cookbook.md)
- **Backlog of pending owner decisions:** [`ROADMAP.md`](./ROADMAP.md)
- **Known bugs from the latest audit:** [`BUGS_TO_FIX.md`](./BUGS_TO_FIX.md)
- **Lead-capture sheet setup:** [`.kiro/steering/lead-capture.md`](./.kiro/steering/lead-capture.md)

---

## Run the site locally

```bash
git clone https://github.com/sahil007-ai/Florista.git
cd Florista
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```

That's it. No `npm install`, no `pip install`. Python 3.8+ and Git are
the only prerequisites.

For the full setup walkthrough, see
[`docs/01-getting-started.md`](./docs/01-getting-started.md).

---

## Repository layout

```
Florista/
├── docs/                  ← The manual. Start here.
├── index.html             ← Home
├── products.html          ← Catalogue (hand-maintained — see Ch 03)
├── about.html, contact.html, wholesale.html, ...
├── products/              ← GENERATED per-product SEO pages
├── use-cases/             ← GENERATED use-case landing pages
├── images/                ← All product photos (WebP)
├── css/style.css          ← The design system
├── js/main.js             ← Nav, FAQ, contact form, consent banner, WA attribution
├── js/quote-cart.js       ← Floating multi-product quote cart
├── tools/                 ← The Python generators + per-product copy module
├── sitemap.xml, robots.txt
├── ROADMAP.md             ← Pending owner decisions
└── BUGS_TO_FIX.md         ← Known issues
```

For a more detailed walkthrough, see
[`docs/02-project-structure.md`](./docs/02-project-structure.md).

---

## The five rules that prevent breakage

These are repeated in [`docs/README.md`](./docs/README.md) but they're
important enough to put right here too:

1. **Always read [Ch 03](./docs/03-managing-products.md) before touching
   a price.** Prices live in three places per product. Skip one and
   search results will lie.
2. **Never edit files in `/products/` or `/use-cases/` by hand.** They're
   generated. Edit `tools/generate_*_pages.py` and re-run the script.
3. **Always work on a branch and open a PR.** Never push directly to
   `main`. CI catches structural issues before they hit production.
4. **The `data-price` and `data-moq` attributes on each catalogue card
   are not cosmetic.** `js/quote-cart.js` reads them. Get them wrong and
   the buyer's WhatsApp message shows wrong numbers.
5. **The lead-capture endpoint URL must match in two files.** When
   wiring up Apps Script (Ch 08), paste the same `/exec` URL into
   `js/main.js` *and* `js/quote-cart.js`.

---

## Contributing

Branch, change, push, PR. CI will run four validators
(HTML well-formedness, JSON-LD schema, internal links, sitemap). If they
pass and you've tested locally, the change is ready to merge.

See [`docs/09-deployment.md`](./docs/09-deployment.md) for details on the
CI workflow and how to interpret failures.

---

## License

© The Florista Flowers. All rights reserved.
