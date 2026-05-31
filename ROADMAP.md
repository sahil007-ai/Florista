# Florista Website — Roadmap of Incomplete Work

This document captures every improvement that has been **identified but not
yet shipped** on the Florista website, so the work is discoverable to anyone
who picks it up later (the owner, a freelancer, or a future agent).

It is the persistent companion to [PR #1](https://github.com/sahil007-ai/Florista/pull/1)
and [PR #2](https://github.com/sahil007-ai/Florista/pull/2), which together
delivered the fixes from a wholesaler-perspective design review of May 2026.

Work that is **already merged into `main`** is summarised at the bottom under
[What's already shipped](#whats-already-shipped) — do not redo it.

---

## How to read this list

Items are grouped by who needs to act:

- 🟡 **Owner input** — the owner of Florista needs to provide content, a
  decision, or a number. The site infrastructure is ready and waiting.
- 🟠 **External setup** — the owner needs to register/verify on a
  third-party service before the integration can be added.
- ⚪ **Explicitly deferred** — there is a deliberate reason this is parked.
  Don't pick these up until the trigger condition is met.

Each row also has a **priority** (P0 = highest business impact, P3 = nice
to have) and a **trigger** describing what unlocks it.

---

## 🟡 Owner input — pending decisions or content

| #   | Pri | Item                                                                                                                | Trigger / what is needed                                                                                                                           |
| --- | --- | ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| O1  | P0  | **About-page production-network copy edit**                                                                         | Owner picks **Option A** ("design + production network") or **Option B** ("just remove single-factory claim"). See [About copy options](#a-about-page-copy-options) below. |
| O2  | P0  | **Real factory address + Google Maps embed** in footer / contact page                                               | Owner sends street address                                                                                                                         |
| O3  | P1  | **Sales email address** (second contact channel besides WhatsApp)                                                   | Owner decides on the address (e.g. `hello@theflorista.in`)                                                                                        |
| O4  | P1  | **Compress the 25 MB catalogue PDF** to under 5 MB                                                                  | Re-export at lower image DPI from the design tool, or send the source PDF for a one-time compression pass                                          |
| O5  | P1  | **Real team + dispatch photos** for the About page and a future trust strip                                         | 2–4 phone shots: team in the working space, packaging area with boxes/AWB labels visible, hands-on-flower close-up. See [Photo brief](#b-photo-brief). |
| O6  | P1  | **Slab pricing tiers** on each product card (e.g. 10pc / 50pc / 100+pc)                                             | Owner decides the price ladder per product. Once decided, chips can be added to all 22 cards in one pass.                                         |
| O7  | P2  | **Real testimonials** to replace the 3 placeholder cards on the home page                                           | Owner sends the prepared WhatsApp template ([Appendix C](#c-testimonial-collection-template)) to 3 past customers and pastes the responses.       |

---

## 🟠 External setup — third-party registration first

| #   | Pri | Item                                                                          | Trigger / what is needed                                                                                                                                                                       |
| --- | --- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1  | P0  | **Udyam / MSME registration number** in footer of every page                  | Free to register at <https://udyamregistration.gov.in>. Once obtained, add to the brand block in the footer of every HTML page.                                                                |
| E2  | P0  | **Legal entity declaration** (Proprietorship / Partnership / LLP / Pvt Ltd) + proprietor name | If sole proprietor, no extra registration is needed. Add a single line near the footer copyright: e.g. "Proprietorship: \<Owner Name\>, Nagpur".                                              |
| E3  | P3  | **Trust seal badges** — JustDial verified, IndiaMART verified, TrustSEAL, Google Business Profile | Owner registers on those platforms first (most are free). Then embed each platform's verified-badge widget in the footer or trust strip.                                                       |

> **Note on GSTIN:** The site previously had GST-related text on `wholesale.html`
> and `terms.html`. Florista is **not GST-registered**, so all such references
> were removed in commit `4ce2fa4` (PR #2). Do not re-add GST language unless and
> until registration happens.

---

## ⚪ Explicitly deferred — do not pick up yet

| #   | Pri | Item                                                                 | Why deferred                                                                                                                                                                                                                                                                          |
| --- | --- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | P2  | **Pin-code shipping cost estimator**                                 | Indian couriers (Delhivery, DTDC, VRL, TCI) do not expose public iframe / JS widgets. A useful estimator would need Florista's actual zone-wise rate card. Manual quotes via WhatsApp are working at current order volume. **Trigger:** owner publishes a zone rate card.             |
| D2  | P3  | **WhatsApp Business API order tracker** ("Your order has been dispatched, AWB: XXXXX") | WA Business API is paid (≈₹0.005–0.05 per conversation in India) and requires Meta Business verification. Not worth the cost or onboarding until volume justifies. **Trigger:** ≥100 orders/month sustained. **Update (May 2026):** Florista now has a *general* WhatsApp sales-bot scaffold in `wa-bot/` (LangGraph + OpenRouter + Apps Script, [PR #30](https://github.com/sahil007-ai/Florista/pull/30)). The order-tracker on this row is a *specific* outbound use-case the scaffold doesn't yet implement; it would require a Meta-approved message template and a webhook from the order management system. See `docs/11-whatsapp-bot.md` (lands with PR #30). |
| D3  | P3  | **Login / reorder portal** with saved carts and order history        | Needs a backend, database, and authentication. Out of scope for a static HTML site. **Trigger:** migration to a CMS (Shopify / WordPress / custom Node or Django) when volume justifies.                                                                                              |
| D4  | P2  | **Multi-size responsive `srcset` image variants** for product photos | Current WebPs already gave a 93% size reduction (88 MB → 5.8 MB). The remaining win is small relative to the work, and would need to be redone once real product photography arrives. **Trigger:** real factory photos land (item O5). Then generate 3 sizes per image in one pass. |

---

## Appendices

### A. About-page copy options

The current About page says:

> "Today we supply ... — all from our single Nagpur production unit. Our pricing
> stays wholesale-direct because there is no one else in the supply chain."

Florista actually outsources production to a small network of partner workshops
in and around Nagpur. The current text could be caught out by an alert wholesaler
during a verification call. Pick one of the following replacements:

**Option A — transparent "design + production network":**

> "Today we design, QC and dispatch every order out of our Nagpur unit, working
> with a small network of skilled artisan workshops in and around Nagpur.
> Pricing stays wholesale-direct because we own the brand, the design library,
> and the customer relationship — no resellers in between."

**Option B — minimal change, just removes the false single-factory claim:**

> "Today we supply wedding decorators, event-management firms, stage contractors,
> and retail outlets across PAN India — from our Nagpur production base. Our
> pricing stays wholesale-direct because we work directly with the artisans who
> make every piece."

If Option A is picked, also update:

- Hero badge: `"Direct from Nagpur Factory"` → `"Direct from Nagpur"`
- Trust-strip card: `"Direct from Factory"` → `"Direct from Production Base"`
- Footer tagline: `"Bulk Decor Manufacturer"` is fine to keep — Florista is the
  manufacturer of the brand even if production is distributed.

### B. Photo brief

Four phone-shot photos are sufficient to replace the AI-rendered placeholder
images on the About page. Phone shots in natural daylight look more authentic
than studio shots in B2B contexts.

| Photo                  | What it should show                                                                | Why it matters                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Team photo**         | Owner + admin (2–4 people) standing in the working space, casual, daylight         | Buyers want a face for the WhatsApp number they are chatting with. Highest-ROI photo.    |
| **QC / inspection**    | Finished flowers laid out, you or a team member inspecting one                     | Shows that every piece is checked before dispatch — Florista's real value-add.           |
| **Packaging / dispatch** | Boxed orders ready, courier AWB labels visible (PII redacted)                    | Proves orders genuinely ship. Buyers worry about ghost manufacturers.                     |
| **Hands close-up**     | One person folding/finishing a flower, no faces needed                             | Suggests craftsmanship without claiming a giant production line. Can be from any partner workshop with permission. |

### C. Testimonial collection template

Send this exact WhatsApp message to 3 of your most-recent happy buyers. Then
paste each response into the `[REPLACE]` slots in the testimonials section of
`index.html`.

> Hi \<Name\>, hope your event went well!
>
> Quick favor — could you share a 2-line review of working with Florista that
> we can put on our website? Just type it back here. Will help us immensely.
> Thank you!

Even **one real testimonial outperforms three fake ones** for B2B trust.
Start with one and add more over time. Anonymous-with-consent is also fine
("A wedding decorator in Pune, 60-piece order, June 2026") if the customer
prefers not to be publicly named.

### D. Future polish (not in scope yet, capture for memory)

These are not on the active backlog but are worth remembering:

- **Pa11y / axe accessibility audit** once real photos arrive
- **Open Graph image** per page — currently each page already has its own image,
  but a dedicated 1200×630 social-share variant per page would render better
- **Cookie banner localisation** — the consent banner is English-only; a Hindi
  translation toggle could help if owner does multi-lingual marketing
- **Schema.org Organization markup** with proper `legalName` once item E2 is
  decided

---

## What's already shipped

For context, the following work is already in `main` and **does not need
redoing**:

### From [PR #1](https://github.com/sahil007-ai/Florista/pull/1) — Wholesaler-review fixes

- Fixed 12 broken `alt` attributes on product cards (the `12"` quote was
  closing the attribute prematurely).
- Added MOQ chips on every product card.
- Replaced placeholder "Your Story" heading with real "Our Story" copy.
- Reconciled the advance-payment policy contradiction between Home FAQ and
  Wholesale page — both now say 100% advance for first-time, 50/50 from the
  third order.
- Added per-page Open Graph images.
- Added Product / ItemList JSON-LD schema covering all 22 products.
- Created `privacy.html`, `terms.html`, `refund.html`.
- Added "Legal" column to footer of every page.

### From [PR #2](https://github.com/sahil007-ai/Florista/pull/2) — Performance, SEO, social proof, AI-pivot polish

- Brand favicon set: `favicon.ico` (multi-size 16/32/48/64/128/256),
  `favicon.svg`, `apple-touch-icon.png`.
- Converted 184 product PNGs to WebP — `images/` folder went from
  88 MB to 5.8 MB (93% saving). Updated every HTML reference and the
  Product JSON-LD.
- New "Latest on Instagram" strip on home page linking to
  [@thefloristaflowerss](https://www.instagram.com/thefloristaflowerss/).
- `sitemap.xml` listing all 8 customer-facing pages, plus `robots.txt`.
- Sticky sort & filter toolbar on `products.html` (filter by MOQ / size,
  sort by price / size, with live result count).
- WhatsApp Business catalogue link (`wa.me/c/917588447595`) above the PDF
  form on the contact page.
- Replaced contradictory "Not AI's Guesswork" hero badge with positive
  "Send a Reference Image — AI, Pinterest or sketch — we craft it real"
  framing. Added a dedicated "Custom Orders" callout inviting buyers to
  send AI references.
- Trusted-by stats strip (Events / Cities / Repeat Decorators / Shades).
- Three-card testimonials section with `[REPLACE]` placeholders and an
  inline HTML-comment "how to collect" guide.
- Removed all GST text from `wholesale.html` and `terms.html` because
  Florista is not GST-registered.
- Size guide on `products.html` — collapsible inline-SVG showing 12"/24"/
  36"/48"/60" flowers next to a 5'7" silhouette to-scale.
- DPDP Act consent banner — bottom-fixed banner on first visit, Accept/
  Decline buttons, choice persisted in `localStorage`. Google Analytics
  upgraded to Consent Mode v2 (default-deny, only fires after consent).
- Hero image on home page now has explicit width / height /
  `fetchpriority="high"` / `decoding="async"` to prevent CLS and prioritise
  the LCP image.
- GitHub Actions CI workflow at `.github/workflows/validate.yml` running
  on every PR — validates HTML well-formedness, JSON-LD parseability,
  internal link integrity, and `sitemap.xml` schema.

---

_Last updated: 31 May 2026 — added BUGS_TO_FIX.md tracker; noted that the
`wa-bot/` LangGraph bot scaffold is in active development on
[PR #30](https://github.com/sahil007-ai/Florista/pull/30) (deployment
pending Meta WA Business credentials + Pricing-sheet population)._
