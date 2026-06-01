# Florista — Developer & Owner Manual

Welcome. This folder is the operating manual for **theflorista.in**.

If you've just joined the project — or you're the owner trying to update the
site without breaking anything — start here.

The site is a **static HTML website** (no database, no backend framework).
That means every change is a small, traceable edit to a file on disk. Once
you understand which file controls which piece of the site, you can confidently
add products, run sales, change phone numbers, swap photos, and edit copy
without touching anything you don't need to.

---

## How to use this manual

Read in order if you're new. Jump straight to a chapter if you know what
you need.

| #  | Chapter | When to read it |
|----|---------|-----------------|
| 01 | [Getting Started](./01-getting-started.md) | First time setup. Install Python, clone the repo, preview the site locally. |
| 02 | [Project Structure](./02-project-structure.md) | What every folder and file does. Map of the codebase. |
| 03 | [Managing Products](./03-managing-products.md) | **Add, edit, remove, or rename a product.** Update prices, MOQs, descriptions, photos. |
| 04 | [Images & Media](./04-images-and-media.md) | How product images are named, how to add new ones, optimisation rules. |
| 05 | [Sales & Discounts](./05-sales-and-discounts.md) | Run a sale: site-wide banner, strikethrough prices, slab pricing, coupon codes. |
| 06 | [Editing Site Content](./06-editing-content.md) | Hero text, FAQ, testimonials, footer, contact info, About page, legal pages. |
| 07 | [Styling & Branding](./07-styling-and-branding.md) | Colours, fonts, the design system. Rebrand without touching every file. |
| 08 | [Analytics & Lead Capture](./08-analytics-and-leads.md) | Google Analytics, WhatsApp click attribution, the Apps Script lead sheet. |
| 09 | [Deployment & CI](./09-deployment.md) | How changes go live. What the GitHub Actions checks do and how to fix them. |
| 10 | [Cookbook (Quick Recipes)](./10-cookbook.md) | One-page recipes for the most common tasks. Bookmark this. |
| 11 | [The WhatsApp Bot](./11-whatsapp-bot.md) | **Run the WhatsApp sales bot.** Change prices, edit tone, swap models, troubleshoot. |

There are also two living documents at the **repo root** that complement
this manual:

- [`ROADMAP.md`](../ROADMAP.md) — work that's been identified but not yet
  shipped (owner pending input, external setup needed, deferred items).
- [`BUGS_TO_FIX.md`](../BUGS_TO_FIX.md) — known bugs from the last audit,
  with severity, repro steps, and fix sketches.

And one team rule of record:

- [`.kiro/steering/lead-capture.md`](../.kiro/steering/lead-capture.md) —
  the Google Apps Script setup steps for the lead-capture sheet. Chapter 08
  links to this; you don't need to find it on your own.
- [`.kiro/steering/whatsapp-bot.md`](../.kiro/steering/whatsapp-bot.md) —
  the click-by-click deployment runbook for the WhatsApp sales bot
  (Meta + OpenRouter + Google Sheets). Chapter 11 links to this; it's
  the deeper companion to that chapter.

---

## The 30-second mental model

```
Florista is just HTML files. Editing the site = editing those files.

  index.html, products.html, about.html, …   <- pages you can see
        ↑
        |  shares
        ↓
  css/style.css        <- one stylesheet for every page
  js/main.js           <- nav, mobile menu, FAQ, contact form
  js/quote-cart.js     <- the multi-product quote cart
  images/*.webp        <- every product photo

  tools/generate_product_pages.py   <- regenerates /products/<slug>.html
  tools/generate_use_case_pages.py  <- regenerates /use-cases/<slug>.html
  tools/product_content.py          <- per-product narrative copy

  wa-bot/                           <- the WhatsApp sales bot (separate
                                       Python service hosted on Railway).
                                       Independent of the website. See
                                       Chapter 11.
```

The two Python scripts in `tools/` are the only "build step" the site has.
Everything else is direct HTML/CSS/JS editing.

The `wa-bot/` folder is a separate Python program that runs 24/7 on a
host like Railway. It receives WhatsApp messages and replies on behalf
of Florista. It does NOT need to run for the website to work — they're
two independent things in the same Git repo. See [Chapter 11](./11-whatsapp-bot.md).

---

## The five rules that prevent breakage

If you remember nothing else from this manual, remember these.

1. **Always read [Chapter 03](./03-managing-products.md) before touching a price.**
   Prices live in *three* places per product (catalogue card, JSON-LD schema,
   per-product page). Skip one and search results will lie.

2. **Never edit files in `/products/` or `/use-cases/` by hand.** They're
   generated. Edit `tools/generate_*_pages.py` and re-run the script.

3. **Always re-run the validators before pushing.**
   GitHub Actions runs them automatically on every PR
   (HTML well-formedness, JSON-LD, broken links, sitemap). If a check fails,
   [Chapter 09](./09-deployment.md) explains how to read the output.

4. **The `data-price` and `data-moq` attributes on each product card are not
   cosmetic.** `js/quote-cart.js` reads them. Get them wrong and the buyer's
   WhatsApp message shows the wrong number.

5. **The lead-capture endpoint URL must be the same in two files.** When you
   set up Google Apps Script (Chapter 08), paste the same `/exec` URL into
   `js/main.js` *and* `js/quote-cart.js`. Both have a `FORM_ENDPOINT_URL`
   constant near the top.

6. **The WhatsApp bot's prices live in the Google Sheet, never in code.**
   To change a price, edit the **Pricing** tab of the "Florista Sales"
   Google Sheet. Don't put prices in `prompts.py`, `products.json`, or
   anywhere else — the bot is designed to look them up fresh from the
   Sheet on every quote so it can never invent a number. See
   [Chapter 11](./11-whatsapp-bot.md).

---

## Who maintains what

| File / area | Owned by | Edit frequency |
|-------------|----------|----------------|
| `tools/generate_product_pages.py` (the `PRODUCTS` list) | Owner / dev | Every product change |
| `tools/product_content.py` | Owner / dev | When adding new SKUs |
| `products.html` (catalogue cards) | Owner / dev | Every product change (kept in sync with `PRODUCTS`) |
| `index.html` hero, FAQ, testimonials | Owner | When messaging changes |
| `about.html`, `contact.html`, `wholesale.html` | Owner | Rarely |
| `privacy.html`, `terms.html`, `refund.html` | Owner / lawyer | Annually |
| `css/style.css` | Dev | When the design changes |
| `js/main.js`, `js/quote-cart.js` | Dev | When behaviour changes |
| `images/` | Owner / dev | Every product change |
| `sitemap.xml`, `robots.txt` | Dev | When pages added/removed |
| `wa-bot/` (the WhatsApp sales bot) | Dev | When bot capabilities change |
| Florista Sales sheet → Pricing tab (bot prices) | Owner | Whenever pricing changes |
| `wa-bot/src/florista_bot/prompts.py` (bot tone & rules) | Owner / dev | When tone or escalation policy changes |

---

## Getting help

If something in this manual is wrong or unclear:

1. Open an issue on the repo describing what tripped you up.
2. Or just edit the file and open a PR — these docs are part of the codebase
   and improvements are welcome.

If you break something on the live site:

1. Don't panic. The site is in Git — every state is recoverable.
2. Revert the offending commit on `main`. The old version comes right back.
3. Re-test in a branch before merging again.

Happy shipping.
