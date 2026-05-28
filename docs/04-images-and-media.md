# 04 — Images & Media

This chapter covers everything image-related: naming, formatting, where to
put files, how to optimise them, and how the generator references them.

---

## The `images/` folder

Every photo on the site lives in `/images/`. There are no subfolders.

Three kinds of files live here:

| Type | Naming | Example |
|------|--------|---------|
| Product photos | `product_<prefix>_<index>.webp` | `product_organza_24_inch_3.webp` |
| Favicons | Standard names | `favicon.ico`, `favicon.svg`, `apple-touch-icon.png` |
| Hero / decorative | (currently none — products serve as hero photos) | — |

---

## Why WebP and not JPEG / PNG

The site ships **only WebP** for product photography. Every modern
browser supports it (since 2020+ for Safari). WebP files are typically
70–95% smaller than the same image as JPEG or PNG.

Concretely: when the site was migrated from PNG to WebP, the `images/`
folder shrank from **88 MB to 5.8 MB** — a 93% reduction. That directly
improved page load times and Google's Core Web Vitals scores.

**Always use WebP for new product photos.** If a supplier sends you a
JPEG or PNG, convert it before checking it in.

---

## How to name product photos

Format: `product_<prefix>_<index>.webp`

Rules:
- Lowercase only.
- Use underscores, never spaces or hyphens.
- The `<prefix>` matches the `image_prefix` field in the product's entry
  in `tools/generate_product_pages.py`.
- The `<index>` is a positive integer. Photos are usually numbered
  starting at 1.
- Indices don't have to be contiguous, but it's tidier when they are.

### Real examples from the repo

| Product | Prefix | Files |
|---------|--------|-------|
| 60" Giant Flora | `product_organza_60_inch` | `_1.webp` through `_13.webp` |
| Aura Flower | `product_aura_flower` | `_1.webp`, `_2.webp` |
| Dream Wings 90" | `product_dream_wings` | `_1.webp`, `_3.webp` (no `_2`) |

The Dream Wings example is allowed because its `image_indices` field is
`[1, 3]` instead of `range(1, 4)`. The generator only references the
indices you tell it about.

---

## How the generator references photos

Every product's entry has these two fields:

```python
"image_prefix": "product_sunset_petals",
"image_indices": [1, 2, 3, 4],
```

The generator builds image URLs like:

```
images/product_sunset_petals_1.webp
images/product_sunset_petals_2.webp
images/product_sunset_petals_3.webp
images/product_sunset_petals_4.webp
```

The first index in the list is used as:
- The hero image on the per-product page
- The Open Graph (`og:image`) for social sharing
- The thumbnail on `products.html`
- The image in the JSON-LD schema

The remaining images become thumbnails on the per-product page gallery
and the catalogue card thumbnail strip.

---

## Adding a new product photo

1. Save the WebP file into `images/` with the right name.
2. If it's a new index for an existing product, add the number to
   `image_indices` in the `PRODUCTS` list. Re-run the generator.
3. If it's a brand new product, see [Recipe 2 in Chapter 03](./03-managing-products.md#recipe-2--add-a-brand-new-product).

---

## Replacing an existing product photo

This is the most common image task — a supplier sends a better photo of
an SKU, and you want to swap it in.

1. **Use the exact same filename** as the existing photo. Overwriting in
   place means the URL stays the same and you don't need to edit any
   markup.
2. Drop the new WebP into `images/` (overwrite the old one).
3. Verify in the browser:
   - <http://localhost:8000/products/your-slug.html>
   - <http://localhost:8000/products.html> (find the card)
4. **Cache busting:** if you've already deployed the site, browsers may
   show the old cached image. The simplest fix is to bump the version in
   the URL by appending a query string in `products.html`:

   ```html
   <img src="images/product_xyz_1.webp?v=2" alt="…">
   ```

   …or bump every reference to that image. The static host's cache will
   purge on its own, usually within an hour.

---

## Image size and quality targets

| Image type | Max dimensions | Target file size |
|------------|----------------|------------------|
| Product hero (main image) | 1200 × 1200 px | ≤200 KB |
| Product thumbnail | 600 × 600 px | ≤80 KB |
| Hero (home page) | 1600 × 1200 px | ≤300 KB |
| OG / social share | 1200 × 630 px | ≤200 KB |

The site's largest contentful paint (LCP) is usually the hero image. Keep
hero photos lean.

### Converting JPEG / PNG → WebP

There are several free options:

- **Online (no install):** <https://squoosh.app/> — drag the file in,
  pick WebP on the right side, slide quality to ~80, download.
- **Command line (mac/linux):** install `cwebp` (`brew install webp` /
  `apt install webp`):

  ```bash
  cwebp -q 80 input.jpg -o output.webp
  ```

- **Batch conversion:**

  ```bash
  for f in *.jpg; do
      cwebp -q 80 "$f" -o "${f%.jpg}.webp"
  done
  ```

Quality 80 is the sweet spot for product photography — visually
indistinguishable from the original at typical viewing sizes.

---

## Alt text

Every `<img>` tag must have an `alt` attribute. This is required for
accessibility and helps SEO.

**Good alt text:**
- Describes what's in the image, briefly.
- Includes the product name.
- Is unique per image (not the same string copied across all photos).

**Bad alt text:**
- Empty (`alt=""`) — only acceptable for decorative images.
- Filename-style (`alt="IMG_3492"`).
- Keyword-stuffed (`alt="organza flower wholesale buy nagpur cheap"`).

The generator writes good alt text automatically using the product name
and size. For hand-edited cards in `products.html`, follow the same
pattern:

```html
<img src="images/product_sunset_petals_1.webp"
     alt="Sunset Petals 24-inch warm-toned wholesale flower by Florista, Nagpur">
```

---

## Be careful with quote characters in `alt`

This is a real bug that bit the site once
([fixed in PR #1](../ROADMAP.md#whats-already-shipped)).

If your product name contains an inch quote (`"`), and you use double
quotes around your `alt` attribute, the attribute closes early:

```html
<!-- WRONG: the alt closes after `12`, the rest of the line is broken -->
<img src="…" alt="12" Regular & Ornela">
```

Two fixes:

```html
<!-- Either: use single quotes around the attribute -->
<img src="…" alt='12" Regular & Ornela'>

<!-- Or: HTML-encode the inch mark -->
<img src="…" alt="12&quot; Regular &amp; Ornela">
```

The generator handles this automatically. Hand-edited cards in
`products.html` need to be careful.

---

## Open Graph images (social-share previews)

Each page has its own Open Graph meta tag pointing to a representative
image. When a buyer shares a link on WhatsApp, Facebook, or LinkedIn, that
image renders as the preview card.

Per-page OG images are set in the `<head>`:

```html
<meta property="og:image" content="https://www.theflorista.in/images/product_organza_60_inch_1.webp">
```

For per-product pages, the generator picks the first image in
`image_indices`. For root-level pages (`index.html`, `about.html`, etc.),
the OG image is hardcoded — edit the `<head>` of that page directly.

---

## Favicons

Favicon files in the repo:

| File | Used by |
|------|---------|
| `favicon.ico` | Older browsers (multi-size: 16/32/48/64/128/256 px) |
| `favicon.svg` | Modern browsers; scales perfectly to any size |
| `apple-touch-icon.png` | iOS home-screen icon (180×180 px) |

Replacing the favicon:

1. Generate a new icon set. <https://realfavicongenerator.net/> takes one
   high-res PNG and produces all the formats above.
2. Drop the new files into `images/` (overwrite the existing ones).
3. Hard-refresh in your browser to see the change. Browsers cache
   favicons aggressively — sometimes a full restart is needed.

The HTML references are already in place in every page's `<head>`:

```html
<link rel="icon" href="images/favicon.ico" sizes="any">
<link rel="icon" href="images/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
```

For pages in subfolders (`/products/*.html`, `/use-cases/*.html`), the
references are `../images/favicon.*` — the generator handles this.

---

## When images break: troubleshooting

**The card shows a broken image icon**

Check three things:

1. The file exists at `images/<exact-filename>.webp` — case-sensitive on
   Linux servers, even if it works on macOS / Windows locally.
2. The `image_prefix` and `image_indices` in `PRODUCTS` match the
   filename.
3. After editing the prefix or indices, you ran the generator.

**The image looks pixellated or distorted**

The source PNG/JPEG was already low-res, or the WebP conversion used too
low a quality. Re-export from the source at a higher resolution.

**The image takes forever to load**

The file is too big. Open `images/`, check the file size:

```bash
ls -lh images/product_<prefix>_*.webp
```

Anything over ~250 KB for a product photo should be re-compressed. Run it
through Squoosh at quality 75 or 80.

**The image displays correctly locally but not after deploying**

Likely a case-sensitivity issue. macOS and Windows treat
`Product_Sunset_Petals_1.webp` and `product_sunset_petals_1.webp` as the
same file. Linux servers (which most static hosts run on) treat them as
different files. **Always lowercase your filenames.**

---

Next chapter: [05 — Sales & Discounts →](./05-sales-and-discounts.md)
