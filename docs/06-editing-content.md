# 06 — Editing Site Content

How to update non-product content: hero copy, FAQ, testimonials, footer,
contact info, About page, legal pages.

Most edits in this chapter are **direct text replacements in HTML files**
— no Python, no generator. Open the file in a text editor, find the text
you want to change, change it, save, refresh the browser.

---

## Edit the homepage hero

**File:** `index.html`

Search for the line:
```html
<section class="hero">
```

The hero contains:
- A small "badge" (top-right pill, e.g. "Direct from Nagpur Factory")
- The H1 headline (e.g. "Premium Organza Flowers at Factory Prices")
- A short paragraph below
- Two CTA buttons (WhatsApp + View Catalogue)

Just replace the text inside each tag. The H1 has a `<span>` for the
italic accent words — keep the `<span>` if you want that style.

Don't change the `class` attributes unless you also update the CSS.

---

## Edit the trust strip (3 cards under hero)

**File:** `index.html`

Search for `<section class="trust-strip">`. Three `<div class="trust-item">`
blocks. Each has an icon (Font Awesome class), a heading, and a sentence.

To change an icon, find Font Awesome's class name on
<https://fontawesome.com/icons> and replace `fa-truck-fast` (or whichever)
with the new one.

---

## Edit the "Trusted by" stats strip

**File:** `index.html`

Search for `<section class="trusted-strip">`. Four numbers and labels
(`100+ events delivered`, `25+ cities shipped to`, etc.).

There's a comment in the file telling the owner to update these to
real numbers as the business grows. Approximate is fine.

---

## Edit testimonials

**File:** `index.html`

Search for `<section class="testimonials-section">`. Three
`<div class="testimonial-card">` blocks.

Each card has:
- 5-star line (don't usually change)
- Quote text (`<p class="quote">…</p>`)
- Author block: avatar initial, name, business + city

Templates ship with `[REPLACE — Quote]`, `[Name]`, `[Business, City]`
placeholders that you swap for real testimonials.

There's a long HTML comment above the section explaining how to collect
testimonials by WhatsApp. Read that comment if you've never collected one.

To **add a fourth testimonial**, copy an existing card and paste another
copy. The grid is `auto-fit`, so up to four cards lay out cleanly.

---

## Edit the FAQ

**File:** `index.html`

Search for `<section class="faq-section">`. Each question is a
`<div class="faq-item">` with two children: `<button class="faq-question">`
(the question) and `<div class="faq-answer">` (the answer, which contains
`<div class="faq-answer-inner">`).

To add a new FAQ:

```html
<div class="faq-item">
    <button class="faq-question" aria-expanded="false">
        <span>Your new question?</span>
        <span class="faq-icon"><i class="fas fa-plus"></i></span>
    </button>
    <div class="faq-answer">
        <div class="faq-answer-inner">
            Your answer goes here. You can include
            <a href="contact.html">links</a> and <strong>bold text</strong>.
        </div>
    </div>
</div>
```

The accordion JavaScript in `js/main.js` wires up open/close automatically
based on the class names — no JS edit needed.

---

## Edit the Instagram strip

**File:** `index.html`

Search for `<section class="ig-section">`. The handle and 6-tile preview.

To change the handle:
1. Update the `<a href="https://www.instagram.com/...">` link.
2. Update the displayed handle text inside `.ig-handle small`.

To swap a tile image, replace the file in `images/` (or update the `src`
to a new filename) — there's no Instagram API integration; the tiles are
static images.

---

## Edit the footer (every page)

**Hard truth:** the footer is duplicated across **every** HTML page. Yes,
including the 22 generated product pages and 5 generated use-case pages.

To change the footer site-wide, you have two paths:

### Path A — for root-level pages (8 pages)

Edit each of these files manually:
- `index.html`
- `products.html`
- `about.html`
- `contact.html`
- `wholesale.html`
- `privacy.html`
- `terms.html`
- `refund.html`
- `404.html`

Find `<footer class="site-footer">` near the bottom and edit.

This is tedious. The cookbook ([Chapter 10](./10-cookbook.md)) has a
`sed` one-liner for replacing a phrase across all 9 files.

### Path B — for generated pages (22 + 5 = 27 pages)

Edit the **template** in:
- `tools/generate_product_pages.py` → search for `<footer class="site-footer">`
- `tools/generate_use_case_pages.py` → same

Then re-run the generators.

> If you're doing a major footer rework, consider extracting it into a
> shared HTML snippet that all pages include via JavaScript at runtime
> (or via a small build step). That work is on the roadmap but not
> built today.

---

## Update the WhatsApp / phone number site-wide

This is a meaningful operation — the number `917588447595` (and the
formatted `+91 7588447595` / `7588447595` variants) appear in **dozens**
of places: every footer, the floating WhatsApp button, every "Enquire"
link on a product card, the contact page, the homepage hero, the
generators, the JSON-LD organisation schema.

### The reliable way

```bash
# Replace in every text file under the repo
grep -rl "917588447595" --include="*.html" --include="*.js" --include="*.py" --include="*.json" .

# Use sed to replace (BSD/Mac syntax shown — adjust for Linux)
grep -rl "917588447595" --include="*.html" --include="*.js" --include="*.py" --include="*.json" . \
    | xargs sed -i '' 's/917588447595/<NEW_NUMBER>/g'

# Also update the formatted versions:
grep -rl "7588447595" --include="*.html" --include="*.py" .   # check no stragglers
```

After replacing, **regenerate** the product and use-case pages (which
have the number embedded in dozens of `wa.me/` URLs):

```bash
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py
```

Test by clicking "Enquire for Wholesale" on the home page — should open
WhatsApp to the new number.

---

## Update the email address (when you set one)

There's currently no public email on the site (see [ROADMAP O3](../ROADMAP.md)).
When you add one:

1. Decide on an address (e.g. `hello@theflorista.in`).
2. Add a contact line to:
   - `contact.html` — under the WhatsApp button block
   - The footer of every page (alongside WhatsApp / Instagram)
   - The generators if you want it on per-product pages too
3. Update the JSON-LD `Manufacturer` schema in `index.html`:

   ```html
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "Manufacturer",
     ...
     "email": "hello@theflorista.in",
     ...
   }
   </script>
   ```

---

## Update the factory address

**File:** `contact.html` (currently has Nagpur but no street address)

When the address is decided ([ROADMAP O2](../ROADMAP.md)):

1. Add it to the visible address block on `contact.html`.
2. Add a Google Maps embed:
   ```html
   <iframe src="https://www.google.com/maps/embed?pb=..." …></iframe>
   ```
   (Get the `src` URL from Google Maps → Share → Embed a Map.)
3. Update the JSON-LD `Manufacturer.address` in `index.html` to include
   the street.
4. Add the address to the footer of every page (Path A from the footer
   section above) if you want it on all pages.

---

## Edit the About page

**File:** `about.html`

Standard edit — open in editor, change the text.

There's a sensitive section about whether Florista runs a single factory
or works with a partner network. [ROADMAP item O1](../ROADMAP.md#a-about-page-copy-options)
has two pre-written replacements ready to paste in. Discuss with the
owner before changing this section.

---

## Edit the contact form

**File:** `contact.html`

The form has four fields: company, phone, city, interest. Their IDs are
hardcoded in `js/main.js`'s submit handler:

```javascript
document.getElementById('companyName')
document.getElementById('phone')
document.getElementById('city')
document.getElementById('interest')
```

If you rename a field's `id`, update both files.

To add a new field:
1. Add the `<input>` or `<textarea>` to `contact.html`.
2. In `js/main.js`'s `enquiryForm.addEventListener('submit', ...)` block,
   read the new field's value and include it in the WhatsApp message
   string and the lead-capture payload.

---

## Edit the legal pages

`privacy.html`, `terms.html`, `refund.html` are static prose. Edit
directly. Re-run the validator (or wait for CI) to make sure you didn't
break HTML well-formedness.

If you change the privacy policy materially:
- Update the `<meta name="last-updated">` tag if present (it's nice to
  add one if not).
- Mention the change in a "What changed" line at the top.
- The DPDP Act consent banner already covers analytics — no code change
  needed for routine policy updates.

---

## Edit the wholesale / logistics page

**File:** `wholesale.html`

Sensitive sections to keep accurate:
- Payment terms (currently: 100% advance for first-time buyers, 50/50
  from the third order onwards)
- Shipping & lead times
- Return / refund policy summary
- MOQ rules

These were reconciled with the home FAQ in PR #1 — keep them in sync.
The FAQ on `index.html` references the same policy; if you change one,
change both.

---

## Edit the meta description / page title

Each page has these in its `<head>`:

```html
<title>Florista – Bulk Organza Flower Manufacturer | Nagpur | PAN India</title>
<meta name="description" content="Florista is a premium manufacturer …">
<link rel="canonical" href="https://www.theflorista.in/">
```

Targets:
- **Title:** ≤60 characters (Google truncates around 60).
- **Description:** ≤155 characters.

If you change a page's title or description, also update the matching
Open Graph tags directly below:

```html
<meta property="og:title" content="…">
<meta property="og:description" content="…">
```

For per-product pages, edit the `page_title()` and `meta_description()`
functions in `tools/generate_product_pages.py` and re-run the generator.

---

## Add a new top-level page (e.g. `/blog.html`)

1. Create the file at `Florista/blog.html`.
2. Copy the `<head>` and `<header>` sections from `about.html` (similar
   structure) and adjust the title, description, canonical, and OG tags.
3. Copy the `<footer>` from the same source.
4. Build out the page content in between.
5. Add the page to the main nav of every other page:

   ```html
   <nav class="main-nav">
       <a href="index.html" class="nav-link">Home</a>
       <a href="products.html" class="nav-link">Products</a>
       <a href="blog.html" class="nav-link">Blog</a>     <!-- new -->
       ...
   </nav>
   ```

   This is hand-maintained per page (see footer note above).

6. Add the page to `sitemap.xml`:
   ```xml
   <url>
       <loc>https://www.theflorista.in/blog.html</loc>
       <lastmod>2026-05-28</lastmod>
       <changefreq>monthly</changefreq>
       <priority>0.6</priority>
   </url>
   ```

7. Optionally add to `robots.txt` if you want extra control.

---

## Edit the cookie consent banner

**File:** `js/main.js`

Search for `DPDP Act Cookie / Analytics Consent Banner`. The banner text,
button labels, and styles are all defined inline in the JS block.

If you change "Accept" / "Decline" labels or the explanation copy, do it
in the `banner.innerHTML = …` block.

If you change the styling, edit the `<style>` template just below.

The behaviour (default-deny analytics until accept) shouldn't be changed
without legal sign-off — it's the DPDP Act compliance.

---

Next chapter: [07 — Styling & Branding →](./07-styling-and-branding.md)
