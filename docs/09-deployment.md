# 09 — Deployment & CI

How changes you make on your laptop end up on the live site, and what to
do when the CI checks complain.

---

## How the site is hosted

The site is a folder of static files served from a static host (typically
GitHub Pages or a similar CDN — check the repo's deployment settings on
GitHub for the exact host). The host:

- Watches the `main` branch.
- Whenever a commit lands on `main`, builds and deploys within a few
  minutes.
- Serves over HTTPS at <https://www.theflorista.in>.

There is no application server, no database, no Node process running on
production. Static files only.

---

## The deployment loop

```
your laptop                GitHub                     production host
───────────                ──────                     ────────────────
edit files
git commit
git push   ───────────►   feature branch
                          PR opened
                          ───► CI runs validate.yml
                                ─ HTML well-formedness
                                ─ JSON-LD schema
                                ─ Internal-link integrity
                                ─ sitemap.xml well-formed
                          PR approved
                          merge to main  ───────►   automatic deploy
                                                    (live within minutes)
```

**Always work on a branch, always go through a PR.** The PR is your
safety net — CI catches structural issues before they hit production.

---

## What the CI workflow does

The workflow file is `.github/workflows/validate.yml`. It runs on every
push to `main` and on every PR.

Four checks, in order:

### 1. HTML well-formedness

Parses every `*.html` file at the repo root, under `products/`, and under
`use-cases/`. Fails if any tag is unclosed or any closing tag has no
matching opener.

**What can fail this:**
- Missing `</div>` somewhere.
- A `<p>` inside a `<p>` (HTML5 rule against nested paragraphs).
- A typo like `<scrip>` instead of `<script>`.
- An inch quote (`"`) inside an attribute value that closed with double
  quotes (the classic alt-attribute bug — see [Ch 04](./04-images-and-media.md)).

### 2. JSON-LD schema validity

Extracts every `<script type="application/ld+json">` block and runs
`json.loads()` on it. Fails if any block has malformed JSON.

**What can fail this:**
- A trailing comma after the last item (Python allows it, JSON doesn't).
- Single-quoted strings (must be double-quoted in JSON).
- An unescaped `"` inside a string value.
- An unescaped newline inside a string.

### 3. Internal-link integrity

Walks every `href` and `src` in every HTML file. For each, checks the
target exists in the repo. External URLs (`https://...`, `tel:`, `mailto:`)
are skipped.

**What can fail this:**
- Renaming a file without updating the links to it.
- Typing a wrong filename (`product_aura_3.webp` when only
  `product_aura_flower_2.webp` exists).
- Removing an image without removing references to it.
- A trailing slash where there shouldn't be one.

### 4. `sitemap.xml` well-formedness

Parses `sitemap.xml` as XML. Fails if the file isn't valid XML or doesn't
match the sitemap schema.

**What can fail this:**
- Missing or extra closing tag.
- An unescaped `&` inside a `<loc>` URL.
- Wrong namespace.

---

## Reading a CI failure

When CI fails on your PR:

1. Open the PR on GitHub.
2. Scroll to the "Checks" or "Actions" tab.
3. Click on the failed step.
4. Look at the log output. Each check prints clear `OK` / `FAIL` lines:

   ```
   OK   index.html
   FAIL products.html: ['unclosed: </div>']
   OK   about.html
   ```

   The first `FAIL` line tells you which file and what's wrong.

5. Fix locally, commit, push. CI re-runs automatically.

---

## Running validators locally before pushing

Saves a round trip. The validator scripts are short Python snippets — run
them inline.

### HTML well-formedness only:

```bash
python3 - <<'EOF'
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

The full set of validators is in `.github/workflows/validate.yml`. Copy
the snippets out of there if you want to run all four locally.

### Or just push and let CI tell you

Honestly, for most cases this is fine. The PR loop is fast. If CI fails,
it fails — fix it and push again. Don't over-optimise the local loop.

---

## What the pre-push checklist looks like

Before opening a PR, run through:

- [ ] I edited the right file (`PRODUCTS` not the generated HTML, etc.).
- [ ] I re-ran the generators if I touched anything in `tools/`.
- [ ] I tested in the browser locally.
- [ ] I'm on a branch, not on `main`.
- [ ] My commit message describes what changed and why.

---

## Rolling back a bad deploy

If a change makes it to `main` and breaks the live site:

### Option A — revert the bad commit

```bash
git checkout main
git pull
git revert <bad-commit-sha>
git push origin main
```

A "Revert <original message>" commit lands on `main`. The host
re-deploys with the previous good version within minutes.

### Option B — point `main` at an older commit (last resort)

```bash
git checkout main
git pull
git reset --hard <known-good-commit-sha>
git push origin main --force-with-lease
```

This rewrites history. Don't do it lightly. Only use if a revert is
problematic for some reason. **Never** force-push to `main` if other
people might have already pulled.

### Option C — hotfix on a branch

For a more controlled rollback:

```bash
git checkout -b hotfix/restore-pricing
# Manually fix the bad change
git commit -m "hotfix: restore correct prices"
git push origin hotfix/restore-pricing
# Open PR, merge as soon as CI passes
```

This is the cleanest pattern for production hotfixes — same workflow as
any other change.

---

## DNS and SSL

Out of the repo's scope, but worth knowing:

- The domain `theflorista.in` is registered separately (via a registrar
  like GoDaddy, Namecheap, BigRock, etc.).
- DNS records point the domain at the static host's CDN.
- SSL is provided by the host automatically (Let's Encrypt or similar).
- If the site goes down, the issue is usually one of: domain expired,
  DNS misconfigured, host outage. Repo changes can't fix these — contact
  the registrar or host directly.

---

## Performance & SEO maintenance

A few things to keep an eye on, monthly or quarterly:

| Check | How |
|-------|-----|
| **Lighthouse score** | Open Chrome DevTools → Lighthouse → run on the home page and a product page. Target: ≥90 across the board. |
| **Search Console errors** | <https://search.google.com/search-console> — set up the property if not already. Check for crawl errors, mobile usability issues, schema warnings. |
| **404 logs** | Static hosts often have an analytics dashboard showing 404s. If you see a recurring 404, add a redirect or fix the broken link. |
| **Image weight** | `du -sh images/` — should stay under ~10 MB total. If it's growing, batch-re-compress the heavy files. |
| **Page weight** | DevTools → Network → check that page load is < 1 MB transferred for first visit. |

---

## When something goes wrong on the live site

Triage order:

1. **Is it a content issue?** (Wrong price, typo, broken link.)
   - Fix in a branch, PR, merge. ~20 minutes round trip.

2. **Is it a JS issue?** (Cart broken, form not submitting, banner stuck.)
   - Open the browser console. Read the error.
   - If it's clear, fix in a branch and PR.
   - If it's a regression from a recent commit, revert that commit
     while you investigate.

3. **Is the whole site down?**
   - Check the host's status page first.
   - Then check DNS (visit the static-host URL directly, bypassing your
     domain — if that works, it's DNS).
   - Then check the registrar (domain expired?).

4. **Is search ranking dropping?**
   - Slower-burning issue. Check Search Console → Coverage for errors.
   - Compare canonicals between similar pages (one of [BUGS_TO_FIX item
     #2](../BUGS_TO_FIX.md)).
   - Check if a recent rename left old URLs without redirects ([Recipe 4
     in Ch 03](./03-managing-products.md#recipe-4--rename-a-product-change-the-slug)).

---

## Branch hygiene

A few conventions that keep the Git history readable:

- **Branch names:** `<type>/<short-description>` — e.g.
  `feature/add-monsoon-banner`, `fix/cart-price-rounding`,
  `content/update-may-prices`.
- **Commit messages:** First line ≤72 chars, written as a command
  ("update", "fix", "add", not "updated", "fixed", "added").
  Body is optional but useful for the *why*.
- **One logical change per PR.** Don't mix a price update and a banner
  redesign in the same PR. Easier to review, easier to revert.
- **Delete merged branches.** GitHub usually has an auto-delete option
  in the repo settings.

---

Next chapter: [10 — Cookbook (Quick Recipes) →](./10-cookbook.md)
