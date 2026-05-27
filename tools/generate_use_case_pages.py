#!/usr/bin/env python3
"""
Generate use-case landing pages from a single source of truth.

Why this exists
---------------
Per-product pages capture queries like ``60 inch giant flora wholesale``.
Use-case pages capture intent queries — the way decorators actually search:
    "flowers for mehndi backdrop wholesale"
    "wedding stage decor flowers bulk"
    "yellow flowers for haldi backdrop"

The pages re-use existing product images (no extra photoshoot or copy
required initially) and link out to the per-product pages so PageRank
flows down to every SKU.

How to use
----------
    python3 tools/generate_use_case_pages.py

Idempotent: re-running overwrites the generated files. Edit ``USE_CASES``
below to add or update use cases, then re-run.
"""
from __future__ import annotations

import html
import json
import pathlib
import urllib.parse
from typing import Any

# Re-use the product database & helpers so we have one source of truth
# for prices, MOQs, image paths, and WhatsApp message generation.
from generate_product_pages import (
    PRODUCTS,
    ROOT,
    SITE_URL,
    WHATSAPP_NUMBER,
    img_url,
    img_abs_url,
)

OUT_DIR = ROOT / "use-cases"
PRODUCT_BY_SLUG: dict[str, dict[str, Any]] = {p["slug"]: p for p in PRODUCTS}


# ---------------------------------------------------------------------------
# Use-case database — single source of truth
# ---------------------------------------------------------------------------
# Field reference:
#   slug                URL slug (kebab-case)
#   name                Short name shown on pills, breadcrumbs, etc.
#   h1                  Page H1 — front-loaded with the search intent
#   tagline             One-liner under the H1
#   meta_description    155-char SEO description
#   intro_paragraphs    1-2 paragraphs of context (factual, no fluff)
#   size_recommendation Plain-English size guidance for this use case
#   color_recommendation Palette guidance
#   recommended_slugs   Ordered list of product slugs (renders as cards;
#                       6-8 looks best in the grid)
#   hero_slug           Product whose first image is used as the OG image
#   feature_bullets     4 trust bullets specific to this use case
#   icon                Font Awesome class (used in the products.html pill)
USE_CASES: list[dict[str, Any]] = [
    {
        "slug": "mehndi-decor",
        "name": "Mehndi Decor",
        "h1": "Wholesale Flowers for Mehndi Decor",
        "tagline": "Pastel-perfect organza florals for mehndi stages, swings & photo backdrops.",
        "meta_description": (
            "Bulk organza flowers for mehndi function decor — soft pastels in "
            "12 to 32 inch sizes for stages, swings, photo walls and ceiling "
            "drops. Direct from Florista's Nagpur factory. PAN India delivery."
        ),
        "intro_paragraphs": [
            "Mehndi events thrive on warmth and softness &mdash; peach, blush, "
            "marigold, mint and dusty pink. Florista&rsquo;s organza florals "
            "come in exactly those tones and the right sizes to layer behind a "
            "swing or fill a photo backdrop without overwhelming the bride.",
            "Decorators typically pair a 24&ndash;32 inch focal piece with a "
            "cluster of 12&ndash;18 inch fillers. Mix shades within a single "
            "order at no extra cost, and combine with our organza butterflies "
            "for ceiling installations.",
        ],
        "size_recommendation": '24"–32" focal pieces with 12"–18" fillers',
        "color_recommendation": "soft pastels &mdash; peaches, yellows, blush, mint",
        "recommended_slugs": [
            "24-inch-wedding-touch",
            "28-inch-wedding-bloom",
            "32-inch-pure-bliss",
            "18-inch-lumora",
            "12-inch-regular-ornela",
            "fluffy-bloom",
            "organza-butterfly",
            "cinderella-flowers",
        ],
        "hero_slug": "24-inch-wedding-touch",
        "feature_bullets": [
            "Soft pastel palette already in stock &mdash; 12 stocked shades you can mix in one order.",
            'Sizes scale from 12" up to 32" so you can layer focal centerpieces with fillers.',
            "MOQ as low as 10 pieces per design &mdash; order one design or the entire palette.",
            "Volumetric shipping calculated PAN India from our Nagpur factory.",
        ],
        "icon": "fa-leaf",
    },
    {
        "slug": "wedding-backdrops",
        "name": "Wedding Backdrops",
        "h1": "Wholesale Flowers for Wedding Backdrops",
        "tagline": "Statement-size organza florals for wedding stages, mandap fronts & reception walls.",
        "meta_description": (
            "Bulk wedding backdrop flowers in 36 to 60 inch sizes plus premium "
            "specialty designs. Direct-from-factory pricing, PAN India shipping "
            "from Florista, Nagpur. MOQ as low as 5 pieces."
        ),
        "intro_paragraphs": [
            "A wedding backdrop reads from across the hall, so size, depth and "
            "colour layering all matter. Our 60 inch Giant Flora and 48 inch "
            "Big Flora are designed to be the centerpieces; everything from 24 "
            "inches downward exists to fill the frame around them.",
            "Most decorators build a wedding backdrop with one or two 60 inch "
            "focal pieces, three to four 36&ndash;48 inch supporting blooms, "
            "and a mass of 24 inch fillers. We ship the structural wire-frame "
            "construction so each piece holds shape across multiple events.",
        ],
        "size_recommendation": '36"–60" focal pieces with 24"–28" fillers',
        "color_recommendation": "white &amp; ivory bases with bold accent shades",
        "recommended_slugs": [
            "60-inch-giant-flora",
            "48-inch-big-flora",
            "44-inch-majestic",
            "40-inch-decor-blooms",
            "36-inch-premium-blooms",
            "aura-flower-3ft",
            "glowing-flower-3ft",
            "24-inch-premium-collection",
        ],
        "hero_slug": "60-inch-giant-flora",
        "feature_bullets": [
            'Largest format in the catalogue: 60" Giant Flora — true 5 ft statement piece.',
            "MOQ from just 5 pieces on the larger sizes — you don't have to over-order.",
            "Wire-frame construction holds shape across multiple weddings &mdash; reusable rental stock.",
            "Mix-and-match colours within one order to match any wedding theme.",
        ],
        "icon": "fa-archway",
    },
    {
        "slug": "stage-decor",
        "name": "Stage Decor",
        "h1": "Wholesale Flowers for Wedding Stage &amp; Reception Decor",
        "tagline": "Premium structured pieces for reception stages, sangeet sets and corporate event walls.",
        "meta_description": (
            "Premium decor flowers for reception stages, sangeet sets and "
            "corporate event backdrops. Illuminated, structured and oversized "
            "designs from Florista, Nagpur. Wholesale pricing, PAN India "
            "delivery."
        ),
        "intro_paragraphs": [
            "Reception and sangeet stages need more than just size &mdash; they "
            "need finish. Our premium specialty range (Glowing Flower, Aura "
            "Flower, Tri-Petal) is built for stage front placement where "
            "structure and silhouette matter as much as colour.",
            "For brightly lit halls, the 60 inch and 48 inch organza florals "
            "carry well. For night-time receptions, pair them with the Glowing "
            "Flower for an integrated illuminated focal piece. All designs ship "
            "with reinforced frames so they survive multiple installations.",
        ],
        "size_recommendation": '36"–60" plus illuminated specialty pieces',
        "color_recommendation": "metallics &amp; deep tones &mdash; gold, ivory, blush, navy",
        "recommended_slugs": [
            "glowing-flower-3ft",
            "aura-flower-3ft",
            "60-inch-giant-flora",
            "48-inch-big-flora",
            "tri-petal-flower-2-5ft",
            "premium-fabric-flowers",
            "cinderella-flowers",
            "36-inch-premium-blooms",
        ],
        "hero_slug": "glowing-flower-3ft",
        "feature_bullets": [
            "Illuminated Glowing Flower (3 ft) for night-event focal pieces &mdash; integrated lighting included.",
            "Tri-Petal and Aura designs read as architectural elements, not just florals.",
            "Reinforced wire frames survive multiple installations &mdash; ideal rental stock.",
            "MOQ from 5 pieces on premium sizes &mdash; trial small, scale up later.",
        ],
        "icon": "fa-star",
    },
    {
        "slug": "haldi-decor",
        "name": "Haldi Decor",
        "h1": "Wholesale Flowers for Haldi Function Decor",
        "tagline": "Yellow, marigold and orange-toned organza florals for haldi backdrops & ceiling drops.",
        "meta_description": (
            "Bulk haldi function decoration flowers in yellow, marigold and "
            "orange tones. Sizes 12 to 28 inches for backdrops, ceiling drops "
            "and seating decor. Direct-from-factory pricing, PAN India "
            "delivery from Florista, Nagpur."
        ),
        "intro_paragraphs": [
            "Haldi events are intimate, daytime, and almost always outdoors or "
            "in well-lit halls &mdash; so the decor needs to be warm-toned and "
            "the scale should support, not dominate. Our yellow, marigold and "
            "orange shades work beautifully solo or layered with the organza "
            "butterfly props for ceiling installations.",
            "Most haldi setups need a small focal panel behind the bride and "
            "filler flowers along the seating frame. The 24 inch and 18 inch "
            "sizes do most of the work; the 12 inch is excellent for tight "
            "filler clusters and ceiling drops.",
        ],
        "size_recommendation": '12"–28" — small fillers and a single focal panel',
        "color_recommendation": "yellows, marigolds, oranges and warm corals",
        "recommended_slugs": [
            "18-inch-lumora",
            "24-inch-wedding-touch",
            "12-inch-regular-ornela",
            "28-inch-wedding-bloom",
            "fluffy-bloom",
            "organza-butterfly",
            "cinderella-flowers",
            "premium-fabric-flowers",
        ],
        "hero_slug": "18-inch-lumora",
        "feature_bullets": [
            "Warm-tone palette already stocked &mdash; pick yellows, marigolds, oranges in one MOQ.",
            "Sizes scaled for daytime haldi stages: focal up to 28 inches, fillers down to 12.",
            "Pair with Organza Butterflies for ceiling installations &mdash; airy without crowding.",
            "MOQ as low as 10 pieces &mdash; order what you need for a single function.",
        ],
        "icon": "fa-sun",
    },
    {
        "slug": "theme-party-decor",
        "name": "Theme Party Decor",
        "h1": "Wholesale Flowers for Theme Party &amp; Kids Birthday Decor",
        "tagline": "Butterflies, fish, angel wings and pastel florals for themed kids events.",
        "meta_description": (
            "Theme-party decoration flowers and props &mdash; butterfly, "
            "under-the-sea fish, 90 inch angel wings, and soft pastel "
            "florals for kids birthdays, baby showers and themed events. "
            "Wholesale pricing from Florista, Nagpur."
        ),
        "intro_paragraphs": [
            "Themed kids events need props more than backdrops &mdash; "
            "butterflies for a butterfly-themed first birthday, fish for an "
            "under-the-sea party, angel wings for a christening photo wall. "
            "Florista&rsquo;s theme range was designed exactly for these moments.",
            "Pair the themed props with soft pastel organza florals for the "
            "frame around the cake or the photo backdrop. The 12 inch and 18 "
            "inch organza work well as filler at kids-event scale &mdash; the "
            "60 inch range is generally too imposing here.",
        ],
        "size_recommendation": "themed props plus 12''&ndash;24'' filler florals",
        "color_recommendation": "bright pastels and theme-matched accent colours",
        "recommended_slugs": [
            "organza-butterfly",
            "theme-party-fish",
            "dream-wings-90-inch",
            "fluffy-bloom",
            "cinderella-flowers",
            "18-inch-lumora",
            "12-inch-regular-ornela",
            "premium-fabric-flowers",
        ],
        "hero_slug": "organza-butterfly",
        "feature_bullets": [
            "Theme-specific props in stock &mdash; butterflies, fish, 90 inch angel wings.",
            "Smaller-scale florals (12 inch, 18 inch) keep kids events feeling fun, not formal.",
            "MOQ from 5 pieces on the angel-wing size &mdash; you can order one set per event.",
            "All pieces are reusable across multiple events with minimal storage footprint.",
        ],
        "icon": "fa-party-horn",
    },
]


# ---------------------------------------------------------------------------
# Schema generators
# ---------------------------------------------------------------------------

def breadcrumb_jsonld(uc: dict[str, Any]) -> dict[str, Any]:
    """Home > Use Cases > <name>."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Products",
             "item": f"{SITE_URL}/products.html"},
            {"@type": "ListItem", "position": 3, "name": uc["name"],
             "item": f"{SITE_URL}/use-cases/{uc['slug']}.html"},
        ],
    }


def itemlist_jsonld(uc: dict[str, Any]) -> dict[str, Any]:
    """ItemList of recommended products. Lets Google show this page as a
    'collection' result and surface the listed products inline."""
    items = []
    for i, slug in enumerate(uc["recommended_slugs"], start=1):
        p = PRODUCT_BY_SLUG[slug]
        items.append({
            "@type": "ListItem",
            "position": i,
            "url": f"{SITE_URL}/products/{slug}.html",
            "name": p["name"],
            "image": img_abs_url(p["image_prefix"], p["image_indices"][0]),
        })
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Recommended flowers for {uc['name']}",
        "description": strip_html(uc["meta_description"]),
        "numberOfItems": len(items),
        "itemListElement": items,
    }


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def strip_html(s: str) -> str:
    """Strip HTML entities from a string for use in plaintext schema fields."""
    return (s.replace("&mdash;", "—").replace("&ndash;", "–")
             .replace("&amp;", "&").replace("&rsquo;", "'")
             .replace("&nbsp;", " "))


def render_intro(uc: dict[str, Any]) -> str:
    return "\n                ".join(
        f"<p>{para}</p>" for para in uc["intro_paragraphs"]
    )


def render_features(uc: dict[str, Any]) -> str:
    rows = []
    for b in uc["feature_bullets"]:
        rows.append(
            f'                    <li>'
            f'<i class="fas fa-check-circle"></i>'
            f'<span>{b}</span></li>'
        )
    return "\n".join(rows)


def render_recommended_cards(uc: dict[str, Any]) -> str:
    """Render the recommended-products grid.

    Cards mirror products.html structure (`.product-card[data-price]`) so
    quote-cart.js auto-wires the floating cart's "+" button on each card.
    The whole card is wrapped in a link to the per-product page.
    """
    cards = []
    for slug in uc["recommended_slugs"]:
        p = PRODUCT_BY_SLUG[slug]
        name_e = html.escape(p["name"])
        cards.append(f"""                <article class="uc-card product-card reveal"
                         data-id="{slug}"
                         data-size="{p['size_inch']}"
                         data-price="{p['price_min']}"
                         data-moq="{p['moq']}">
                    <a class="uc-card-link" href="../products/{slug}.html"
                       aria-label="View details for {name_e}">
                        <div class="card-img-wrap">
                            <img class="main-img" src="{img_url(p['image_prefix'], p['image_indices'][0])}"
                                 alt="{name_e} &mdash; {html.escape(p['size_label'])} wholesale decor flower"
                                 loading="lazy">
                            <div class="variant-badge">{p['shade_count']} shades</div>
                        </div>
                        <div class="card-body">
                            <h3>{name_e}</h3>
                            <p class="desc">{html.escape(p['tagline'])}</p>
                            <span class="moq-chip"><i class="fas fa-box-open"></i> MOQ {p['moq']} pcs</span>
                            <div class="card-footer-row">
                                <span class="card-price">{html.escape(p['price_display'])}</span>
                                <span class="uc-card-cta">Details <i class="fas fa-arrow-right"></i></span>
                            </div>
                        </div>
                    </a>
                </article>""")
    return "\n".join(cards)


def render_related_use_cases(current: dict[str, Any]) -> str:
    """Other use cases shown at the bottom for cross-linking."""
    cards = []
    for uc in USE_CASES:
        if uc["slug"] == current["slug"]:
            continue
        hero = PRODUCT_BY_SLUG[uc["hero_slug"]]
        img = img_url(hero["image_prefix"], hero["image_indices"][0])
        cards.append(f"""                <a class="uc-related-card" href="{uc['slug']}.html">
                    <div class="uc-related-img-wrap">
                        <img src="{img}" alt="{html.escape(uc['name'])}" loading="lazy">
                    </div>
                    <div class="uc-related-body">
                        <i class="fas {uc['icon']}"></i>
                        <strong>{html.escape(uc['name'])}</strong>
                        <span>View recommended pieces &rarr;</span>
                    </div>
                </a>""")
    return "\n".join(cards)


def wa_link(message: str) -> str:
    return (f"https://wa.me/{WHATSAPP_NUMBER}?text="
            + urllib.parse.quote(message))


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_e}</title>
    <meta name="description" content="{description_e}">
    <link rel="canonical" href="{canonical}">

    <!-- Open Graph -->
    <meta property="og:title" content="{title_e}">
    <meta property="og:description" content="{description_e}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Florista">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_e}">
    <meta name="twitter:description" content="{description_e}">
    <meta name="twitter:image" content="{og_image}">

    <!-- Favicons -->
    <link rel="icon" href="../images/favicon.ico" sizes="any">
    <link rel="icon" href="../images/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="../images/apple-touch-icon.png">

    <!-- Preconnect for performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">

    <!-- CSS -->
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-T5GR1DL2G0"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('consent', 'default', {{
        analytics_storage:
          (typeof localStorage !== 'undefined'
            && localStorage.getItem('florista-consent') === 'accepted')
            ? 'granted' : 'denied',
        ad_storage: 'denied'
      }});
      gtag('js', new Date());
      gtag('config', 'G-T5GR1DL2G0');
    </script>

    <!-- Breadcrumb schema -->
    <script type="application/ld+json">
{breadcrumb_jsonld}
    </script>

    <!-- ItemList schema for recommended products -->
    <script type="application/ld+json">
{itemlist_jsonld}
    </script>

    <style>
        /* ── Use-case page layout ───────────────────────────────── */
        .uc-breadcrumb {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            color: var(--color-gray);
            padding: 18px 0 4px;
        }}
        .uc-breadcrumb a {{ color: var(--color-gray); transition: color 0.2s ease; }}
        .uc-breadcrumb a:hover {{ color: var(--color-primary-dark); }}
        .uc-breadcrumb .sep {{ opacity: 0.5; }}
        .uc-breadcrumb .current {{ color: var(--color-dark); font-weight: 500; }}

        /* Hero */
        .uc-hero {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr);
            gap: 48px;
            align-items: center;
            padding: 24px 0 50px;
        }}
        .uc-hero-text .uc-eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--color-primary-dark);
            background: var(--color-primary-light);
            padding: 6px 14px;
            border-radius: 50px;
            margin-bottom: 18px;
        }}
        .uc-hero-text h1 {{
            font-size: clamp(1.9rem, 3.6vw, 2.7rem);
            margin-bottom: 12px;
            line-height: 1.18;
        }}
        .uc-hero-text .uc-tagline {{
            font-size: 1.05rem;
            color: var(--color-gray);
            margin-bottom: 18px;
        }}
        .uc-hero-text p {{
            color: var(--color-gray);
            line-height: 1.75;
            margin-bottom: 14px;
        }}
        .uc-hero-text strong {{ color: var(--color-dark); }}
        .uc-hero-cta {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 22px;
        }}
        .uc-hero-img-wrap {{
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 22px;
            padding: 18px;
            box-shadow: var(--glass-shadow);
            aspect-ratio: 1 / 1;
            overflow: hidden;
        }}
        .uc-hero-img-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.5s ease;
        }}
        .uc-hero-img-wrap:hover img {{ transform: scale(1.04); }}

        /* Quick-facts strip */
        .uc-facts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin: 0 0 50px;
        }}
        .uc-fact {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: var(--glass-shadow);
        }}
        .uc-fact .label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--color-gray);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .uc-fact .label i {{ color: var(--color-primary-dark); }}
        .uc-fact .value {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--color-dark);
        }}

        /* Feature bullets */
        .uc-features {{
            list-style: none;
            padding: 0;
            margin: 0 0 50px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 14px;
        }}
        .uc-features li {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 16px;
            box-shadow: var(--glass-shadow);
            font-size: 0.92rem;
            color: var(--color-dark);
            line-height: 1.5;
        }}
        .uc-features li i {{
            color: #1f6b3a;
            margin-top: 4px;
            flex-shrink: 0;
        }}

        /* Section title */
        .uc-section-title {{
            text-align: center;
            margin-bottom: 28px;
        }}
        .uc-section-title .uc-section-label {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--color-primary-dark);
            margin-bottom: 8px;
        }}
        .uc-section-title h2 {{
            font-size: clamp(1.4rem, 2.6vw, 1.8rem);
            margin: 0;
        }}

        /* Recommended products grid */
        .uc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 24px;
            margin-bottom: 70px;
        }}
        .uc-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
            transition: var(--transition);
            position: relative;
        }}
        .uc-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 22px 56px rgba(80,30,60,0.13);
            border-color: rgba(201,126,160,0.35);
        }}
        .uc-card-link {{
            display: flex;
            flex-direction: column;
            color: inherit;
            text-decoration: none;
            height: 100%;
        }}
        .uc-card .card-img-wrap {{
            position: relative;
            width: 100%;
            height: 230px;
            overflow: hidden;
            background: rgba(245,213,228,0.12);
        }}
        .uc-card .main-img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 8px;
            transition: transform 0.45s ease;
        }}
        .uc-card:hover .main-img {{ transform: scale(1.05); }}
        .uc-card .variant-badge {{
            position: absolute;
            top: 12px; left: 12px;
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--color-primary-dark);
        }}
        .uc-card .card-body {{
            padding: 16px 18px 18px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .uc-card h3 {{
            font-family: var(--font-sans);
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 4px;
        }}
        .uc-card .desc {{
            font-size: 0.83rem;
            color: var(--color-gray);
            margin: 0 0 12px;
            flex: 1;
        }}
        .uc-card .moq-chip {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--color-secondary);
            color: #1f6b3a;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 50px;
            margin-bottom: 12px;
            width: fit-content;
        }}
        .uc-card .card-footer-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}
        .uc-card .card-price {{
            font-weight: 700;
            font-size: 0.95rem;
            color: var(--color-primary-dark);
            white-space: nowrap;
        }}
        .uc-card-cta {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--color-primary-dark);
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .uc-card:hover .uc-card-cta {{ gap: 7px; }}
        .uc-card-cta i {{ font-size: 0.7rem; transition: transform 0.25s ease; }}
        .uc-card:hover .uc-card-cta i {{ transform: translateX(2px); }}

        /* Related use cases */
        .uc-related-section {{
            padding: 50px 0 30px;
            border-top: 1px solid rgba(201,126,160,0.18);
        }}
        .uc-related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-top: 28px;
        }}
        .uc-related-card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
            transition: var(--transition);
            color: inherit;
            text-decoration: none;
            display: flex;
            flex-direction: column;
        }}
        .uc-related-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 16px 40px rgba(80,30,60,0.12);
            border-color: rgba(201,126,160,0.3);
        }}
        .uc-related-img-wrap {{
            aspect-ratio: 4 / 3;
            overflow: hidden;
            background: rgba(245,213,228,0.12);
        }}
        .uc-related-img-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 6px;
        }}
        .uc-related-body {{
            padding: 14px 16px 16px;
            text-align: center;
        }}
        .uc-related-body i {{
            color: var(--color-primary-dark);
            font-size: 1.15rem;
            margin-bottom: 6px;
            display: block;
        }}
        .uc-related-body strong {{
            display: block;
            font-size: 0.95rem;
            color: var(--color-dark);
            margin-bottom: 4px;
        }}
        .uc-related-body span {{
            font-size: 0.78rem;
            color: var(--color-gray);
        }}

        /* Final CTA */
        .uc-final-cta {{
            text-align: center;
            background: linear-gradient(135deg, var(--color-primary-light), rgba(255,255,255,0.5));
            border: 1px solid var(--glass-border);
            border-radius: 22px;
            padding: 40px 28px;
            margin: 30px 0 60px;
            box-shadow: var(--glass-shadow);
        }}
        .uc-final-cta h2 {{
            font-size: clamp(1.3rem, 2.4vw, 1.7rem);
            margin-bottom: 10px;
        }}
        .uc-final-cta p {{
            color: var(--color-gray);
            margin-bottom: 22px;
            max-width: 540px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Responsive */
        @media (max-width: 880px) {{
            .uc-hero {{ grid-template-columns: 1fr; gap: 28px; padding: 16px 0 40px; }}
            .uc-hero-img-wrap {{ max-width: 380px; margin: 0 auto; }}
        }}
    </style>
</head>
<body>

    <header class="site-header">
        <div class="container">
            <a href="../index.html" class="logo">Florista<span>.</span></a>
            <nav class="main-nav">
                <a href="../index.html" class="nav-link">Home</a>
                <a href="../products.html" class="nav-link">Products</a>
                <a href="../wholesale.html" class="nav-link">Wholesale &amp; Logistics</a>
                <a href="../about.html" class="nav-link">About Us</a>
                <a href="../contact.html" class="nav-link">Contact</a>
            </nav>
            <button class="mobile-menu-btn" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
        </div>
    </header>

    <main>
        <div class="container">

            <!-- Breadcrumb -->
            <nav class="uc-breadcrumb" aria-label="Breadcrumb">
                <a href="../index.html">Home</a>
                <span class="sep">/</span>
                <a href="../products.html">Products</a>
                <span class="sep">/</span>
                <span class="current" aria-current="page">{name_e}</span>
            </nav>

            <!-- Hero -->
            <section class="uc-hero">
                <div class="uc-hero-text">
                    <span class="uc-eyebrow"><i class="fas {icon}"></i> {name_e}</span>
                    <h1>{h1}</h1>
                    <p class="uc-tagline">{tagline}</p>
                    {intro_html}
                    <div class="uc-hero-cta">
                        <a href="{wa_enquire}" class="btn btn-whatsapp" target="_blank" rel="noopener">
                            <i class="fab fa-whatsapp"></i> Get a {name_e} quote
                        </a>
                        <a href="../products.html" class="btn btn-outline">Browse full catalogue</a>
                    </div>
                </div>
                <div class="uc-hero-img-wrap">
                    <img src="{hero_image}" alt="{name_e} flowers by Florista" loading="eager" fetchpriority="high">
                </div>
            </section>

            <!-- Quick facts -->
            <div class="uc-facts">
                <div class="uc-fact">
                    <div class="label"><i class="fas fa-ruler-combined"></i> Recommended sizes</div>
                    <div class="value">{size_recommendation}</div>
                </div>
                <div class="uc-fact">
                    <div class="label"><i class="fas fa-palette"></i> Suggested palette</div>
                    <div class="value">{color_recommendation}</div>
                </div>
                <div class="uc-fact">
                    <div class="label"><i class="fas fa-box-open"></i> MOQ</div>
                    <div class="value">From 5&ndash;10 pieces per design</div>
                </div>
                <div class="uc-fact">
                    <div class="label"><i class="fas fa-truck"></i> Shipping</div>
                    <div class="value">PAN India from Nagpur</div>
                </div>
            </div>

            <!-- Why Florista bullets -->
            <ul class="uc-features">
{features_html}
            </ul>

            <!-- Recommended products -->
            <div class="uc-section-title">
                <span class="uc-section-label">Curated Selection</span>
                <h2>Recommended pieces for {name_e}</h2>
            </div>
            <div class="uc-grid">
{recommended_html}
            </div>

            <!-- Final CTA -->
            <section class="uc-final-cta">
                <h2>Building a {name_e} setup?</h2>
                <p>Send us your requirement on WhatsApp &mdash; sizes, shades and quantities &mdash; and we&rsquo;ll come back with a packed quote including PAN-India shipping.</p>
                <a href="{wa_enquire}" class="btn btn-whatsapp" target="_blank" rel="noopener">
                    <i class="fab fa-whatsapp"></i> Chat with Florista
                </a>
            </section>

            <!-- Related use cases -->
            <section class="uc-related-section">
                <div class="uc-section-title">
                    <span class="uc-section-label">Other Event Types</span>
                    <h2>More use-case guides</h2>
                </div>
                <div class="uc-related-grid">
{related_html}
                </div>
            </section>

        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <a href="../index.html" class="logo" style="margin-bottom:14px;display:block;">Florista<span>.</span></a>
                    <p>Bulk Decor Manufacturer.<br>Premium Quality at Factory Prices.<br>Nagpur, Maharashtra.</p>
                    <div class="footer-social">
                        <a href="https://wa.me/917588447595" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
                        <a href="https://www.instagram.com/thefloristaflowerss/" target="_blank" rel="noopener" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
                        <a href="tel:+917588447595" aria-label="Call"><i class="fas fa-phone"></i></a>
                    </div>
                </div>
                <div class="footer-col">
                    <h4>Products</h4>
                    <ul class="footer-links">
                        <li><a href="../products.html#organza">Organza Flowers</a></li>
                        <li><a href="../products.html#premium">Premium &amp; Specialty</a></li>
                        <li><a href="../products.html#theme">Theme &amp; Events</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Company</h4>
                    <ul class="footer-links">
                        <li><a href="../about.html">About Us</a></li>
                        <li><a href="../wholesale.html">Wholesale Policy</a></li>
                        <li><a href="../contact.html">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Get In Touch</h4>
                    <p style="margin-bottom:10px;"><i class="fab fa-whatsapp" style="color:#25D366;margin-right:8px;"></i>+91 75884 47595</p>
                    <p><i class="fas fa-map-marker-alt" style="color:var(--color-primary);margin-right:8px;"></i>Nagpur, Maharashtra</p>
                </div>
                <div class="footer-col">
                    <h4>Legal</h4>
                    <ul class="footer-links">
                        <li><a href="../privacy.html">Privacy Policy</a></li>
                        <li><a href="../terms.html">Terms &amp; Conditions</a></li>
                        <li><a href="../refund.html">Refund &amp; Cancellation</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 The Florista Flowers. All rights reserved. Handcrafted in Nagpur.</p>
            </div>
        </div>
    </footer>

    <a href="https://wa.me/917588447595" class="floating-whatsapp" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
    <button class="back-to-top" aria-label="Back to top"><i class="fas fa-chevron-up"></i></button>

    <script src="../js/main.js"></script>
    <script src="../js/quote-cart.js"></script>
</body>
</html>
"""


def render_page(uc: dict[str, Any]) -> str:
    hero = PRODUCT_BY_SLUG[uc["hero_slug"]]
    title = f"{uc['name']} Flowers Wholesale | Florista Nagpur"
    return PAGE_TEMPLATE.format(
        title_e=html.escape(title),
        description_e=html.escape(strip_html(uc["meta_description"])),
        canonical=f"{SITE_URL}/use-cases/{uc['slug']}.html",
        og_image=img_abs_url(hero["image_prefix"], hero["image_indices"][0]),
        breadcrumb_jsonld=json.dumps(breadcrumb_jsonld(uc), indent=2),
        itemlist_jsonld=json.dumps(itemlist_jsonld(uc), indent=2),
        # Hero
        name_e=html.escape(uc["name"]),
        h1=uc["h1"],
        tagline=uc["tagline"],
        icon=uc["icon"],
        intro_html=render_intro(uc),
        wa_enquire=wa_link(
            f"Hi Florista, I'm planning {uc['name']} decor and "
            f"would like a wholesale quote. Could you share recommended "
            f"pieces and slab pricing?"
        ),
        hero_image=img_url(hero["image_prefix"], hero["image_indices"][0]),
        # Facts
        size_recommendation=uc["size_recommendation"],
        color_recommendation=uc["color_recommendation"],
        # Sections
        features_html=render_features(uc),
        recommended_html=render_recommended_cards(uc),
        related_html=render_related_use_cases(uc),
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    seen: set[str] = set()
    for uc in USE_CASES:
        if uc["slug"] in seen:
            raise SystemExit(f"Duplicate slug: {uc['slug']}")
        seen.add(uc["slug"])
        # Sanity: every recommended slug must be a real product
        for s in uc["recommended_slugs"]:
            if s not in PRODUCT_BY_SLUG:
                raise SystemExit(
                    f"Use case '{uc['slug']}' references unknown "
                    f"product slug '{s}'"
                )
        if uc["hero_slug"] not in PRODUCT_BY_SLUG:
            raise SystemExit(
                f"Use case '{uc['slug']}' has unknown hero_slug "
                f"'{uc['hero_slug']}'"
            )

        out_path = OUT_DIR / f"{uc['slug']}.html"
        out_path.write_text(render_page(uc), encoding="utf-8")
        print(f"  wrote {out_path.relative_to(ROOT)}")

    print(f"\nGenerated {len(USE_CASES)} use-case pages in "
          f"{OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
