# 03 — Managing Products

This is the most important chapter in the manual. **Read it fully before
adding, editing, or removing any product.** Skipping the steps below is
how prices end up wrong on the live site or in Google search results.

---

## The mental model: three files per product

Each product appears in **three** places, all of which must agree:

```
                     ┌─────────────────────────────────────────┐
                     │   tools/generate_product_pages.py       │
                     │   (PRODUCTS list — single source         │
                     │    of truth for the SEO pages)          │
                     └─────────────────────────────────────────┘
                                       │
                                       │  python3 tools/generate_product_pages.py
                                       ▼
                     ┌─────────────────────────────────────────┐
                     │   /products/<slug>.html                 │
                     │   (generated SEO landing page,          │
                     │    do NOT edit by hand)                 │
                     └─────────────────────────────────────────┘

                     ┌─────────────────────────────────────────┐
                     │   products.html                         │  <- HAND-MAINTAINED
                     │   ① The card markup (.product-card)     │
                     │   ② The JSON-LD ItemList at the top     │
                     └─────────────────────────────────────────┘

                     ┌─────────────────────────────────────────┐
                     │   tools/product_content.py              │  <- expressive copy
                     │   (CONTENT_BY_SLUG — narrative,         │
                     │    built_for, pairs_with, etc.)         │
                     └─────────────────────────────────────────┘
```

Every product has:

| Where | What it controls |
|-------|------------------|
| `tools/generate_product_pages.py` → `PRODUCTS` list | Price, MOQ, size, shade count, image prefix, slug |
| `tools/product_content.py` → `CONTENT_BY_SLUG` | The rich narrative copy on the per-product page |
| `products.html` → `<div class="product-card" …>` | The catalogue card buyers click on |
| `products.html` → JSON-LD `ItemList` block | The SEO schema that Google reads |

**If you change the price in only one place, the others lie.** Search
results, the cart, and the catalogue card will disagree with each other
until you fix all three.

---

## The golden rule

> Always edit prices and MOQs in the `PRODUCTS` list **first**, regenerate,
> then mirror the change to `products.html` (both the card markup and the
> JSON-LD).

This order ensures the catalogue and per-product pages can never drift
apart by accident.

---

## Recipe 1 — Change the price of an existing product

Say you want to bump the **24" Wedding Touch** price from Rs. 375 to Rs. 425.

### Step 1 — Edit `tools/generate_product_pages.py`

Open the file. Find the entry for the product (search for its `slug`):

```python
{
    "slug": "24-inch-wedding-touch",
    "name": '24" Wedding Touch',
    ...
    "price_min": 375,        # ← change this
    "price_max": 375,        # ← and this (same value if single price)
    "price_display": "Rs. 375",   # ← and this (the display string)
    ...
},
```

Update all three price-related fields.

> **Why three fields?** `price_min` and `price_max` go into the JSON-LD
> schema (`Offer` if equal, `AggregateOffer` if a range). `price_display`
> is the human-readable string shown on the page. They're separate so a
> "From Rs. 445" display string can have a `price_min` of `445` for SEO
> while letting the copy stay friendly.

### Step 2 — Regenerate the per-product pages

```bash
python3 tools/generate_product_pages.py
```

This rewrites `/products/24-inch-wedding-touch.html` with the new price.
`git status` will show it as modified.

### Step 3 — Update `products.html` to match

Open `products.html` and find the matching card. Search for the product
name (`24" Wedding Touch`):

```html
<div class="product-card reveal" data-size="24" data-price="375" data-moq="10">
    ...
    <div class="card-price">Rs. 375</div>
    ...
</div>
```

Update **two** spots:

1. The `data-price` attribute (used by the quote cart)
2. The visible `<div class="card-price">` text

```html
<div class="product-card reveal" data-size="24" data-price="425" data-moq="10">
    ...
    <div class="card-price">Rs. 425</div>
    ...
</div>
```

### Step 4 — Update the JSON-LD ItemList in `products.html`

Scroll to the top of `products.html` (the `<head>` section). Find the
`<script type="application/ld+json">` block — it lists every product.
Search for the same product name and update its `price`:

```json
{
  "@type": "ListItem",
  "position": 3,
  "item": {
    "@type": "Product",
    "name": "24\" Wedding Touch",
    ...
    "offers": {
      "@type": "Offer",
      "priceCurrency": "INR",
      "price": 425,    // ← updated
      ...
    }
  }
},
```

> **Note:** If `price_min === price_max`, use `"@type": "Offer"` with a
> single `"price"` field. If they differ, use `"@type": "AggregateOffer"`
> with `"lowPrice"` and `"highPrice"`. Existing entries already follow
> this pattern — copy the shape of a sibling.

### Step 5 — Quick sanity check

Reload `products.html` in your browser. The card should show the new
price. Click "Add to Quote" → open the cart → the line item should show
the new price too.

Open `/products/24-inch-wedding-touch.html` directly. The price should
match.

### Step 6 — Commit

```bash
git add tools/generate_product_pages.py products.html products/24-inch-wedding-touch.html
git commit -m "update 24\" Wedding Touch price to Rs. 425"
```

Open a PR. CI will run the validators. If they pass, merge it.

---

## Recipe 2 — Add a brand new product

Adding a new SKU touches more places than a price change but the order is
the same: **data first, regenerate, mirror.**

### Step 1 — Add product photos to `images/`

Name them `product_<your_prefix>_1.webp`, `_2.webp`, etc.

- The prefix should be lowercase, snake_case.
- Always WebP format (see [Ch 04](./04-images-and-media.md) for why).
- Indices start at 1 and should be contiguous (`1, 2, 3, …`). If a number
  is missing, that's fine — note it in `image_indices` below.
- Aim for ≤200 KB per image. Most photos in the repo are 20–60 KB.

Example: for a new SKU "Sunset Petals," save photos as
`product_sunset_petals_1.webp`, `product_sunset_petals_2.webp`, etc.

### Step 2 — Add an entry to `PRODUCTS` in `tools/generate_product_pages.py`

Find the section comment that matches the category
(`# ── Organza Flowers`, `# ── Premium & Specialty`, or `# ── Theme & Events`)
and add a dict at the end of that section:

```python
{
    "slug": "sunset-petals",                      # URL slug, kebab-case, must be unique
    "name": "Sunset Petals",                      # display name
    "category": "premium",                        # one of: organza, premium, theme
    "size_inch": 24,                              # numeric size used for filtering
    "size_label": '24"',                          # human label
    "size_meta": "61 cm",                         # metric size for body copy
    "shade_count": 6,                             # number of colour variants
    "moq": 10,                                    # minimum order quantity
    "price_min": 425,                             # numeric, INR
    "price_max": 425,                             # numeric, INR
    "price_display": "Rs. 425",                   # pretty string
    "image_prefix": "product_sunset_petals",      # filename prefix in /images/
    "image_indices": [1, 2, 3, 4],                # which numbered photos exist
    "tagline": "Warm-toned 6-shade fabric flower",  # one-liner for the catalogue card
    "use_case": "warm-toned reception backdrops and sunset-themed weddings",
                                                  # plugged into the description copy
},
```

### Step 3 — (Optional but recommended) Add expressive copy

Open `tools/product_content.py` and add a `CONTENT_BY_SLUG` entry for the
new slug. Each entry has six fields — see the existing entries for the
voice and length:

```python
"sunset-petals": {
    "narrative": [
        "Two paragraphs of warm, specific copy about the piece...",
        "Second paragraph about colour, scale, who it's for...",
    ],
    "built_for": [
        "Use case 1.",
        "Use case 2.",
        "Use case 3.",
        "Use case 4.",
    ],
    "pairs_with":
        "One sentence on what it layers with on a real backdrop.",
    "craft_note":
        "One short sensory or production detail unique to this piece.",
    "hook_headline": "Question or hook headline?",
    "contact_hook":
        "1–2 sentences inviting a WhatsApp chat about THIS product specifically.",
},
```

If you skip this step, the per-product page will render with a generic
fallback — still functional, just less expressive.

### Step 4 — Regenerate

```bash
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py    # only needed if you reference
                                            # the new slug from a use-case
```

A new file `/products/sunset-petals.html` should appear.

### Step 5 — Add a card to `products.html`

Open `products.html`. Find the right category section
(`<!-- ── Organza Flowers ── -->`, etc.) inside the `<main>` block.
Add a new `<div class="product-card">` block. Copy a similar existing
card and adjust the values.

Minimum required attributes (used by the quote cart):

```html
<div class="product-card reveal"
     data-id="sunset-petals"
     data-size="24"
     data-price="425"
     data-moq="10">

    <div class="card-img-wrap"
         onclick="openLightbox('images/product_sunset_petals_1.webp', this)">
        <img class="main-img"
             src="images/product_sunset_petals_1.webp"
             alt="Sunset Petals" loading="lazy">
        <div class="variant-badge">6 shades</div>
    </div>

    <div class="thumb-strip">
        <img src="images/product_sunset_petals_1.webp" alt="" class="active">
        <img src="images/product_sunset_petals_2.webp" alt="">
        <img src="images/product_sunset_petals_3.webp" alt="">
        <img src="images/product_sunset_petals_4.webp" alt="">
    </div>

    <div class="card-body">
        <h3>
            <a class="card-title-link" href="products/sunset-petals.html">
                Sunset Petals
            </a>
        </h3>
        <p class="desc">Warm-toned 6-shade fabric flower</p>
        <span class="moq-chip"><i class="fas fa-box-open"></i> MOQ 10 pcs</span>
        <div class="card-footer-row">
            <span class="card-price">Rs. 425</span>
            <a href="https://wa.me/917588447595?text=Enquiry%20for%20Sunset%20Petals"
               class="enquire-btn" target="_blank">
                <i class="fab fa-whatsapp"></i> Enquire
            </a>
        </div>
    </div>
</div>
```

The `data-id` should match the slug. The `href` of the title link points
to the generated per-product page.

### Step 6 — Add the product to the JSON-LD ItemList in `products.html`

In the `<script type="application/ld+json">` at the top of `products.html`:

1. Append a new `ListItem` block (copy the shape of an existing one).
2. Set `position` to the next number in sequence.
3. Update `numberOfItems` near the top of the list to match.

```json
{
  "@type": "ListItem",
  "position": 23,
  "item": {
    "@type": "Product",
    "name": "Sunset Petals",
    "image": "https://www.theflorista.in/images/product_sunset_petals_1.webp",
    "description": "Wholesale handcrafted decor flower by Florista, Nagpur. Minimum order quantity: 10 pieces. PAN India delivery.",
    "brand": { "@type": "Brand", "name": "Florista" },
    "category": "Wholesale Decor Flowers",
    "url": "https://www.theflorista.in/products.html#card-sunset-petals",
    "offers": {
      "@type": "Offer",
      "priceCurrency": "INR",
      "price": 425,
      "availability": "https://schema.org/InStock",
      "seller": { "@type": "Organization", "name": "The Florista Flowers" }
    }
  }
}
```

### Step 7 — Update the sitemap

Open `sitemap.xml` and add a `<url>` entry for the new page:

```xml
<url>
    <loc>https://www.theflorista.in/products/sunset-petals.html</loc>
    <lastmod>2026-05-28</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
</url>
```

### Step 8 — Test, commit, PR

```bash
python3 -m http.server 8000
```

Visit:
- <http://localhost:8000/products.html> — your new card should appear
- <http://localhost:8000/products/sunset-petals.html> — the per-product page should render
- Add it to the cart → check the qty and price in the drawer

Then commit and PR. CI will catch any broken links or invalid JSON.

---

## Recipe 3 — Edit a product's name, MOQ, or shade count

These are smaller-than-a-rename edits. The same three-place rule applies:

1. Edit the field in the `PRODUCTS` list.
2. Regenerate (`python3 tools/generate_product_pages.py`).
3. Update the matching card in `products.html` (and the JSON-LD if it's the name).

Specifically:

| Change | Where in `PRODUCTS` | Where in `products.html` |
|--------|---------------------|--------------------------|
| Name | `name` | `<h3>` text + `alt` attributes + JSON-LD `name` |
| MOQ | `moq` | `data-moq` attribute + visible `MOQ X pcs` chip |
| Shade count | `shade_count` | `<div class="variant-badge">N shades</div>` |
| Tagline | `tagline` | `<p class="desc">…</p>` |
| Size label | `size_label` | (description copy in body — usually safe to leave) |

---

## Recipe 4 — Rename a product (change the slug)

Renaming a slug means changing its URL. Search engines have indexed the
old URL, so you need to redirect.

1. Decide on the new slug. Slugs must be unique, kebab-case, and stable.
2. Update `slug` in the `PRODUCTS` list.
3. If you have an entry in `CONTENT_BY_SLUG` (`tools/product_content.py`),
   rename its key too.
4. Regenerate.
5. **Delete the old generated file** — `git rm products/<old-slug>.html`.
   The generator only creates new files; it doesn't clean up renamed ones.
6. In `products.html`:
   - Update the card's `data-id` and the title link's `href`.
   - Update the JSON-LD `url` field.
7. Update `sitemap.xml`:
   - Replace the old URL with the new one.
8. **Add a redirect** for the old URL. Two options:

   a. **Static-host redirect** — preferred. If the site is on Netlify,
      add a line to `_redirects`. If it's on Cloudflare Pages, the same
      file works. If it's on plain GitHub Pages, you can't do server-side
      redirects, so use option (b).

   b. **Meta-refresh page** — keep a tiny stub at the old URL:

      ```html
      <!DOCTYPE html>
      <html><head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url=/products/new-slug.html">
        <link rel="canonical" href="https://www.theflorista.in/products/new-slug.html">
        <title>Redirecting…</title>
      </head><body>
        <p>This product has moved. <a href="/products/new-slug.html">Continue</a>.</p>
      </body></html>
      ```

      Save this as `products/<old-slug>.html` (overwriting the deleted
      generated file).

9. Commit, PR, merge.

> **Avoid renaming if you can.** Stable slugs preserve SEO. Only rename
> if the old slug is genuinely misleading.

---

## Recipe 5 — Remove a product (out of stock or discontinued)

If you just want to **temporarily hide** a product, the cleanest pattern is:

1. In the card markup in `products.html`, add an `is-hidden` class:

   ```html
   <div class="product-card reveal is-hidden" …>
   ```

   (The CSS rule `.product-card.is-hidden { display: none !important; }`
   already exists.)

2. Don't delete the generated page or the JSON-LD entry. Buyers who land
   on the per-product URL from search can still see it.
3. To bring it back, just remove the `is-hidden` class.

To **permanently remove** a product:

1. Delete its entry from `PRODUCTS` in `tools/generate_product_pages.py`.
2. Delete its entry from `CONTENT_BY_SLUG` in `tools/product_content.py`
   (if present).
3. Run the generator. The old `/products/<slug>.html` file is **not**
   automatically deleted — `git rm products/<slug>.html` it.
4. Remove the card from `products.html`.
5. Remove the entry from the JSON-LD ItemList. Renumber subsequent
   `position` values, and decrement `numberOfItems`.
6. Remove the URL from `sitemap.xml`.
7. Add a meta-refresh stub at the old URL pointing to `/products.html`,
   so search hits don't 404.
8. Check `tools/generate_use_case_pages.py` — if the slug was in any
   `recommended_slugs` list, remove it there too.

---

## Recipe 6 — Reorder products on the catalogue

Products on `products.html` appear in the order their cards are written.
There is no automatic sort by price or popularity in the markup — only the
runtime sort dropdown.

To change the default order:

1. Cut and paste the `<div class="product-card">…</div>` blocks into the
   order you want them.
2. Update the corresponding JSON-LD ItemList: re-order the `ListItem`
   entries to match, and renumber `position` from 1.

> The runtime sort (`Newest`, `Price low → high`, etc.) is handled by
> `js/main.js` via the `#sort-select` dropdown. Default is whatever's in
> the markup.

---

## Recipe 7 — Add a category

The site has three categories (`organza`, `premium`, `theme`). Adding a
fourth requires:

1. In `tools/generate_product_pages.py`, add the new category to:
   - `CATEGORY_LABELS` (singular, for body copy)
   - `CATEGORY_NAMES` (plural, for headings)
   - `CATEGORY_ICONS` (Font Awesome class)
2. In `products.html`:
   - Add a new sidebar nav link in `.cat-sidebar`.
   - Add a new `<section class="category-section" id="<slug>">…</section>`
     block in the right place.
   - Add the new category to the `cat-toolbar` size/MOQ filter chips
     if it should be filterable.
3. Run the generator.
4. Add product entries with the new category value.

---

## Common mistakes (the ones that get caught in code review)

**❌ Edited the price on the per-product page directly.**
You'll lose the change next time the generator runs. Always edit the
`PRODUCTS` list.

**❌ Changed `data-price` but forgot the visible `<div class="card-price">`.**
The cart will show one number, the card another. Buyers notice.

**❌ Added a new product to `products.html` but not to `sitemap.xml`.**
Google won't index it as quickly. Always add the URL to the sitemap.

**❌ Changed a slug without redirecting the old URL.**
Existing search results 404. Lost SEO.

**❌ Forgot to update `numberOfItems` in the catalogue JSON-LD.**
Validators won't catch it (it's still valid JSON), but it's a hint to
search engines about catalogue size. Keep it accurate.

**❌ Image filename and `image_prefix` don't match.**
The page will render with a broken image. Test the per-product page in
the browser after every change.

---

## Quick reference: which file controls what

| You want to change… | Edit this file | Then run |
|---------------------|---------------|----------|
| The price | `tools/generate_product_pages.py` (PRODUCTS) + `products.html` (card + JSON-LD) | `python3 tools/generate_product_pages.py` |
| The MOQ | `tools/generate_product_pages.py` (PRODUCTS) + `products.html` (card) | `python3 tools/generate_product_pages.py` |
| The narrative on the per-product page | `tools/product_content.py` (CONTENT_BY_SLUG) | `python3 tools/generate_product_pages.py` |
| The catalogue tagline | `tools/generate_product_pages.py` (PRODUCTS.tagline) + `products.html` (card desc) | `python3 tools/generate_product_pages.py` |
| The product image | Add WebP to `images/` + update `image_indices` if needed | `python3 tools/generate_product_pages.py` |
| The shade count badge | `tools/generate_product_pages.py` (PRODUCTS.shade_count) + `products.html` (card badge) | `python3 tools/generate_product_pages.py` |
| Hide a product temporarily | Add `is-hidden` class to its card in `products.html` | (nothing) |
| Reorder cards | `products.html` (cut/paste the card blocks + renumber JSON-LD) | (nothing) |

---

Next chapter: [04 — Images & Media →](./04-images-and-media.md)
