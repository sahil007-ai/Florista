# 01 — Getting Started

This chapter gets you from "I just cloned the repo" to "I can see the site
in my browser and I can edit it." It takes about 10 minutes.

---

## What you need installed

| Tool | Why | How to check |
|------|-----|--------------|
| **Git** | Source control | `git --version` |
| **Python 3.8+** | Runs the product-page generator and the local preview server | `python3 --version` |
| A text editor | VS Code, Sublime, Notepad++, anything | — |
| A modern browser | Chrome, Firefox, Safari, Edge | — |

You do **not** need Node.js, npm, Webpack, Docker, or any framework. The
site is plain HTML, CSS, and vanilla JavaScript.

> **Windows users:** You can use Git Bash (comes with Git for Windows) for
> all the shell commands shown in this manual. Or use PowerShell — the
> commands are the same except where noted.

---

## Get the code

```bash
git clone https://github.com/sahil007-ai/Florista.git
cd Florista
```

That's it. There is no `npm install`, no `pip install`. The Python scripts
use only the standard library.

---

## Preview the site locally

The site is static HTML, so the simplest possible local server works:

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000> in your browser. You should see the home page.

> **Why not just double-click `index.html`?** Browsers block some features
> (relative paths, fetches, service workers) when a page is loaded via
> `file://`. Always serve through `http://` for local previews.

To stop the server, press `Ctrl+C` in the terminal.

---

## Make your first edit

Let's confirm everything's working with a tiny throwaway edit.

1. Open `index.html` in your editor.
2. Search for `Premium Organza Flowers at`.
3. Change the headline to something silly, like
   `Premium Organza Flowers at Local Test Prices`.
4. Save the file.
5. Reload <http://localhost:8000> in your browser. The new headline should appear.
6. **Undo your edit** (or `git checkout index.html`). Don't commit the silly headline.

If steps 1–6 worked, you're ready.

---

## Run the product generator

The `/products/*.html` and `/use-cases/*.html` pages are generated. Try
running the generator now to confirm Python is happy:

```bash
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py
```

You should see no errors. The 22 product pages and 5 use-case pages get
overwritten — but with identical content, so `git status` should show no
changes.

If the scripts fail, see [Troubleshooting](#troubleshooting) below.

---

## Run the validators (optional but recommended)

Every push to GitHub triggers a CI workflow that validates the site. You
can run the same checks locally before pushing — saves a round trip.

The validators live in `.github/workflows/validate.yml`. They're Python
snippets, so you can run them inline. The cookbook has a one-liner; for
now, just trust that GitHub Actions will catch issues if you forget.

See [Chapter 09 — Deployment & CI](./09-deployment.md) for details on what
each check does and how to interpret a failure.

---

## What's running where

For mental model purposes:

```
Your laptop                      GitHub                       theflorista.in
─────────────                   ────────                      ───────────────
git clone     ──────────►       main branch    ──── deploys ──►  live site
git push      ──────────►       runs CI checks
git pull      ◄──────────       on every PR
```

The site is hosted on a static host (the actual host is configured in the
repo's deployment settings — typically GitHub Pages or a similar CDN).
Anything that lands on `main` ends up on production within a few minutes.

That's why **every change goes through a Pull Request first**. The CI
checks run on the PR, you (or a reviewer) get one last look, and only
then does it merge to `main`.

---

## Daily workflow

Once you're set up, every change follows the same shape:

```bash
# 1. Start from a clean main
git checkout main
git pull

# 2. Branch
git checkout -b update-prices-may

# 3. Edit files. Save. Refresh browser. Repeat.

# 4. If you touched anything in tools/, regenerate
python3 tools/generate_product_pages.py
python3 tools/generate_use_case_pages.py

# 5. Commit
git add -A
git commit -m "update prices for May 2026 catalogue"

# 6. Push and open a PR
git push origin update-prices-may
```

Don't push directly to `main`. Always work on a branch.

---

## Troubleshooting

**`python3: command not found`**

On macOS, install Python via [python.org](https://www.python.org/downloads/)
or use Homebrew (`brew install python`). On Windows, install from
python.org and tick "Add Python to PATH" during install. On Linux, use
your package manager (`apt install python3`, `dnf install python3`, etc).

**The browser shows "Address already in use" when starting the server**

Another process is using port 8000. Either kill it or pick a different
port: `python3 -m http.server 8001` and visit <http://localhost:8001>.

**The generator fails with `ModuleNotFoundError: No module named 'product_content'`**

Run the script from the **repo root**, not from inside `tools/`:

```bash
# From repo root, this works:
python3 tools/generate_product_pages.py

# From inside tools/, you'd need:
cd tools && python3 generate_product_pages.py
```

The script handles both cases via a `sys.path.insert()` near the top, so
either should work. If it still fails, you may have a stale `__pycache__`
folder — delete `tools/__pycache__/` and try again.

**Browser is showing an old version of the page after I edited a file**

Hard refresh: `Ctrl+Shift+R` (Windows / Linux) or `Cmd+Shift+R` (Mac).
Browsers aggressively cache CSS and JS files. The live site sets cache
headers correctly via the host; for local development, hard refresh.

---

Next chapter: [02 — Project Structure →](./02-project-structure.md)
