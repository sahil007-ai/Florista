# 10 — Cookbook (Quick Recipes)

One-page reference for the most common tasks. Each recipe is the smallest
possible set of steps. For background, follow the cross-references back
to the relevant chapter.

> **Print this page or bookmark it.** It's the everyday companion to the
> rest of the manual.

---

## Daily Git workflow

```bash
# Start fresh
git checkout main
git pull

# Branch
git checkout -b <branch-name>

# Edit, save, test in browser
python3 -m http.server 8000

# Commit & push
git add -A
git commit -m "<short verb-led message>"
git push origin <branch-name>
# Open PR on GitHub
```

---

## Change a product's price

(See [Ch 03](./03-managing-products.md#recipe-1--change-the-price-of-an-existing-product) for the full version.)

1. Edit `tools/generate_product_pages.py` → find the product → update
   `price_min`, `price_max`, `price_display`.
2. Run:
   ```bash
   python3 tools/generate_product_pages.py
   ```
3. Edit `products.html` → find the card → update `data-price` AND visible
   `<div class="card-price">`.
4. Edit `products.html` → top JSON-LD ItemList → update the `price` for
   this product.
5. Commit, push, PR.

---

## Add a brand-new product

(See [Ch 03 Recipe 2](./03-managing-products.md#recipe-2--add-a-brand-new-product) for full version.)

1. Save photos to `images/product_<prefix>_<n>.webp`.
2. Add a `PRODUCTS` entry in `tools/generate_product_pages.py`.
3. Optional: add expressive copy to `tools/product_content.py`.
4. Regenerate:
   ```bash
   python3 tools/generate_product_pages.py
   ```
5. Add a `<div class="product-card">` block to `products.html`.
6. Add a `ListItem` to `products.html`'s JSON-LD ItemList. Increment
   `numberOfItems`.
7. Add a `<url>` entry to `sitemap.xml`.
8. Commit, push, PR.

---

## Hide a product temporarily

In `products.html`, add `is-hidden` to the card class list:

```html
<div class="product-card reveal is-hidden" …>
```

---

## Change the WhatsApp number site-wide

```bash
# 1. Replace in every text file
grep -rl "917588447595" --include="*.html" --include="*.js" --include="*.py" --include="*.json" . \
    | xargs sed -i '' 's/917588447595/<NEW>/g'

# Linux: drop the '' after -i
# 2. Regenerate
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py

# 3. Test by clicking "Enquire for Wholesale" on the home page
```

---

## Run a sale (announcement banner only)

(See [Ch 05 Option 1](./05-sales-and-discounts.md#option-1--site-wide-announcement-banner) for full version.)

1. Add the `.sale-banner` CSS to `css/style.css` (one-time).
2. Add the `<div class="sale-banner" id="sale-banner-<campaign>">…</div>`
   block right after `<body>` in each root-level page.
3. Optionally add the same to the generator templates so per-product /
   use-case pages also show it.
4. Add the dismissal-memory snippet to `js/main.js` (one-time).
5. When the sale ends, remove the markup.

---

## Update the homepage hero copy

Edit `index.html` → search for `<section class="hero">` → change text
inside the `<h1>`, `<p>`, and badge.

---

## Add an FAQ entry

Edit `index.html` → search for `<section class="faq-section">` → copy an
existing `<div class="faq-item">` block and edit the question + answer.

The accordion JS auto-wires up. No JS edit needed.

---

## Replace a testimonial

Edit `index.html` → search for `<section class="testimonials-section">`.
Find the card with `[REPLACE]` placeholders. Update:
- `.quote` text
- `.avatar` initial
- `.who strong` (name)
- `.who span` (business + city)

---

## Change a colour site-wide

Edit `css/style.css` → top of file → `:root` block → change the
`--color-primary-dark` (or whichever) value. Save. Refresh.

The whole site picks up the new colour because every component uses the
variable.

(See [Ch 07](./07-styling-and-branding.md#the-brand-palette) for the
palette reference.)

---

## Wire up the lead-capture sheet

(See [Ch 08](./08-analytics-and-leads.md#layer-3--apps-script-lead-capture-sheet) for context.)

1. Follow the setup at [`.kiro/steering/lead-capture.md`](../.kiro/steering/lead-capture.md).
2. Copy the resulting `/exec` URL.
3. Paste into **both** files:
   - `js/main.js` → the `FORM_ENDPOINT_URL` constant near the top.
   - `js/quote-cart.js` → the `FORM_ENDPOINT_URL` constant inside the IIFE.

Both URLs must be identical. Don't paste only one.

---

## Switch GA4 properties

```bash
grep -rl "G-T5GR1DL2G0" . | xargs sed -i '' 's/G-T5GR1DL2G0/G-NEWID/g'
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py
```

---

## Find every place a hardcoded value lives

```bash
# WhatsApp number
grep -rn "917588447595" --include="*.html" --include="*.js" --include="*.py" .

# Domain
grep -rn "theflorista.in" --include="*.html" --include="*.js" --include="*.py" .

# GA4 property
grep -rn "G-T5GR1DL2G0" --include="*.html" --include="*.js" --include="*.py" .
```

---

## Check what's about to ship

```bash
# Files changed since main
git diff --name-only main..HEAD

# Full diff
git diff main..HEAD

# Just the commits
git log --oneline main..HEAD
```

---

## Validate your changes locally before pushing

```bash
python3 - <<'EOF'
# HTML well-formedness check
import pathlib, sys
from html.parser import HTMLParser

class Strict(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors, self.stack = [], []
        self.void = {"area","base","br","col","embed","hr","img","input",
                     "link","meta","param","source","track","wbr"}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.errors.append(f"unclosed: </{self.stack.pop()}>")
            if self.stack: self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}>")

root = pathlib.Path(".")
files = sorted(set(root.glob("*.html"))
               | set((root / "products").glob("*.html"))
               | set((root / "use-cases").glob("*.html")))
fail = False
for f in files:
    p = Strict()
    p.feed(f.read_text())
    p.close()
    issues = p.errors + ([f"unclosed: {p.stack}"] if p.stack else [])
    if issues:
        fail = True
        print(f"FAIL {f}: {issues[:3]}")
sys.exit(1 if fail else 0)
EOF
```

(Full set of validators in `.github/workflows/validate.yml`.)

---

## Restore the site to a previous version

If a deploy broke things:

```bash
# Find the last good commit
git log --oneline

# Revert the bad commit (creates a new "Revert ..." commit)
git checkout main
git pull
git revert <bad-sha>
git push origin main
```

The site re-deploys to the previous version within minutes.

---

## Add a new top-level page (e.g. `/blog.html`)

(See [Ch 06](./06-editing-content.md#add-a-new-top-level-page-eg-bloghtml) for full version.)

1. Copy `about.html` → rename to your new page.
2. Update title, description, canonical, OG tags.
3. Update body content.
4. Add to the main nav of every other page.
5. Add to `sitemap.xml`.

---

## Replace a product image (in place)

1. Save the new WebP file with the **exact same filename** as the existing
   one in `images/`.
2. Hard-refresh the browser (`Ctrl+Shift+R`).
3. Commit, push, PR.

No HTML changes needed if you preserve the filename.

---

## Take a product permanently offline

1. Remove its `PRODUCTS` entry in `tools/generate_product_pages.py`.
2. Remove its `CONTENT_BY_SLUG` entry in `tools/product_content.py`
   (if present).
3. `git rm products/<slug>.html`.
4. Remove the card from `products.html`.
5. Remove the JSON-LD ListItem and renumber the rest, decrement
   `numberOfItems`.
6. Remove the URL from `sitemap.xml`.
7. (Optional) put a meta-refresh stub at `products/<slug>.html`
   redirecting to `/products.html`.

---

## Investigate "the site shows the wrong price"

Three places to check, in this order:

1. `tools/generate_product_pages.py` — `PRODUCTS` entry. Is `price_min` /
   `price_max` / `price_display` correct?
2. Has `python3 tools/generate_product_pages.py` been run since the last
   change? Check `products/<slug>.html`.
3. `products.html` — the card's `data-price` AND `<div class="card-price">`
   text. Both should match the `PRODUCTS` data.

If one of those three is out of date, fix it and follow the recipe at the
top of this page.

---

## I broke something. Where do I look?

| Symptom | Likely cause | Where to look |
|---------|--------------|----------------|
| Page is blank or partly broken | HTML well-formedness error | CI logs, or the page in the browser console |
| Cart shows the wrong price | `data-price` on the card and `PRODUCTS.price_min` are out of sync | `products.html` and `tools/generate_product_pages.py` |
| Form submit doesn't work | Probably a typo in `js/main.js` | Browser console for the error |
| Lead sheet stopped receiving rows | Apps Script re-deployed with a new URL? | `FORM_ENDPOINT_URL` in `js/main.js` and `js/quote-cart.js` |
| Image is broken on a card | Filename mismatch | `images/` folder vs `image_prefix` in PRODUCTS |
| Search results show the old name | Browser cache or Google not re-crawled yet | Wait 24–48 hours for Google. Hard-refresh for browser. |
| `validate.yml` fails on PR | One of the four checks (HTML / JSON-LD / links / sitemap) | Read the FAIL line in the CI log; fix that file |

---

## Where things live (one-line reference)

```
Hero / FAQ / testimonials  → index.html
Catalogue cards            → products.html  (hand-maintained)
Per-product SEO pages      → products/*.html  (GENERATED)
Use-case pages             → use-cases/*.html  (GENERATED)
Brand palette              → css/style.css :root
Cart logic                 → js/quote-cart.js
Forms / nav / FAQ behavior → js/main.js
Product data               → tools/generate_product_pages.py (PRODUCTS)
Product narrative copy     → tools/product_content.py
Lead-capture URL           → js/main.js + js/quote-cart.js (BOTH)
GA4 property ID            → every page's <head>
WhatsApp number            → grep -rn "917588447595"
Sitemap                    → sitemap.xml
CI workflow                → .github/workflows/validate.yml
Backlog                    → ROADMAP.md
Known bugs                 → BUGS_TO_FIX.md
This manual                → docs/
```

---

That's the manual. Bookmark this page, read the rest when you need depth.

← [Back to the Manual Index](./README.md)
