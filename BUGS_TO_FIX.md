# Florista Website — Known Bugs & Cleanup Tracker

A short, audited list of known issues on the site as of 31 May 2026,
companion to [`ROADMAP.md`](./ROADMAP.md). The split:

- **`ROADMAP.md`** = pending features and owner-input items (e.g. real
  testimonials, factory address, slab pricing).
- **`BUGS_TO_FIX.md`** *(this file)* = small known defects and cruft
  cleanup. Stuff that's wrong but doesn't block business.

If you find something newly broken, add it here, not in `ROADMAP.md`.

## Severity

- **P0** = customer-visible, fix urgently.
- **P1** = SEO / accessibility / quality issue, fix in the next sweep.
- **P2** = cosmetic or maintenance, fix when convenient.
- **P3** = optional cleanup; safe to ignore unless someone has time.

---

## Open

| #   | Pri | Title                                         | Notes |
|-----|-----|-----------------------------------------------|-------|
| 5   | P1  | Per-page `<style>` blocks duplicate styles already in `css/style.css` | Several pages (home hero, catalogue toolbar, per-product pages) declare their own `<style>` blocks in `<head>` for page-specific layout. Consolidating into `style.css` would shrink page weight modestly and centralize design tokens. **Not breaking anything today.** Defer until next visual refresh. |
| 10a | P2  | Two root-page `<title>` tags slightly exceed the 60-char SEO target | `index.html` is 64 chars; `products.html` is 62 chars. Most pages are now in budget after PR #1/#2. The remaining two are marginal — Google still shows ~70 chars in SERPs. Trim only if a future audit flags them as truncated. |
| 16  | P3  | Orphan file: `florista_wa_bot_complete_test.json` (36 KB, 0 newlines) | Single-line minified JSON, looks like a test export of the n8n workflow. Not referenced anywhere in the codebase. Decision needed: keep as a backup of an earlier export, or delete. |
| 17  | P3  | Orphan file: `n8n_after_paste2.png` (122 KB) at repo root | Screenshot from when the n8n workflow was being set up. Not referenced anywhere. Move to a `docs/screenshots/` folder if it has long-term value, otherwise delete. |
| 18  | P3  | Stray `website/` directory containing only `flowers.code-workspace` | Looks like a duplicate of the root-level `flowers.code-workspace`. Probably the result of an earlier accidental move. Delete after confirming the root copy is the live one. |
| 19  | P3  | Legacy n8n workflow: `florista_wa_bot_complete.json` (53 KB) | Superseded by the Python LangGraph bot in `wa-bot/`. Keep as design-reference until `wa-bot/` is deployed and proven in production, then archive or delete. Tracked in `.kiro/steering/whatsapp-bot.md`. |
| 20  | P2  | `js/main.js` line ~524 — `*_unknown` data-wa-source tagging | Comment notes that any `wa.me/...` link not on a known section gets tagged `<page>_unknown` in the lead sheet. Rows tagged `*_unknown` are a soft TODO list — when one shows up, audit the link and rename its `data-wa-source` attribute to something descriptive. Not a bug per se; an ongoing hygiene task. |

## Resolved (kept here so doc references still link to a live file)

These were tracked in earlier audit notes; they're now fixed in the
codebase. Listed here so any old documentation pointing at
`BUGS_TO_FIX.md#N` still resolves to a useful entry.

| #   | Title                                                                              | Resolved by         |
|-----|------------------------------------------------------------------------------------|---------------------|
| 2   | Missing `<link rel="canonical">` on 9 root pages                                   | PR #1 — every root page (`index`, `about`, `contact`, `products`, `wholesale`, `privacy`, `terms`, `refund`, `404`) now has its canonical. |
| 9   | Missing `loading="eager" fetchpriority="high"` on the hero LCP image of `products.html` and `about.html` | PR #2 — both pages now have the LCP attributes set on their hero `<img>`. |
| 10  | 24/36 pages exceeded the 60-char `<title>` budget                                  | Mostly resolved in PR #1/#2. Only 2 marginal cases remain — see #10a above. |
| 15  | Site-wide `:focus-visible` accessibility ring missing                              | PR #2 — `css/style.css` now has the global rule plus button/btn/anchor variants (≈lines 79–92). |

---

## How to use this file

- **Adding a bug:** pick the next unused number, give it a severity, and
  describe it in one to three lines. Don't write a fix plan — that goes
  in the PR that fixes it.
- **Fixing a bug:** move it to "Resolved" with the PR or commit reference,
  rather than deleting the row. That preserves doc links of the form
  `BUGS_TO_FIX.md#N`.
- **Big features go in `ROADMAP.md`, not here.** This file is for small
  defects and cleanup, not new functionality.

---

_Last updated: 31 May 2026._
