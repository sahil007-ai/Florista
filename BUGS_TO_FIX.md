# Bugs To Fix — Florista Site Audit

Backlog of issues surfaced during a hostile-developer audit on May 27, 2026.
Each item has been verified by replay (script-driven test against the actual
codebase, not just static reading).

The site is **fundamentally working and shippable**. None of these are
release blockers. They're a mix of real bugs, robustness gaps, and SEO/a11y
polish that a senior reviewer would flag in code review.

---

## Quick triage

| # | Severity | Item | Effort |
|---|---|---|---|
| 1 | HIGH | Cart crashes on poisoned `localStorage` | 5 min |
| 2 | HIGH | 9 root pages missing `<link rel="canonical">` | 15 min |
| 3 | HIGH | Drawer crashes if cart item is missing `price` | 5 min |
| 4 | MEDIUM | `setQty()` accepts `Infinity` and `1e15` (no upper bound) | 5 min |
| 5 | MEDIUM | 236 KB of duplicated inline CSS across 22 product pages | 30 min |
| 6 | MEDIUM | Contact form has zero `maxlength` on any input | 5 min |
| 7 | MEDIUM | Quote drawer missing `aria-modal="true"` + focus trap | 30 min |
| 8 | MEDIUM | Lightbox missing `role="dialog"` and `aria-modal` | 10 min |
| 9 | MEDIUM | Hero LCP images lazy-loaded on `products.html` and `about.html` | 5 min |
| 10 | MEDIUM | 28 meta-descriptions > 160 chars, 24 titles > 60 chars (SERP truncation) | 20 min |
| 11 | MEDIUM | JSON-LD blocks don't escape `<` `>` `&` (defense-in-depth) | 5 min |
| 12 | LOW | Inconsistent `-webkit-backdrop-filter` prefixing in inline CSS | 10 min |
| 13 | LOW | 16 inline `onclick=` handlers per product page (blocks strict CSP) | 30 min |
| 14 | LOW | `localStorage.setItem()` not wrapped in try/catch (iOS Safari private = 0 quota) | 5 min |
| 15 | LOW | No `:focus-visible` styles — keyboard focus indicator is browser default | 20 min |
| 16 | LOW | Devanagari digits in phone field rejected by `\D/g` | 5 min |
| 17 | LOW | `navigator.sendBeacon` not used for fire-and-forget telemetry | 15 min |

Total: 17 items. Estimated effort if batched: ~3.5 hours.

---

## HIGH severity

### 1. Cart crashes on poisoned `localStorage`

**Location**: `js/quote-cart.js:69-74` — `loadCart()`

**What's wrong**: The `try/catch` only protects against malformed JSON, not
against valid JSON values that aren't objects. If someone sets the storage
key to `"null"` (valid JSON, parses to JS `null`), `loadCart()` returns
`null`, and the next `addToCart()` call crashes with
`TypeError: Cannot set properties of null (setting 'some-id')`.

The same issue with `"42"`, `"\"hello\""`, `"[1,2,3]"`, `"true"` — those
don't crash but they silently lose every cart write because property
assignment on primitives is a no-op (in non-strict) or throws (in strict).

**Repro**:
```js
localStorage.setItem('florista-quote-cart', 'null');
location.reload();
// Try to add anything to cart → TypeError
```

**Fix** (one-liner in `loadCart()`):
```js
function loadCart() {
    try {
        const v = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
        return (v && typeof v === 'object' && !Array.isArray(v)) ? v : {};
    } catch (_) {
        return {};
    }
}
```

---

### 2. Nine root pages have NO `<link rel="canonical">`

**Location**: `index.html`, `products.html`, `about.html`, `contact.html`,
`wholesale.html`, `privacy.html`, `terms.html`, `refund.html`, `404.html`

**What's wrong**: Only the 22 generated `/products/<slug>.html` pages and
the 5 `/use-cases/<slug>.html` pages have canonicals. The most-trafficked
surface area on the site (the front door) has none.

Search engines may treat `theflorista.in/`, `theflorista.in/index.html`,
and any UTM-tagged variants as duplicate content. Without an explicit
canonical, Google picks one arbitrarily.

**Verified by**: scanning all 36 HTML files for `<link rel="canonical"`
patterns. 9 files have no match.

**Fix**: Add to each root-level page's `<head>`:
```html
<link rel="canonical" href="https://www.theflorista.in/index.html">
```
(adjust the URL per page).

For consistency with the generated product pages, place it directly under
the `<meta name="description">` tag.

---

### 3. Quote drawer crashes if any cart item is missing `price`

**Location**: `js/quote-cart.js:286` (and a few similar spots in
`renderDrawer()`)

```js
'<span class="quote-item-meta">Rs. ' + item.price.toLocaleString('en-IN')
+ '/pc · MOQ ' + item.moq + '</span>' +
```

**What's wrong**: No defensive `?.` or default. If a future schema change
leaves old localStorage entries lacking `price`, *the entire drawer
renders blank with a console error* — `Cannot read properties of undefined
(reading 'toLocaleString')`. User sees nothing useful and the send-quote
button never appears.

This is a forward-compatibility hazard, not currently triggered by the
code as it stands today. But schema migrations are inevitable.

**Repro** (verified by Node replay):
```js
const item = { id: 'x', name: 'Test', moq: 1, qty: 1 /* no price */ };
const line = `Rs. ${item.price.toLocaleString('en-IN')}/pc`;
// → CRASH: Cannot read properties of undefined (reading 'toLocaleString')
```

**Fix**: Defensive defaults at render time:
```js
const price = typeof item.price === 'number' ? item.price : 0;
const qty   = typeof item.qty   === 'number' ? item.qty   : (item.moq || 1);
```
Apply uniformly anywhere `item.price`, `item.qty`, `item.moq` are used.

---

## MEDIUM severity

### 4. `setQty()` accepts `Infinity` and `1e15`

**Location**: `js/quote-cart.js:184-189`

```js
function setQty(id, qty) {
    const cart = loadCart();
    if (!cart[id]) return;
    const moq = cart[id].moq || 1;
    cart[id].qty = Math.max(moq, Math.floor(qty) || moq);
    saveCart(cart);
}
```

**What's wrong**: No upper bound. The HTML `<input type="number">` (in the
drawer) has `min="..."` but no `max=`. A buyer (or a bot, or a careless
paste) can set qty to `Infinity`, `1e15`, or any large number. The
WhatsApp message body and Apps Script lead row will both contain the
garbage value.

Verified by replay:

| Input | Result |
|---|---|
| `0` | clamped to MOQ ✓ |
| `-100` | clamped to MOQ ✓ |
| `NaN` | clamped to MOQ ✓ |
| `Infinity` | qty = `Infinity` ✗ |
| `1e15` | qty = `1000000000000000` ✗ |
| `'abc'` | clamped to MOQ ✓ |

**Fix**:
```js
const MAX_QTY = 100000;  // sane upper bound — adjust per business needs
const parsed = Math.floor(qty);
const safe = Number.isFinite(parsed) ? parsed : moq;
cart[id].qty = Math.min(MAX_QTY, Math.max(moq, safe || moq));
```

Also add to the rendered `<input>` in `renderDrawer()`:
```html
<input ... max="100000" ...>
```

---

### 5. 236 KB of duplicated inline CSS across 22 product pages

**Location**: `tools/generate_product_pages.py` — `PAGE_TEMPLATE` contains
a 10,886-character `<style>` block that's emitted verbatim into every
generated product page.

**What's wrong**: The same 10 KB of CSS ships on every product page. With
22 product pages, that's ~225 KB of bandwidth wasted on cold-cache visitors
crawling the catalogue (or search engine bots crawling all pages).

The site already loads `css/style.css` via `<link rel="stylesheet">`, so
the inline block isn't there for any technical reason — it just landed
there during generator development.

**Verified by**: counting `<style>` block sizes across the 22 generated
pages: `10,758 × 22 = 236,676 bytes` of duplicated CSS.

**Fix**:
1. Move the styles defining `.product-detail`, `.pd-gallery`, `.pd-info`,
   `.pd-spec-grid`, `.pd-cta`, `.pd-description`, `.pd-feature-list`,
   `.pd-thumbs`, `.pd-story`, `.pd-hook`, `.related-section`,
   `.related-card`, `.lightbox-overlay`, `.lightbox-img`, `.lightbox-close`,
   and `.breadcrumb` into `css/style.css`.
2. Strip the `<style>` block from `PAGE_TEMPLATE`.
3. Re-run the generator.
4. Validate that `validate.yml` still passes.

Net win: ~225 KB saved on cold cache, single source of truth for product
page styles, easier to edit globally.

---

### 6. Contact form has zero `maxlength` on any input

**Location**: `contact.html:171, 175, 179, 183`

```html
<input type="text"  id="companyName" ...>
<input type="tel"   id="phone"       ...>
<input type="text"  id="city"        ...>
<input type="text"  id="interest"    ...>
```

None have `maxlength`. The JS validator only checks `!company` (after
`.trim()`) and phone digit count — no length cap.

**What's wrong**: A 2000-character company name or city sails through
validation, ends up in the WhatsApp message body, and lands in the
Apps Script lead-capture sheet. Combined with no rate limiting on the
endpoint, this is a denial-of-quota vector — Apps Script free tier has a
~20k/day execution quota.

**Fix**:
```html
<input type="text"  id="companyName" ... maxlength="120">
<input type="tel"   id="phone"       ... maxlength="20">
<input type="text"  id="city"        ... maxlength="80">
<input type="text"  id="interest"    ... maxlength="200">
```

Even if a determined attacker bypasses the form (DOM tampering), the JS
handler can also clamp:
```js
const company = companyField.value.trim().slice(0, 120);
```

Tradeoff to discuss: should phone allow longer for international-format
numbers? `+91 (75) 88-44-7595` is 18 chars. `maxlength="25"` is safer.

---

### 7. Quote drawer missing `aria-modal="true"` and focus trap

**Location**: `js/quote-cart.js:236` (inside `buildDrawer()`)

```js
drawer.setAttribute('role', 'dialog');
drawer.setAttribute('aria-label', 'Your quote');
```

**What's wrong**: 
- No `aria-modal="true"` → screen readers will read content behind the
  drawer as accessible.
- No focus trap — pressing Tab inside the drawer cycles focus into the
  page beneath, putting the user in a confusing state.
- No "focus into drawer on open" — `openDrawer()` sets `display`, but
  doesn't move keyboard focus into the drawer.

**Fix**:
```js
// In buildDrawer():
drawer.setAttribute('role', 'dialog');
drawer.setAttribute('aria-modal', 'true');
drawer.setAttribute('aria-label', 'Your quote');

// In openDrawer():
function openDrawer() {
    if (!drawer) return;
    renderDrawer();
    drawerOverlay.classList.add('open');
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    // NEW: move focus into drawer
    drawer.querySelector('.quote-close').focus();
}

// NEW: focus trap
drawer.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    const focusable = drawer.querySelectorAll(
        'button, [href], input, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
        last.focus(); e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === last) {
        first.focus(); e.preventDefault();
    }
});

// In closeDrawer(), restore focus to the trigger:
function closeDrawer() {
    if (!drawer) return;
    // ...
    if (cartButton) cartButton.focus();  // NEW
}
```

---

### 8. Lightbox missing `role="dialog"` and `aria-modal`

**Location**: `tools/generate_product_pages.py` (lightbox HTML in
`PAGE_TEMPLATE`)

```html
<div class="lightbox-overlay" id="lightbox" onclick="closeLightbox(event)">
    <button class="lightbox-close" ...>
    <img class="lightbox-img" id="lightbox-img" src="" alt="Product zoom">
</div>
```

**What's wrong**: ESC closes (good — already wired), but the `<div>` is
not announced as modal. Screen readers will read it as a regular div.

**Fix** (in the template):
```html
<div class="lightbox-overlay" id="lightbox"
     role="dialog" aria-modal="true" aria-label="Product image zoom"
     onclick="closeLightbox(event)">
```

Move focus to the close button on `openLightbox()`, restore to the main
image thumbnail on close (same focus-restore pattern as the drawer).

---

### 9. Hero LCP images lazy-loaded on `products.html` and `about.html`

**Location**: 
- `products.html` (first `<img>` in `<body>`)
- `about.html` (first `<img>` in `<body>`)

**What's wrong**: The first image visible above-the-fold on a page is
typically its Largest Contentful Paint (LCP) candidate. Lazy-loading it
delays LCP until after the IntersectionObserver fires — costing 100-300ms
on most connections.

`index.html` and the 22 per-product pages get this right (`loading="eager"
fetchpriority="high"`). The two missing pages take an LCP penalty for no
reason.

**Verified by**: scanning the first `<img>` after `<body>` in each page.

**Fix** (per page):
```html
<img src="..." alt="..." loading="eager" fetchpriority="high">
```

For `products.html` specifically, the hero is the catalogue header banner;
for `about.html`, the founder portrait.

---

### 10. Title and meta-description length issues (SERP truncation)

**Location**: 
- 28 pages have meta-description > 160 chars (Google truncates display)
- 24 pages have title > 60 chars

For product pages, the issue is in the generator templates:

```python
def page_title(p):
    return f"{p['name']} – Wholesale {p['size_label']} {CATEGORY_LABELS[p['category']]} | Florista Nagpur"
```

Example: `12" Regular & Ornela – Wholesale 12" Organza Flower | Florista Nagpur` = 63 chars.

```python
def meta_description(p):
    return (
        f"Buy {p['name']} wholesale at factory prices from Florista, Nagpur. "
        f"Handcrafted {p['size_label']} {cat} for {p['use_case']}. "
        f"{p['shade_count']} shades available, MOQ {p['moq']} pcs. PAN India delivery."
    )
```

Example: 220+ chars.

**What's wrong**: Anything past ~60 chars (title) and ~160 chars (description)
gets cut off mid-sentence in search results, often at an awkward place.

**Fix**: Tighten the templates:

```python
def page_title(p):
    # target ≤60 chars
    return f"{p['name']} | Florista Nagpur Wholesale"

def meta_description(p):
    # target ≤155 chars
    return (
        f"{p['name']} ({p['size_label']}) — wholesale from Florista's "
        f"Nagpur factory. {p['shade_count']} shades, MOQ {p['moq']}. "
        f"PAN India shipping."
    )
```

Re-generate, re-verify per-page lengths, ensure JSON-LD `description` field
matches the new shorter text.

---

### 11. JSON-LD blocks don't escape `<` `>` `&`

**Location**: `tools/generate_product_pages.py` — `render_page()`:
```python
product_jsonld=json.dumps(product_jsonld(p), indent=2),
```

**What's wrong**: `json.dumps()` does not escape `<` and `>` by default.
HTML5 parser scans `<script>` blocks for `</script>` even when their `type`
isn't JavaScript. If a product name ever contains `</script>`, the JSON-LD
block ends early and the rest of the value renders as HTML — including any
`<script>...</script>` payload it carries.

**Verified by** (defense-in-depth test):
```python
test_product["name"] = '<script>alert("XSS")</script>'
html = render_page(test_product)
# 3 occurrences of `<script>alert(` appear unescaped in the output,
# all inside <script type="application/ld+json"> blocks.
```

No real product name has these chars today (verified across all 22 SKUs),
so this is **not currently exploited**. But it's a defense-in-depth gap
that becomes important if Florista ever loads product data from an
external source (CSV import, Google Sheet, headless CMS).

**Fix**: Wrap `json.dumps(...)` output with HTML-safe escaping:
```python
def safe_jsonld(obj):
    return (
        json.dumps(obj, indent=2)
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('&', '\\u0026')
    )
```

This is Google's recommended pattern for embedded JSON-LD.

---

## LOW severity

### 12. Inconsistent `backdrop-filter` prefixing

**Location**: Inline CSS inside `tools/generate_product_pages.py`
`PAGE_TEMPLATE`.

```css
backdrop-filter: blur(14px);                    /* unprefixed */
-webkit-backdrop-filter: blur(14px);            /* prefixed */
```

Some places have both, some have only the unprefixed version. Safari
supported unprefixed `backdrop-filter` only from version 18 (2024). Older
iOS Safari (most users on iPhones not yet updated) needs the `-webkit-`
prefix.

**Verified by**: counting per-product page — 4 unprefixed, 2 prefixed.

**Fix**: For every `backdrop-filter` rule, also emit
`-webkit-backdrop-filter` immediately above it. Easiest done with a
post-process step or by editing the template directly.

---

### 13. 16 inline `onclick=` handlers per product page block strict CSP

**Location**: `tools/generate_product_pages.py` `PAGE_TEMPLATE` —
`onclick="openLightbox()"`, `onclick="pdSwitchImg(this)"`,
`onclick="closeLightbox(event)"`, `onclick="document.getElementById(...)"`.

**What's wrong**: These would block any future Content-Security-Policy
that doesn't allow `'unsafe-inline'` for `script-src`. Modern best
practice is to attach handlers via `addEventListener` from the script
file at the bottom of the page.

For a static site without a CSP today, this is purely a hygiene issue.

**Fix**: Move all four functions into `js/main.js` (or a new
`js/product-page.js`) and bind via `addEventListener` on
`DOMContentLoaded`. The thumbnails should be selected by class, not
identified individually.

---

### 14. `localStorage.setItem()` not wrapped in try/catch

**Location**: `js/quote-cart.js:81`
```js
function saveCart(cart) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    renderCartButton();
    if (drawer && drawer.classList.contains('open')) renderDrawer();
}
```

**What's wrong**: iOS Safari private browsing has historically had a
0-byte localStorage quota. Every `setItem()` throws
`QuotaExceededError`. The cart will appear to add items (UI updates) but
nothing persists, and the next operation crashes.

Modern Safari (16+) lifted this restriction in private mode, but legacy
iOS versions still in use among older buyer segments will hit it.

**Fix**:
```js
function saveCart(cart) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    } catch (e) {
        console.warn('[FloristaCart] localStorage write failed:', e);
        // Optional: fall back to in-memory state for the session
    }
    renderCartButton();
    if (drawer && drawer.classList.contains('open')) renderDrawer();
}
```

---

### 15. No `:focus-visible` styles

**Location**: `css/style.css` (and inline page CSS)

**What's wrong**: Buttons and links don't define a custom `:focus-visible`
ring. Browsers fall back to their own default outline, which varies wildly
across UAs and is sometimes invisible against the brand pink. Keyboard
users have a degraded experience.

**Fix**: Add a global focus style to `css/style.css`:
```css
:focus-visible {
    outline: 2px solid var(--color-primary-dark);
    outline-offset: 2px;
    border-radius: 4px;
}
button:focus-visible,
.btn:focus-visible {
    outline-offset: 3px;
}
```

The quote-cart `.quote-add-btn:focus-visible` already has a custom
treatment — propagate that pattern site-wide.

---

### 16. Devanagari digits in phone field are rejected

**Location**: `js/main.js:151-155` (form validation)
```js
const digits = phone.replace(/\D/g, '');
if (digits.length < 10) {
    flagInvalid(phoneField, 'Please enter a valid 10-digit number');
    return;
}
```

**What's wrong**: `\D` matches anything that isn't an ASCII digit
`[0-9]`. Devanagari digits (`९८७६५४३२१०` = 9876543210) are stripped as
"non-digits", and the resulting empty string fails the length check. An
Indian buyer typing their number on a Hindi keyboard cannot submit the
form.

**Verified by replay**: input `९८७६५४३२१०` → REJECTED.

**Fix**: Normalize Unicode-numeric chars to ASCII before stripping
non-digits.
```js
function toAsciiDigits(s) {
    // Devanagari (०-९), Arabic-Indic (٠-٩), Bengali (০-৯), etc.
    return s.replace(/[\u0660-\u0669\u06F0-\u06F9\u0966-\u096F\u09E6-\u09EF]/g,
        c => String.fromCharCode((c.charCodeAt(0) & 0xF) + 48)
    );
}
const digits = toAsciiDigits(phone).replace(/\D/g, '');
```

Or — simpler fallback — match `[\d]` instead of `\D` exclusion and use
the `u` flag with Unicode digit class:
```js
const digits = phone.match(/[0-9\u0660-\u0669\u0966-\u096F]/gu)?.join('') || '';
```

---

### 17. `navigator.sendBeacon` not used for fire-and-forget telemetry

**Location**: `js/main.js` `beaconClick()` — `js/main.js` form submit —
`js/quote-cart.js` `sendQuote()`

```js
fetch(FORM_ENDPOINT_URL, { method: 'POST', mode: 'no-cors', ... });
```

**What's wrong**: `fetch()` is the right tool for most things, but fire-
and-forget POSTs that need to survive a page navigation are more reliably
handled by `navigator.sendBeacon()` — which is specifically designed for
this case. With `fetch`, if the user clicks the WhatsApp button and the
page navigates before the request completes, the request is aborted.

For the contact form and quote cart this is mitigated because we open
WhatsApp in a new tab (so the original tab stays alive). But for the
WhatsApp click attribution beacon (PR #15's `beaconClick()`) the new tab
opens immediately and the original tab is no longer reliably foregrounded
on mobile, where browsers aggressively cancel pending fetches.

**Fix**:
```js
function postLeadCapture(payload) {
    if (!FORM_ENDPOINT_URL) return;
    const body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
        // sendBeacon survives page navigation
        const blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
        navigator.sendBeacon(FORM_ENDPOINT_URL, blob);
    } else {
        // Fallback for older browsers
        try {
            fetch(FORM_ENDPOINT_URL, {
                method: 'POST', mode: 'no-cors',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body, keepalive: true,
            });
        } catch (_) {}
    }
}
```

`keepalive: true` on the fetch fallback also helps modern browsers
prioritize it for completion across navigation.

---

## What's working well (not bugs — context for prioritization)

Listed for completeness so the next person doesn't re-litigate these:

- **HTML well-formedness**: 36/36 pages clean.
- **JSON-LD validity**: 56/56 blocks valid (Product + BreadcrumbList).
- **Internal-link integrity**: 0 broken refs across the site.
- **Sitemap**: in sync with `/products/*.html` on disk.
- **Consent Mode v2**: correctly wired — `consent('default')` runs before
  `config()`, default `denied`, granted only on banner accept.
- **GA4 attribution stack** (PR #15 merged, PR #16 pending): UTM tagging
  + Apps Script beacon + `— via:` message marker covers every dropout
  point. Pending `generate_lead` events round it out.
- **Generator architecture**: graceful fallbacks for products without
  custom content; sibling-content module keeps the template tidy.
- **Cart UX**: synchronous popup-blocker-friendly `window.open`,
  cart-survives-navigation localStorage, MOQ-aware steppers.
- **Color contrast**: all body text meets WCAG AA on the cream
  background. Brand-primary on cream is AA-large only — borderline for
  long-form text but fine for headings/CTAs.

---

## Suggested batching for PRs

If addressing this backlog over a few sessions, here's a sensible split:

**PR 1 — Production hardening (HIGH)**
- #1 Cart loadCart defensive type check
- #2 Add canonicals to 9 root pages
- #3 Cart drawer null-safe item rendering

**PR 2 — Input safety (MEDIUM)**
- #4 setQty upper bound + input max=
- #6 Form maxlength attributes
- #11 JSON-LD HTML-safe escaping

**PR 3 — Accessibility polish (MEDIUM)**
- #7 Drawer aria-modal + focus trap
- #8 Lightbox aria-modal
- #15 :focus-visible globals

**PR 4 — Performance + SEO (MEDIUM)**
- #5 Move inline CSS into shared style.css
- #9 Eager-load LCP images on products.html and about.html
- #10 Tighten title and meta-description templates

**PR 5 — Polish (LOW)**
- #12-#17 Bundle the LOW items together

Each PR is small enough to review in 5-10 minutes. Total backlog is
deliverable in a couple of focused afternoons.
