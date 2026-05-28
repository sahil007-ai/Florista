# 08 — Analytics & Lead Capture

The site has three layered tracking systems. Each captures a different
slice of buyer intent, and together they give the owner a near-complete
picture of where leads come from.

---

## The three layers

```
┌─────────────────────────────────────────────────────────────┐
│  1. Google Analytics 4 (GA4)                                │
│     Macro-level traffic + lead events.                      │
│     ID: G-T5GR1DL2G0   (defined in every page's <head>)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  2. WhatsApp click attribution                              │
│     Every wa.me/... link auto-tagged with utm_source,       │
│     utm_medium=whatsapp, utm_campaign=enquiry.              │
│     Source slug identifies page + section.                  │
│     Implemented in js/main.js (FloristaWA module).          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  3. Apps Script lead-capture sheet                          │
│     Fire-and-forget POST on every WA click and form submit. │
│     Captures intent even when the buyer doesn't tap Send.   │
│     URL: FORM_ENDPOINT_URL in js/main.js + js/quote-cart.js │
└─────────────────────────────────────────────────────────────┘
```

The three layers don't replace each other — they each catch a different
dropout point.

---

## Layer 1 — Google Analytics 4

### What's set up

Every page in the site has GA4 wired into its `<head>`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-T5GR1DL2G0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}

  // DPDP Act: default-deny analytics until user gives consent
  gtag('consent', 'default', {
    analytics_storage:
      (typeof localStorage !== 'undefined'
        && localStorage.getItem('florista-consent') === 'accepted')
        ? 'granted' : 'denied',
    ad_storage: 'denied'
  });

  gtag('js', new Date());
  gtag('config', 'G-T5GR1DL2G0');
</script>
```

Three things to notice:

1. **Property ID is `G-T5GR1DL2G0`.** This is hardcoded on every page.
   To switch GA properties, do a project-wide find-and-replace.
2. **Default-deny.** Analytics doesn't fire until the buyer clicks "Accept"
   on the consent banner (DPDP Act compliance). The banner stores the
   choice in `localStorage` under `florista-consent`.
3. **`ad_storage` is always denied.** Florista doesn't run ads. If that
   changes, update this value to `'granted'` in the consent-update logic.

### What events are tracked

Beyond the standard GA4 page views, two custom events fire:

| Event name | When it fires | Properties |
|-----------|---------------|-----------|
| `select_content` | Buyer clicks any `wa.me/...` link | `content_type: 'whatsapp_cta'`, `item_id: <source_slug>` |
| `generate_lead` | Buyer submits the contact form OR sends a quote-cart | `method`, `form_id` / `source`, `city`, etc. |

`generate_lead` is GA4's recommended event for B2B lead capture and is
one-click promotable to a Key Event in the GA4 UI. Once promoted, it
shows up as a conversion goal you can build reports around.

### Switching to a different GA property

```bash
# Replace the ID across the whole codebase
grep -rl "G-T5GR1DL2G0" . | xargs sed -i '' 's/G-T5GR1DL2G0/G-YOURNEWID/g'

# Regenerate so the new ID lands on per-product / per-use-case pages
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py
```

(Linux: drop the `''` after `-i`.)

---

## Layer 2 — WhatsApp click attribution

Every `<a href="https://wa.me/...">` link on the site is automatically
decorated by `js/main.js` (the `FloristaWA` module) the moment the page
loads. Two things happen:

### 1. UTM parameters get appended to the wa.me URL

```
Before: https://wa.me/917588447595?text=Hi+Florista
After:  https://wa.me/917588447595?text=Hi+Florista
        &utm_source=home_hero
        &utm_medium=whatsapp
        &utm_campaign=enquiry
```

`wa.me` itself ignores these, but they make the URL self-documenting in
dev tools and GA4's outbound-link click events pick them up.

### 2. A "via:" line is appended to the message

```
Before message: "Hi Florista, I want to enquire…"
After message:  "Hi Florista, I want to enquire…

                — via: home_hero"
```

This survives the wa.me hop into WhatsApp itself, so the source is also
visible inside the chat for any message the customer actually sends.

### How sources are derived

The `source` slug auto-derives from where the link sits in the DOM:

| Link location | Source slug |
|---------------|-------------|
| `<a class="floating-whatsapp">` | `<page>_floating` |
| Inside `.footer-social` | `<page>_footer_social` |
| Inside `.product-card` | `<page>_card_<slug>` |
| Inside `.uc-final-cta` | `<page>_final_cta` |
| Inside `.uc-hero` | `<page>_hero` |
| Inside `.size-guide` | `<page>_size_guide` |
| Inside `.cat-sidebar` / `.sidebar-cta` | `<page>_sidebar` |
| Inside `.pd-cta` (per-product) | `<page>_enquire` |
| Anywhere else | `<page>_unknown` |

Where `<page>` is:

| URL | `<page>` |
|-----|---------|
| `/` or `/index.html` | `home` |
| `/products.html` | `products` |
| `/products/60-inch-giant-flora.html` | `product_60-inch-giant-flora` |
| `/use-cases/wedding-backdrops.html` | `use_case_wedding-backdrops` |

### Overriding a source

If a link is somewhere the auto-derivation can't infer (e.g. a custom
section like the home-page hero CTA), override it explicitly:

```html
<a href="https://wa.me/917588447595?text=Hi"
   data-wa-source="home_hero">
    Enquire
</a>
```

The `data-wa-source` attribute always wins.

### Re-tagging dynamically inserted links

If you insert a `wa.me` link via JavaScript after the page loads, call:

```javascript
window.FloristaWA.tagAll(parentElement);  // or document for the whole page
```

This is what `js/quote-cart.js` does internally for the cart's "Send Quote"
button.

### Reading the data in GA4

GA4 → Reports → Engagement → Events → `select_content` → look at the
`item_id` dimension. You'll see one row per source slug. The slug taxonomy
above tells you exactly which page and section drove each click.

---

## Layer 3 — Apps Script lead-capture sheet

The most useful layer for a small business — a single Google Sheet that
shows every lead, with timestamp and source, in one place.

### Why this is useful

GA4 tells you *that* somebody clicked WhatsApp. The sheet tells you *who*
they were and what they wanted, even when they:

- Open WhatsApp but never tap Send (most common dropout).
- Use a phone with WhatsApp Business that doesn't open from the wa.me link.
- Bounce away mid-typing.

In every case, the sheet captures the intent **before** WhatsApp opens.

### What the sheet captures

Three kinds of rows, all in the same sheet:

| Row type | When | Company column |
|----------|------|----------------|
| Contact-form submission | Buyer submits the form on `contact.html` | The name they typed |
| Quote-cart send | Buyer taps "Send Quote on WhatsApp" | `(Quote — anonymous; awaiting WhatsApp reply)` |
| Bare WhatsApp click | Any `wa.me/...` click anywhere on the site | `(WhatsApp click — anonymous; awaiting reply)` |

Filter the "Company" column by `starts with "("` to find the anonymous
rows. Filter by source slug in the "Interested In" column (formatted as
`[<source>] <message preview>`) to attribute by page section.

### One-time setup

The full Apps Script setup is documented at
**[`.kiro/steering/lead-capture.md`](../.kiro/steering/lead-capture.md)**.
Walk through that file once to:

1. Create a new Google Sheet.
2. Open Apps Script via `Extensions → Apps Script`.
3. Paste the supplied `doPost` script.
4. Deploy as a Web App with "Anyone" access.
5. Copy the resulting `/exec` URL.

### Wiring the URL into the site

After you have the `/exec` URL, paste it into **two** files:

```javascript
// js/main.js (top of the file)
const FORM_ENDPOINT_URL = 'https://script.google.com/macros/s/AKfy.../exec';
```

```javascript
// js/quote-cart.js (inside the IIFE)
const FORM_ENDPOINT_URL = 'https://script.google.com/macros/s/AKfy.../exec';
```

Both files have a comment near the constant reminding you about the
duplication. The duplication is intentional — both files are small and
self-contained, and there are only two callsites.

> **Until both URLs are set, all flows still work.** The form still opens
> WhatsApp, the cart still works. They just don't log to the sheet.

### Verifying it works

1. Open `contact.html` in your browser.
2. Fill in the form with test data.
3. Submit.
4. Open the Google Sheet — within 2–3 seconds a new row should appear.

If no row appears:
- Check the browser console for errors (F12 → Console).
- Check the Apps Script "Executions" tab for failures.
- Re-deploy the Apps Script with "Who has access: Anyone" — this is
  required.
- Verify the URL is exactly the one ending in `/exec` (not the editor URL).

### Reading the sheet day-to-day

Open the sheet, filter the "Received At" column to the last 7 days. Each
row is a lead. The "Interested In" column tells you what they want and
where they came from. Use it to:

- Reply to anonymous clicks with a "saw your interest, need any help?"
  follow-up.
- Track which pages drive the most leads.
- Spot patterns ("we get a lot of haldi-decor questions on weekends").

---

## Quick comparison: when to look where

| Question | Best layer to check |
|----------|---------------------|
| How much traffic did the site get this week? | GA4 |
| What's the bounce rate on the home page? | GA4 |
| Which page generates the most enquiries? | Sheet (filter by source slug) |
| Did anyone click the "60 Giant Flora" enquire button today? | Sheet OR GA4 (`select_content` events) |
| What did Mr. Sharma write in his enquiry yesterday? | Sheet (filter by company) |
| Did our Diwali campaign drive new buyers? | Both — GA4 for traffic, sheet for actual conversions |

---

## Privacy & DPDP Act compliance

A few things to keep in mind:

- **Analytics is opt-in by default.** The consent banner default-denies
  analytics until the buyer clicks Accept. Don't change this without
  legal review — DPDP Act 2023 requires explicit consent for non-essential
  tracking.

- **The lead-capture sheet captures personal data.** Phone numbers,
  cities, names. Treat the sheet as confidential. Limit access to people
  who need it. Periodically delete old rows you no longer need.

- **The `<a>` decoration in `FloristaWA.tagAll` does not require consent.**
  UTM parameters on outbound links are not personal data. The `select_content`
  GA event uses non-personal slug strings, but it still respects consent
  (it's a `gtag` event, gated by the same default-deny flag).

- **Privacy policy** at `privacy.html` describes all three layers. If you
  add new tracking, update the privacy policy too.

---

## Adding a new tracked event

If you want to track a new interaction (e.g. clicks on the Instagram
strip), follow this pattern:

```javascript
// In a click handler
if (window.gtag) {
    window.gtag('event', 'select_content', {
        content_type: 'instagram_tile',
        item_id: tile.dataset.tileId,    // a slug you control
    });
}
```

Use built-in GA4 event names where they exist
(<https://support.google.com/analytics/table/13594742>). Custom event
names work but cost you the built-in reports.

For high-value events (a new lead-generation pathway), use `generate_lead`
instead of `select_content`. GA4 lets you promote `generate_lead` to a
Key Event with one click.

---

## Troubleshooting

**Leads aren't reaching the sheet.**

In order:
1. Confirm `FORM_ENDPOINT_URL` is set in **both** `js/main.js` AND
   `js/quote-cart.js`. Both must have the same `/exec` URL.
2. Open the Apps Script project, click "Executions" — see if any
   executions are recorded. If yes but the row isn't in the sheet, the
   script isn't writing to the right sheet.
3. Re-deploy the Apps Script. Set "Execute as: Me" and "Who has access:
   Anyone." If you change either, you have to re-deploy and use the **new**
   `/exec` URL.

**GA4 isn't recording any events.**

1. Open the live site in an incognito window.
2. Click "Accept" on the consent banner.
3. Open GA4 → Reports → Realtime. You should appear within ~30 seconds.
4. If nothing appears, check the property ID in the page source matches
   what's in your GA4 admin.

**The consent banner shows up every time.**

`localStorage` may not be persisting (incognito mode, or a browser
extension blocking it). Once a buyer accepts, the choice is stored under
`florista-consent`. If the key gets cleared (or never sets), the banner
re-shows. This is correct behaviour — don't change it.

---

Next chapter: [09 — Deployment & CI →](./09-deployment.md)
