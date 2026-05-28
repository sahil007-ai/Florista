# 05 — Sales & Discounts

The site doesn't have a built-in discount engine today (no checkout
happens on the site — every order finishes via WhatsApp). But you can
still run sales by combining the building blocks below.

This chapter walks you through three escalating options:

1. **Site-wide announcement banner** — easiest, no price changes.
2. **Strikethrough sale prices on individual products** — more work,
   most visual impact.
3. **Slab pricing chips** — for "buy more, save more" wholesale tiers.

Pick the one that matches the campaign you're running. They can be
combined.

---

## Option 1 — Site-wide announcement banner

A thin, dismissible bar at the top of every page that says something like
"🎉 Monsoon Sale — Flat 15% off all 60" Giant Flora orders. Use code
RAINY15 on WhatsApp."

This is the **cheapest, fastest** way to advertise a sale. No product
prices change. Buyers mention the code on WhatsApp and you apply it
manually when quoting.

### Step 1 — Add the banner CSS

Edit `css/style.css` and append at the bottom:

```css
/* ── Sale Announcement Banner ───────────────────────────────── */
.sale-banner {
    background: linear-gradient(135deg, var(--color-primary-dark) 0%, #b66a8e 100%);
    color: white;
    text-align: center;
    padding: 10px 20px;
    font-size: 0.92rem;
    font-weight: 500;
    position: relative;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
}
.sale-banner a {
    color: white;
    text-decoration: underline;
    font-weight: 600;
}
.sale-banner-close {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 0.85rem;
    line-height: 1;
    flex-shrink: 0;
}
.sale-banner-close:hover {
    background: rgba(255, 255, 255, 0.15);
}
.sale-banner.is-dismissed { display: none; }
@media (max-width: 600px) {
    .sale-banner { font-size: 0.82rem; padding: 8px 14px; }
}
```

### Step 2 — Add the banner markup to every page

The banner sits **directly inside `<body>` before `<header>`**, so it
appears above the navigation.

For each page (`index.html`, `products.html`, `about.html`, `contact.html`,
`wholesale.html`, `privacy.html`, `terms.html`, `refund.html`), add:

```html
<body>
    <!-- ── Sale Banner ── Edit the message and dates here ── -->
    <div class="sale-banner" id="sale-banner-monsoon-2026">
        <span>
            <i class="fas fa-bolt"></i>
            <strong>Monsoon Sale</strong> — Flat 15% off all 60"
            Giant Flora orders until 30 June.
            <a href="https://wa.me/917588447595?text=Hi%20Florista%2C%20I%27d%20like%20to%20use%20code%20RAINY15"
               target="_blank">
                Mention code <strong>RAINY15</strong> on WhatsApp →
            </a>
        </span>
        <button type="button" class="sale-banner-close"
                aria-label="Dismiss"
                onclick="document.getElementById('sale-banner-monsoon-2026').classList.add('is-dismissed'); localStorage.setItem('sale-banner-monsoon-2026', 'dismissed')">
            ×
        </button>
    </div>

    <header class="site-header">
    ...
```

For per-product pages and use-case pages, the same banner can be added
to the generator templates (`PAGE_TEMPLATE` in
`tools/generate_product_pages.py` and `tools/generate_use_case_pages.py`).
Add the same `<div>` block right after `<body>`.

> **Tip:** Give every banner a **unique `id`** that includes the
> campaign name (`sale-banner-monsoon-2026`, `sale-banner-diwali-2026`).
> The localStorage dismiss key uses the same id, so a buyer who dismisses
> one banner doesn't keep that banner permanently dismissed when you run
> the next campaign.

### Step 3 — Make the banner remember dismissal across reloads

Add this snippet to the very bottom of `js/main.js`:

```javascript
/* ── Sale-banner dismissal memory ────────────────────────────── */
document.querySelectorAll('.sale-banner').forEach((banner) => {
    if (banner.id && localStorage.getItem(banner.id) === 'dismissed') {
        banner.classList.add('is-dismissed');
    }
});
```

Now if a buyer dismisses the banner on `index.html`, it stays dismissed
on every other page.

### Step 4 — When the sale ends

Easy. Either:
- Edit the banner markup to remove the `<div class="sale-banner">` block
  from each page.
- Or change the message and code for the next campaign.

Don't forget to remove it from the generator templates too if you added
it there.

---

## Option 2 — Strikethrough sale prices on individual products

For an actual price reduction visible on each product card, you'll show
the old price struck through next to the new price. Visually:

> ~~Rs. 2,500~~ **Rs. 2,125** *(15% off)*

This requires editing prices in the same three places as a permanent
price change ([Recipe 1 in Chapter 03](./03-managing-products.md#recipe-1--change-the-price-of-an-existing-product))
**plus** carrying the original price as a "compare-at" value.

### Step 1 — Extend the product data model

In `tools/generate_product_pages.py`, add two optional fields to the
`PRODUCTS` entries you want to put on sale:

```python
{
    "slug": "60-inch-giant-flora",
    ...
    "price_min": 2125,                  # current sale price (numeric)
    "price_max": 2125,
    "price_display": "Rs. 2,125",       # display string
    "compare_at_price": 2500,           # ← NEW: the strikethrough price
    "sale_label": "15% off",            # ← NEW: optional label
    ...
},
```

Products without these two fields render as normal — backward compatible.

### Step 2 — Update the per-product page template

Find the price block in `PAGE_TEMPLATE` in
`tools/generate_product_pages.py`. It currently looks something like:

```html
<div class="pd-price">{price_display_e}</div>
```

Change it to conditionally render the strikethrough:

```html
<div class="pd-price">
    {compare_at_html}
    <span class="pd-price-now">{price_display_e}</span>
    {sale_label_html}
</div>
```

And add a helper to the script (near `meta_description()`):

```python
def price_block_parts(p: dict) -> tuple[str, str]:
    """Return (compare_at_html, sale_label_html). Empty strings if no sale."""
    compare = p.get("compare_at_price")
    label = p.get("sale_label", "")
    if not compare or compare <= p["price_min"]:
        return "", ""
    compare_html = (
        f'<span class="pd-price-was">Rs. {compare:,.0f}</span>'
    )
    label_html = (
        f'<span class="pd-price-tag">{html.escape(label)}</span>'
        if label else ""
    )
    return compare_html, label_html
```

Call it in `render_page()`:

```python
compare_at_html, sale_label_html = price_block_parts(p)
```

…and pass into the format dict.

### Step 3 — Add the strikethrough CSS

Append to `css/style.css`:

```css
.pd-price { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.pd-price-was {
    text-decoration: line-through;
    color: var(--color-gray);
    font-size: 0.95rem;
    font-weight: 500;
}
.pd-price-now {
    color: var(--color-primary-dark);
    font-weight: 700;
}
.pd-price-tag {
    background: #e74c3c;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 50px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* On catalogue cards too */
.product-card .card-price-was {
    text-decoration: line-through;
    color: var(--color-gray);
    font-weight: 500;
    margin-right: 8px;
    font-size: 0.85rem;
}
.product-card .card-sale-tag {
    background: #e74c3c;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 50px;
    margin-left: 6px;
    letter-spacing: 0.05em;
}
```

### Step 4 — Update the catalogue card in `products.html`

For each on-sale product, edit the card's price block from:

```html
<div class="card-footer-row">
    <span class="card-price">Rs. 2,500</span>
    ...
</div>
```

…to:

```html
<div class="card-footer-row">
    <span>
        <span class="card-price-was">Rs. 2,500</span>
        <span class="card-price">Rs. 2,125</span>
        <span class="card-sale-tag">15% off</span>
    </span>
    ...
</div>
```

### Step 5 — Update `data-price` (this controls the cart)

The quote cart reads `data-price` for line-item totals. Make sure the
attribute reflects the **sale price**, not the original:

```html
<div class="product-card reveal" data-size="60" data-price="2125" data-moq="5">
```

### Step 6 — Update the JSON-LD ItemList in `products.html`

For sale items, the schema lets you express both prices using
`PriceSpecification`:

```json
"offers": {
    "@type": "Offer",
    "priceCurrency": "INR",
    "price": 2125,
    "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "priceType": "https://schema.org/ListPrice",
        "price": 2500,
        "priceCurrency": "INR"
    },
    "availability": "https://schema.org/InStock",
    "validThrough": "2026-06-30",
    "seller": { "@type": "Organization", "name": "The Florista Flowers" }
}
```

Note the `validThrough` date — Google uses it to stop showing the sale
in search results after the campaign ends.

### Step 7 — Regenerate, test, ship

```bash
python3 tools/generate_product_pages.py
python3 -m http.server 8000
# Open the catalogue and a sale product. Verify the strikethrough renders.
```

Commit and PR.

### Step 8 — When the sale ends

1. Remove `compare_at_price` and `sale_label` from each `PRODUCTS` entry.
2. Optionally restore the original price in `price_min`/`price_max` /
   `price_display` (or leave at the lower price if it was a permanent
   reduction).
3. Regenerate.
4. In `products.html`, remove the `card-price-was` and `card-sale-tag`
   spans and update `data-price`.
5. In the JSON-LD, remove `priceSpecification` and `validThrough`.

---

## Option 3 — Slab pricing chips (wholesale tiers)

For "buy more, save more" wholesale pricing, e.g.:

| Quantity | Per piece |
|----------|-----------|
| 10 – 49 pcs | Rs. 425 |
| 50 – 99 pcs | Rs. 400 |
| 100+ pcs | Rs. 375 |

This is a recurring policy, not a time-bound sale. It lives on the page
permanently.

The roadmap already lists slab pricing as planned ([item O6](../ROADMAP.md)).
Sketch for when it gets built:

### Step 1 — Extend `PRODUCTS`

```python
{
    "slug": "24-inch-wedding-touch",
    ...
    "price_slabs": [
        {"min_qty": 10,  "price": 425, "label": "10–49 pcs"},
        {"min_qty": 50,  "price": 400, "label": "50–99 pcs"},
        {"min_qty": 100, "price": 375, "label": "100+ pcs"},
    ],
},
```

### Step 2 — Render slabs on the per-product page

In `PAGE_TEMPLATE`, add a slab block under the price:

```html
{slab_block_html}
```

…where `slab_block_html` (built in Python) renders something like:

```html
<div class="pd-slabs">
    <h4>Bulk pricing</h4>
    <ul>
        <li><strong>10–49 pcs</strong> — Rs. 425/pc</li>
        <li><strong>50–99 pcs</strong> — Rs. 400/pc</li>
        <li><strong>100+ pcs</strong> — Rs. 375/pc</li>
    </ul>
</div>
```

### Step 3 — Show a chip on catalogue cards

In `products.html`, add a chip near the MOQ chip:

```html
<span class="moq-chip"><i class="fas fa-box-open"></i> MOQ 10 pcs</span>
<span class="slab-chip"><i class="fas fa-percent"></i> Slab pricing from Rs. 375</span>
```

Style the chip in CSS to match the look of `moq-chip`.

### Step 4 — Cart logic (advanced)

The current cart uses a single `data-price`. To make the cart auto-apply
the right slab, you'd need to:

1. Embed slab data on the card as `data-slabs='[{...}]'`.
2. In `js/quote-cart.js`'s `setQty()`, look up the slab matching the
   current quantity and update the line price.

This is more work than the other options. Until built, you can keep
slabs as informational only — buyers and Florista agree the slab during
WhatsApp negotiation.

---

## Option 4 — Coupon codes (simplest of all)

If a slab system is overkill for your campaign, just publish a code:

> "**Use code FESTIVE15 on WhatsApp for 15% off** on orders of 50+ pieces."

Implement it as either:
- A site-wide banner (Option 1 above), or
- A line in the FAQ section on `index.html`

There's nothing to validate in code — you (or the WhatsApp bot) recognise
the code when the buyer mentions it.

---

## When *not* to run a sale on this site

A few situations where putting a sale on the site is the wrong move:

- **You only intend the discount for one buyer.** Send the code privately
  on WhatsApp; don't put it on the site.
- **The discount changes with relationship/volume.** That's negotiated
  pricing, not a public sale. Keep it off the public site.
- **The sale is for slow-moving stock.** Better to mention it casually in
  WhatsApp replies — public discounting on the catalogue can train regular
  buyers to wait for sales before placing orders.

A public site sale is most useful for:
- Acquiring new buyers (a campaign tied to ads or social posts).
- Creating urgency around a launch / festival window.
- Clearing a single SKU you genuinely want to clear.

---

## Sales sanity checklist (before going live)

- [ ] All sale prices match across the three places (PRODUCTS list, card
      markup, JSON-LD).
- [ ] `data-price` on each card reflects the **sale** price, not the
      original.
- [ ] If using strikethrough, `validThrough` is set in the JSON-LD with
      the actual end date.
- [ ] The banner has a unique `id` that includes the campaign name.
- [ ] Banner mentions the WhatsApp code (if any) in the link text.
- [ ] You've tested the cart: adding a sale product → drawer shows the
      sale price → "Send Quote" message reflects the sale price.
- [ ] You've added a calendar reminder to take the banner down when the
      sale ends.

---

Next chapter: [06 — Editing Site Content →](./06-editing-content.md)
