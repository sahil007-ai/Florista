#!/usr/bin/env python3
"""
Generate per-product SEO landing pages from a single source of truth.

Why this exists
---------------
Florista has 22 products that previously all lived on products.html under #anchors.
Search engines (and AI search) reward dedicated URLs per product. This script
templates out one HTML file per product into ``/products/<slug>.html`` so each
SKU can rank for its own long-tail query (e.g. "60 inch wedding backdrop
flower wholesale Nagpur").

How to use
----------
    python3 tools/generate_product_pages.py

Idempotent: re-running overwrites the generated files. Edit ``PRODUCTS``
below to add/remove items or update prices, then re-run.
"""
from __future__ import annotations

import html
import json
import pathlib
import sys
import urllib.parse
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "products"
SITE_URL = "https://www.theflorista.in"
WHATSAPP_NUMBER = "917588447595"

# Per-product expressive content (narrative, built_for, pairs_with,
# craft_note, contact_hook) lives in tools/product_content.py so the
# template logic in this file stays small. Sibling-file import — add
# tools/ to sys.path so the script works from any cwd, including
# `python3 tools/generate_product_pages.py` from the repo root.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from product_content import (  # noqa: E402  (sys.path tweak above)
    CONTENT_BY_SLUG,
    FLORISTA_PROMISE,
    HOOK_REASSURANCE,
)

# ---------------------------------------------------------------------------
# Product database — single source of truth
# ---------------------------------------------------------------------------
# Field reference:
#   slug          URL slug (kebab-case)
#   name          Display name (may contain inch quotes)
#   category      organza | premium | theme  (matches anchors on products.html)
#   size_inch     Numeric size used for filtering (matches data-size on cards)
#   size_label    Human label, e.g. '60"' or '90"' or '3 ft'
#   size_meta     Approximate metric size used in copy
#   shade_count   Number of colour variants offered
#   moq           Minimum order quantity (pieces)
#   price_min     Numeric, INR
#   price_max     Numeric, INR (= price_min when single-price)
#   price_display Pretty string used in the card and product page
#   image_prefix  Filename prefix in /images, before the index
#   image_indices List of integer suffixes (most products are [1,2,...,N];
#                 dream_wings is [1, 3] because file 2 doesn't exist)
#   tagline       One-liner shown on the catalogue card
#   use_case      Phrase plugged into description templates
PRODUCTS: list[dict[str, Any]] = [
    # ── Organza Flowers (11) ────────────────────────────────────────────
    {
        "slug": "12-inch-regular-ornela",
        "name": '12" Regular & Ornela',
        "category": "organza",
        "size_inch": 12,
        "size_label": '12"',
        "size_meta": "30 cm",
        "shade_count": 11,
        "moq": 10,
        "price_min": 230,
        "price_max": 275,
        "price_display": "Rs. 230 – Rs. 275",
        "image_prefix": "product_organza_12_inch",
        "image_indices": list(range(1, 12)),
        "tagline": "12 pastel shades available",
        "use_case": "candy bars, aisle markers and small backdrop fillers",
    },
    {
        "slug": "18-inch-lumora",
        "name": '18" Lumora',
        "category": "organza",
        "size_inch": 18,
        "size_label": '18"',
        "size_meta": "46 cm",
        "shade_count": 11,
        "moq": 10,
        "price_min": 375,
        "price_max": 375,
        "price_display": "Rs. 375",
        "image_prefix": "product_organza_18_inch",
        "image_indices": list(range(1, 12)),
        "tagline": "12 pastel shades available",
        "use_case": "entry decor, mandap pillars and aisle accents",
    },
    {
        "slug": "24-inch-wedding-touch",
        "name": '24" Wedding Touch',
        "category": "organza",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 13,
        "moq": 10,
        "price_min": 375,
        "price_max": 375,
        "price_display": "Rs. 375",
        "image_prefix": "product_organza_24_inch",
        "image_indices": list(range(1, 14)),
        "tagline": "Perfect for intimate backdrops",
        "use_case": "intimate backdrops, photo booths and table centerpieces",
    },
    {
        "slug": "24-inch-premium-collection",
        "name": '24" Premium Collection',
        "category": "organza",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 20,
        "moq": 10,
        "price_min": 375,
        "price_max": 450,
        "price_display": "Rs. 375 – Rs. 450",
        "image_prefix": "product_organza_24_inch_premium",
        "image_indices": list(range(1, 21)),
        "tagline": "Large-format premium prints",
        "use_case": "premium-finish wedding stages and corporate event backdrops",
    },
    {
        "slug": "28-inch-wedding-bloom",
        "name": '28" Wedding Bloom',
        "category": "organza",
        "size_inch": 28,
        "size_label": '28"',
        "size_meta": "71 cm",
        "shade_count": 12,
        "moq": 10,
        "price_min": 450,
        "price_max": 450,
        "price_display": "Rs. 450",
        "image_prefix": "product_organza_28_inch",
        "image_indices": list(range(1, 13)),
        "tagline": "Premium finish for events",
        "use_case": "mid-tier wedding backdrops and reception stages",
    },
    {
        "slug": "32-inch-pure-bliss",
        "name": '32" Pure Bliss',
        "category": "organza",
        "size_inch": 32,
        "size_label": '32"',
        "size_meta": "81 cm",
        "shade_count": 12,
        "moq": 10,
        "price_min": 550,
        "price_max": 675,
        "price_display": "Rs. 550 – Rs. 675",
        "image_prefix": "product_organza_32_inch",
        "image_indices": list(range(1, 13)),
        "tagline": "Large statement pieces",
        "use_case": "wedding stage decor and large mandap fronts",
    },
    {
        "slug": "36-inch-premium-blooms",
        "name": '36" Premium Blooms',
        "category": "organza",
        "size_inch": 36,
        "size_label": '36" / 3 ft',
        "size_meta": "91 cm",
        "shade_count": 14,
        "moq": 10,
        "price_min": 750,
        "price_max": 750,
        "price_display": "Rs. 750",
        "image_prefix": "product_organza_36_inch",
        "image_indices": list(range(1, 15)),
        "tagline": "Elegant 36\" variants",
        "use_case": "backdrop centerpieces and stage focal points",
    },
    {
        "slug": "40-inch-decor-blooms",
        "name": '40" Decor Blooms',
        "category": "organza",
        "size_inch": 40,
        "size_label": '40"',
        "size_meta": "102 cm",
        "shade_count": 13,
        "moq": 10,
        "price_min": 950,
        "price_max": 950,
        "price_display": "Rs. 950",
        "image_prefix": "product_organza_40_inch",
        "image_indices": list(range(1, 14)),
        "tagline": "Stage & backdrop decor",
        "use_case": "stage fronts and large backdrop installations",
    },
    {
        "slug": "44-inch-majestic",
        "name": '44" Majestic',
        "category": "organza",
        "size_inch": 44,
        "size_label": '44"',
        "size_meta": "112 cm",
        "shade_count": 13,
        "moq": 10,
        "price_min": 1200,
        "price_max": 1200,
        "price_display": "Rs. 1,200",
        "image_prefix": "product_organza_44_inch",
        "image_indices": list(range(1, 14)),
        "tagline": "For grand stage decor",
        "use_case": "grand stage decor and oversized photo backdrops",
    },
    {
        "slug": "48-inch-big-flora",
        "name": '48" Big Flora',
        "category": "organza",
        "size_inch": 48,
        "size_label": '48" / 4 ft',
        "size_meta": "122 cm",
        "shade_count": 13,
        "moq": 5,
        "price_min": 1500,
        "price_max": 1500,
        "price_display": "Rs. 1,500",
        "image_prefix": "product_organza_48_inch",
        "image_indices": list(range(1, 14)),
        "tagline": "Massive floral centerpieces",
        "use_case": "massive centerpieces and grand reception backdrops",
    },
    {
        "slug": "60-inch-giant-flora",
        "name": '60" Giant Flora',
        "category": "organza",
        "size_inch": 60,
        "size_label": '60" / 5 ft',
        "size_meta": "152 cm",
        "shade_count": 13,
        "moq": 5,
        "price_min": 2500,
        "price_max": 2500,
        "price_display": "Rs. 2,500",
        "image_prefix": "product_organza_60_inch",
        "image_indices": list(range(1, 14)),
        "tagline": "Our largest masterpiece",
        "use_case": "grand stage backdrops and statement focal pieces",
    },
    # ── Premium & Specialty (8) ─────────────────────────────────────────
    {
        "slug": "glowing-flower-3ft",
        "name": "Glowing Flower (3ft)",
        "category": "premium",
        "size_inch": 36,
        "size_label": "3 ft (36\")",
        "size_meta": "91 cm",
        "shade_count": 2,
        "moq": 5,
        "price_min": 2300,
        "price_max": 2300,
        "price_display": "Rs. 2,300",
        "image_prefix": "product_glowing_flower",
        "image_indices": [1, 2],
        "tagline": "Illuminated elegant decor",
        "use_case": "premium illuminated stages and night-event focal pieces",
    },
    {
        "slug": "aura-flower-3ft",
        "name": "Aura Flower (3ft)",
        "category": "premium",
        "size_inch": 36,
        "size_label": "3 ft (36\")",
        "size_meta": "91 cm",
        "shade_count": 2,
        "moq": 5,
        "price_min": 1699,
        "price_max": 1699,
        "price_display": "Rs. 1,699",
        "image_prefix": "product_aura_flower",
        "image_indices": [1, 2],
        "tagline": "Premium structural design",
        "use_case": "modern wedding stages and luxury reception backdrops",
    },
    {
        "slug": "tri-petal-flower-2-5ft",
        "name": "Tri-Petal Flower (2.5ft)",
        "category": "premium",
        "size_inch": 30,
        "size_label": "2.5 ft (30\")",
        "size_meta": "76 cm",
        "shade_count": 2,
        "moq": 10,
        "price_min": 1200,
        "price_max": 1200,
        "price_display": "Rs. 1,200",
        "image_prefix": "product_tri_petal_flower",
        "image_indices": [1, 2],
        "tagline": "Unique geometric style",
        "use_case": "modern themed stages and design-forward photo walls",
    },
    {
        "slug": "cinderella-flowers",
        "name": "Cinderella Flowers",
        "category": "premium",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 2,
        "moq": 10,
        "price_min": 1025,
        "price_max": 1025,
        "price_display": "From Rs. 1,025",
        "image_prefix": "product_cinderella_flowers",
        "image_indices": [1, 2],
        "tagline": "Fairytale aesthetic",
        "use_case": "fairytale-themed weddings and princess birthday stages",
    },
    {
        "slug": "fluffy-bloom",
        "name": "Fluffy Bloom",
        "category": "premium",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 2,
        "moq": 10,
        "price_min": 445,
        "price_max": 445,
        "price_display": "From Rs. 445",
        "image_prefix": "product_fluffy_bloom",
        "image_indices": [1, 2],
        "tagline": "Soft, voluminous texture",
        "use_case": "soft pastel backdrops and engagement decor",
    },
    {
        "slug": "premium-fabric-flowers",
        "name": "Premium Fabric Flowers",
        "category": "premium",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 5,
        "moq": 10,
        "price_min": 645,
        "price_max": 645,
        "price_display": "From Rs. 645",
        "image_prefix": "product_premium_fabric",
        "image_indices": [1, 2, 3, 4, 5],
        "tagline": "High-quality structured fabric",
        "use_case": "high-end wedding stages and corporate event walls",
    },
    {
        "slug": "blooming-dales",
        "name": "Blooming Dales",
        "category": "premium",
        "size_inch": 24,
        "size_label": '24" / 32" / 36"',
        "size_meta": "61–91 cm",
        "shade_count": 4,
        "moq": 10,
        "price_min": 509,
        "price_max": 509,
        "price_display": "From Rs. 509",
        "image_prefix": "product_blooming_dales",
        "image_indices": [1, 2, 3, 4],
        "tagline": "Available in 24\", 32\", 36\"",
        "use_case": "mixed-size backdrop arrangements and layered decor",
    },
    {
        "slug": "printed-fabric-flower",
        "name": "Printed Fabric Flower",
        "category": "premium",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 4,
        "moq": 10,
        "price_min": 675,
        "price_max": 675,
        "price_display": "Rs. 675",
        "image_prefix": "product_printed_fabric",
        "image_indices": [1, 2, 3, 4],
        "tagline": "Vibrant printed textures",
        "use_case": "themed events and vibrant photo walls",
    },
    # ── Theme & Events (3) ──────────────────────────────────────────────
    {
        "slug": "organza-butterfly",
        "name": "Organza Butterfly",
        "category": "theme",
        "size_inch": 18,
        "size_label": '18"',
        "size_meta": "46 cm",
        "shade_count": 2,
        "moq": 10,
        "price_min": 450,
        "price_max": 450,
        "price_display": "From Rs. 450",
        "image_prefix": "product_organza_butterfly",
        "image_indices": [1, 2],
        "tagline": "12 pastel shades available",
        "use_case": "butterfly-themed parties, baby showers and kids' events",
    },
    {
        "slug": "dream-wings-90-inch",
        "name": 'Dream Wings (90")',
        "category": "theme",
        "size_inch": 90,
        "size_label": '90"',
        "size_meta": "229 cm",
        "shade_count": 2,
        "moq": 5,
        "price_min": 2300,
        "price_max": 2300,
        "price_display": "Rs. 2,300",
        "image_prefix": "product_dream_wings",
        "image_indices": [1, 3],  # No image with index 2 in repo
        "tagline": "Massive angel wing props",
        "use_case": "angel-wing photo props and statement entrance pieces",
    },
    {
        "slug": "theme-party-fish",
        "name": "Theme Party Fish",
        "category": "theme",
        "size_inch": 24,
        "size_label": '24"',
        "size_meta": "61 cm",
        "shade_count": 4,
        "moq": 10,
        "price_min": 725,
        "price_max": 725,
        "price_display": "From Rs. 725",
        "image_prefix": "product_theme_party_fish",
        "image_indices": [1, 2, 3, 4],
        "tagline": "Under-the-sea party decor",
        "use_case": "under-the-sea birthdays, mermaid parties and aquatic-themed events",
    },
]

CATEGORY_LABELS = {
    "organza": "Organza Flower",
    "premium": "Premium Decor Flower",
    "theme":   "Theme Party Decor",
}

CATEGORY_NAMES = {
    "organza": "Organza Flowers",
    "premium": "Premium & Specialty",
    "theme":   "Theme & Events",
}

CATEGORY_ICONS = {
    "organza": "fa-seedling",
    "premium": "fa-star",
    "theme":   "fa-party-horn",
}


def wa_link(message: str) -> str:
    """Build a wa.me URL with a pre-filled message."""
    return f"https://wa.me/{WHATSAPP_NUMBER}?text=" + urllib.parse.quote(message)


def img_url(prefix: str, idx: int) -> str:
    """Path to a product image, relative to a /products/<slug>.html page."""
    return f"../images/{prefix}_{idx}.webp"


def img_abs_url(prefix: str, idx: int) -> str:
    """Absolute URL for a product image (used in OG tags & JSON-LD)."""
    return f"{SITE_URL}/images/{prefix}_{idx}.webp"


def offer_jsonld(p: dict[str, Any]) -> dict[str, Any]:
    """Schema.org Offer or AggregateOffer based on price range."""
    base = {
        "priceCurrency": "INR",
        "availability": "https://schema.org/InStock",
        "seller": {"@type": "Organization", "name": "The Florista Flowers"},
    }
    if p["price_min"] == p["price_max"]:
        return {"@type": "Offer", "price": p["price_min"], **base}
    return {
        "@type": "AggregateOffer",
        "lowPrice": p["price_min"],
        "highPrice": p["price_max"],
        **base,
    }


def product_jsonld(p: dict[str, Any]) -> dict[str, Any]:
    """Full Product schema for the per-product page."""
    images = [img_abs_url(p["image_prefix"], i) for i in p["image_indices"]]
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "image": images,
        "description": meta_description(p),
        "brand": {"@type": "Brand", "name": "Florista"},
        "manufacturer": {
            "@type": "Organization",
            "name": "The Florista Flowers",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Nagpur",
                "addressRegion": "Maharashtra",
                "addressCountry": "IN",
            },
        },
        "category": "Wholesale Decor Flowers",
        "url": f"{SITE_URL}/products/{p['slug']}.html",
        "sku": p["slug"],
        "offers": offer_jsonld(p),
    }


def breadcrumb_jsonld(p: dict[str, Any]) -> dict[str, Any]:
    """BreadcrumbList for Home > Products > <Product>."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Products",
             "item": f"{SITE_URL}/products.html"},
            {"@type": "ListItem", "position": 3, "name": p["name"],
             "item": f"{SITE_URL}/products/{p['slug']}.html"},
        ],
    }


def meta_description(p: dict[str, Any]) -> str:
    cat = CATEGORY_LABELS[p["category"]].lower()
    return (
        f"Buy {p['name']} wholesale at factory prices from Florista, Nagpur. "
        f"Handcrafted {p['size_label']} {cat} for {p['use_case']}. "
        f"{p['shade_count']} shades available, MOQ {p['moq']} pcs. PAN India delivery."
    )


def page_title(p: dict[str, Any]) -> str:
    return (
        f"{p['name']} – Wholesale {p['size_label']} {CATEGORY_LABELS[p['category']]} "
        f"| Florista Nagpur"
    )


def long_description_html(p: dict[str, Any]) -> str:
    """Two-paragraph descriptive copy.

    Uses the per-product `narrative` from CONTENT_BY_SLUG when authored
    (preferred &mdash; that's the Florista voice talking) and falls back to
    the generic templated paragraphs so a newly-added product still
    renders sensibly before its custom copy lands.
    """
    custom = CONTENT_BY_SLUG.get(p["slug"], {}).get("narrative")
    if custom:
        # Authored copy may already contain HTML entities (`&mdash;`,
        # `&quot;` etc.) — pass through verbatim, just wrap each
        # paragraph in <p>.
        return "".join(f"<p>{para}</p>" for para in custom)

    # Generic fallback (matches the historical generator output).
    name = html.escape(p["name"])
    size = html.escape(p["size_label"])
    meta = html.escape(p["size_meta"])
    use = html.escape(p["use_case"])
    cat_label = html.escape(CATEGORY_LABELS[p["category"]].lower())
    return (
        f"<p>The <strong>{name}</strong> is a handcrafted {cat_label} produced "
        f"in Florista&rsquo;s Nagpur factory. At <strong>{size} ({meta})</strong>, "
        f"it&rsquo;s designed for {use}. Each piece is built on a wire frame "
        f"with high-quality fabric so it holds shape across multiple events "
        f"and ships safely PAN India.</p>"
        f"<p>Wholesale-only supply &mdash; minimum order quantity is "
        f"<strong>{p['moq']} pieces</strong>. Mix and match shades within an "
        f"order, and combine with other Florista sizes for layered backdrop "
        f"installations. Volumetric shipping is calculated at the factory; "
        f"chat with us on WhatsApp for a packed quote to your city.</p>"
    )


def feature_list_html(p: dict[str, Any]) -> str:
    """Render the bullet list inside the info column.

    First bullet is always the Florista brand-identity anchor (same on
    every page). The remaining 3-4 bullets come from the per-product
    `built_for` array so each page reads with its own use-case context
    instead of the same generic list. Falls back to the historical
    generic bullets if a product hasn't been authored yet.
    """
    bullets: list[str] = []

    custom = CONTENT_BY_SLUG.get(p["slug"], {}).get("built_for")
    if custom:
        # Brand-identity anchor first (consistent across all pages).
        bullets.append(
            "Direct-from-factory pricing &mdash; no middlemen, no inflated "
            "retail markup."
        )
        bullets.extend(custom)
    else:
        # Generic fallback (matches the historical generator output).
        bullets = [
            "Direct-from-factory pricing &mdash; no middlemen.",
            f"{p['shade_count']} shades available; custom bulk colours on request.",
            "Volumetric shipping calculated PAN India from Nagpur.",
            "Reusable across multiple events &mdash; durable wire-frame construction.",
        ]

    items = "\n".join(
        f'                        <li><i class="fas fa-check-circle"></i> {b}</li>'
        for b in bullets
    )
    return items


def story_section_html(p: dict[str, Any]) -> str:
    """Render the 3-column 'Behind this piece' section.

    Sits between the article (gallery+info) and the related-products
    grid. Three blocks side by side:
      1. PAIRS WELL WITH  — product-specific layering recommendation
      2. BEHIND THE CRAFT — tactile note about how this piece is made
      3. THE FLORISTA PROMISE — brand-identity, identical across pages

    Returns an empty string for products without authored content so the
    section is omitted entirely (no awkward half-populated grid).
    """
    content = CONTENT_BY_SLUG.get(p["slug"], {})
    pairs_with = content.get("pairs_with")
    craft_note = content.get("craft_note")
    if not (pairs_with and craft_note):
        return ""

    return (
        '\n            <section class="pd-story" aria-label="Behind this piece">\n'
        '                <div class="section-title">\n'
        '                    <div class="section-label">Behind this piece</div>\n'
        f'                    <h2>How buyers use the {html.escape(p["name"])}</h2>\n'
        '                </div>\n'
        '                <div class="pd-story-grid">\n'
        '                    <div class="pd-story-block">\n'
        '                        <h3><i class="fas fa-layer-group" aria-hidden="true"></i> Pairs well with</h3>\n'
        f'                        <p>{pairs_with}</p>\n'
        '                    </div>\n'
        '                    <div class="pd-story-block">\n'
        '                        <h3><i class="fas fa-hammer" aria-hidden="true"></i> Behind the craft</h3>\n'
        f'                        <p>{craft_note}</p>\n'
        '                    </div>\n'
        '                    <div class="pd-story-block pd-story-promise">\n'
        '                        <h3><i class="fas fa-seedling" aria-hidden="true"></i> The Florista promise</h3>\n'
        f'                        <p>{FLORISTA_PROMISE}</p>\n'
        '                    </div>\n'
        '                </div>\n'
        '            </section>'
    )


def hook_section_html(p: dict[str, Any]) -> str:
    """Render the branded contact-hook block.

    A warm, product-specific moment between the story grid and the
    related-products carousel. The headline + paragraph are written
    by hand for each product (in product_content.py); the WhatsApp
    CTA below carries the same enquiry text as the in-info button so
    GA4's `generate_lead` and the lead-capture sheet stay consistent.
    Returns empty for products without an authored hook.
    """
    content = CONTENT_BY_SLUG.get(p["slug"], {})
    headline = content.get("hook_headline")
    hook = content.get("contact_hook")
    if not (headline and hook):
        return ""

    wa = wa_link(f"Enquiry for {p['name']}")
    return (
        '\n            <section class="pd-hook" aria-label="Talk to Florista">\n'
        f'                <h2>{headline}</h2>\n'
        f'                <p>{hook}</p>\n'
        '                <div class="pd-hook-cta">\n'
        f'                    <a href="{wa}" class="btn btn-whatsapp" target="_blank" rel="noopener" data-wa-source="product_{p["slug"]}_hook">\n'
        '                        <i class="fab fa-whatsapp"></i> Start a WhatsApp chat\n'
        '                    </a>\n'
        '                    <a href="../contact.html" class="btn btn-outline">Send a detailed enquiry</a>\n'
        '                </div>\n'
        f'                <p class="pd-hook-meta"><i class="fas fa-circle-check" aria-hidden="true"></i> {HOOK_REASSURANCE}</p>\n'
        '            </section>'
    )


def related_products(current: dict[str, Any]) -> list[dict[str, Any]]:
    """Up to 3 sibling products from the same category."""
    siblings = [p for p in PRODUCTS
                if p["category"] == current["category"] and p["slug"] != current["slug"]]
    # Prefer those closest in size for a more useful "you might also like"
    siblings.sort(key=lambda p: abs(p["size_inch"] - current["size_inch"]))
    return siblings[:3]


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
    <meta property="og:type" content="product">
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

    <!-- Product schema -->
    <script type="application/ld+json">
{product_jsonld}
    </script>

    <!-- Breadcrumb schema -->
    <script type="application/ld+json">
{breadcrumb_jsonld}
    </script>

    <style>
        /* ── Per-product page layout ── */
        .product-detail {{
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
            gap: 48px;
            padding: 24px 0 60px;
            align-items: start;
        }}
        .pd-gallery {{
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 22px;
            padding: 18px;
            box-shadow: var(--glass-shadow);
            position: sticky;
            top: 98px;
        }}
        .pd-main-img-wrap {{
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 16px;
            overflow: hidden;
            background: rgba(245,213,228,0.12);
            cursor: zoom-in;
        }}
        .pd-main-img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 16px;
            transition: transform 0.45s ease;
        }}
        .pd-main-img-wrap:hover .pd-main-img {{ transform: scale(1.04); }}
        .pd-thumbs {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
            gap: 8px;
            margin-top: 16px;
        }}
        .pd-thumbs img {{
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 10px;
            cursor: pointer;
            border: 2px solid transparent;
            opacity: 0.7;
            transition: var(--transition);
        }}
        .pd-thumbs img:hover, .pd-thumbs img.active {{
            border-color: var(--color-primary-dark);
            opacity: 1;
        }}
        .pd-info h1 {{
            font-size: clamp(1.8rem, 3vw, 2.4rem);
            margin-bottom: 8px;
        }}
        .pd-tagline {{
            color: var(--color-gray);
            font-size: 1rem;
            margin-bottom: 20px;
        }}
        .pd-price {{
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--color-primary-dark);
            font-family: var(--font-serif);
            margin: 6px 0 20px;
        }}
        .pd-spec-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-bottom: 26px;
        }}
        .pd-spec {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: var(--glass-shadow);
        }}
        .pd-spec .label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--color-gray);
            margin-bottom: 4px;
        }}
        .pd-spec .value {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--color-dark);
        }}
        .pd-cta {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 24px 0 30px;
        }}
        .pd-description {{
            color: var(--color-gray);
            line-height: 1.75;
            margin-bottom: 28px;
        }}
        .pd-description p {{ margin-bottom: 14px; }}
        .pd-description strong {{ color: var(--color-dark); }}
        .pd-feature-list {{
            list-style: none;
            padding: 0;
            margin: 0 0 28px;
            display: grid;
            gap: 10px;
        }}
        .pd-feature-list li {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            font-size: 0.95rem;
            color: var(--color-dark);
        }}
        .pd-feature-list i {{
            color: #1f6b3a;
            margin-top: 4px;
        }}

        /* Breadcrumb */
        .breadcrumb {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            color: var(--color-gray);
            padding: 18px 0 4px;
        }}
        .breadcrumb a {{ color: var(--color-gray); transition: color 0.2s ease; }}
        .breadcrumb a:hover {{ color: var(--color-primary-dark); }}
        .breadcrumb .sep {{ opacity: 0.5; }}
        .breadcrumb .current {{ color: var(--color-dark); font-weight: 500; }}

        /* Related products */
        .related-section {{
            padding: 40px 0 80px;
            border-top: 1px solid rgba(201,126,160,0.18);
            margin-top: 30px;
        }}
        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-top: 28px;
        }}
        .related-card {{
            background: var(--glass-bg);
            -webkit-backdrop-filter: blur(14px);
            backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
            transition: var(--transition);
            display: flex;
            flex-direction: column;
        }}
        .related-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 50px rgba(80,30,60,0.12);
            border-color: rgba(201,126,160,0.3);
        }}
        .related-card .img-wrap {{
            aspect-ratio: 1 / 1;
            overflow: hidden;
            background: rgba(245,213,228,0.12);
        }}
        .related-card img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 8px;
            transition: transform 0.45s ease;
        }}
        .related-card:hover img {{ transform: scale(1.05); }}
        .related-card .body {{
            padding: 14px 16px 18px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .related-card h3 {{
            font-family: var(--font-sans);
            font-size: 0.98rem;
            font-weight: 600;
            margin: 0;
        }}
        .related-card .price {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--color-primary-dark);
        }}
        .related-card a.cover {{
            display: flex;
            flex-direction: column;
            flex: 1;
            color: inherit;
        }}

        /* Lightbox (same pattern as products.html) */
        .lightbox-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(10,10,20,0.92);
            z-index: 10000;
            align-items: center;
            justify-content: center;
            -webkit-backdrop-filter: blur(6px);
            backdrop-filter: blur(6px);
        }}
        .lightbox-overlay.open {{ display: flex; }}
        .lightbox-img {{
            max-width: 88vw;
            max-height: 88vh;
            object-fit: contain;
            border-radius: 16px;
            box-shadow: 0 32px 80px rgba(0,0,0,0.5);
        }}
        .lightbox-close {{
            position: fixed;
            top: 20px; right: 24px;
            background: rgba(255,255,255,0.12);
            border: none;
            color: white;
            font-size: 1.5rem;
            width: 44px; height: 44px;
            border-radius: 50%;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
        }}
        .lightbox-close:hover {{ background: rgba(255,255,255,0.25); }}

        /* ── Story section: Pairs / Behind the craft / Promise ── */
        .pd-story {{
            padding: 48px 0 16px;
            border-top: 1px solid rgba(201,126,160,0.18);
            margin-top: 30px;
        }}
        .pd-story .section-title {{
            text-align: center;
            margin-bottom: 8px;
        }}
        .pd-story-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 24px;
            margin-top: 28px;
        }}
        .pd-story-block {{
            background: var(--glass-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            padding: 28px 26px;
            box-shadow: var(--glass-shadow);
            transition: var(--transition);
        }}
        .pd-story-block:hover {{
            transform: translateY(-3px);
            box-shadow: 0 20px 50px rgba(80,30,60,0.10);
        }}
        .pd-story-block h3 {{
            font-family: var(--font-sans);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--color-primary-dark);
            margin: 0 0 14px;
            display: flex;
            align-items: center;
            gap: 9px;
        }}
        .pd-story-block h3 i {{ font-size: 0.95rem; }}
        .pd-story-block p {{
            color: var(--color-dark);
            line-height: 1.7;
            font-size: 0.95rem;
            margin: 0;
        }}
        .pd-story-promise {{
            background: linear-gradient(135deg, rgba(201,126,160,0.08), rgba(245,213,228,0.16));
        }}

        /* ── Branded contact hook block ── */
        .pd-hook {{
            background: linear-gradient(135deg, rgba(201,126,160,0.12), rgba(245,213,228,0.20));
            border: 1px solid rgba(201,126,160,0.22);
            border-radius: 22px;
            padding: 48px 36px;
            margin: 40px 0 8px;
            text-align: center;
        }}
        .pd-hook h2 {{
            font-family: var(--font-serif);
            font-size: clamp(1.4rem, 2.4vw, 1.95rem);
            margin: 0 0 14px;
            color: var(--color-dark);
        }}
        .pd-hook > p {{
            color: var(--color-gray);
            font-size: 1rem;
            line-height: 1.65;
            max-width: 640px;
            margin: 0 auto 24px;
        }}
        .pd-hook-cta {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 18px;
        }}
        .pd-hook-meta {{
            font-size: 0.82rem;
            color: var(--color-gray);
            margin: 0;
        }}
        .pd-hook-meta i {{
            color: #1f6b3a;
            margin-right: 6px;
        }}

        @media (max-width: 900px) {{
            .product-detail {{ grid-template-columns: 1fr; gap: 28px; }}
            .pd-gallery {{ position: static; }}
        }}
        @media (max-width: 600px) {{
            .pd-hook {{ padding: 36px 22px; }}
            .pd-story-block {{ padding: 24px 20px; }}
        }}
    </style>
</head>
<body>

    <header class="site-header">
        <div class="container">
            <a href="../index.html" class="logo">Florista<span>.</span></a>
            <nav class="main-nav">
                <a href="../index.html" class="nav-link">Home</a>
                <a href="../products.html" class="nav-link active">Products</a>
                <a href="../wholesale.html" class="nav-link">Wholesale &amp; Logistics</a>
                <a href="../about.html" class="nav-link">About Us</a>
                <a href="../contact.html" class="nav-link">Contact</a>
            </nav>
            <button class="mobile-menu-btn" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
        </div>
    </header>

    <main>
        <div class="container">
            <nav class="breadcrumb" aria-label="Breadcrumb">
                <a href="../index.html">Home</a>
                <span class="sep">/</span>
                <a href="../products.html">Products</a>
                <span class="sep">/</span>
                <a href="../products.html#{category}">{category_name_e}</a>
                <span class="sep">/</span>
                <span class="current" aria-current="page">{name_e}</span>
            </nav>

            <article class="product-detail">

                <!-- Gallery -->
                <div class="pd-gallery">
                    <div class="pd-main-img-wrap">
                        <img class="pd-main-img" id="pd-main-img"
                             src="{main_image}" alt="{name_e} - {size_label_e} wholesale decor flower by Florista Nagpur"
                             loading="eager" fetchpriority="high">
                    </div>
                    <div class="pd-thumbs" role="list">
{thumbs_html}
                    </div>
                </div>

                <!-- Info -->
                <div class="pd-info">
                    <h1>{name_e}</h1>
                    <p class="pd-tagline">{tagline_e}</p>
                    <div class="pd-price">{price_display_e}</div>

                    <div class="pd-spec-grid">
                        <div class="pd-spec">
                            <div class="label">Size</div>
                            <div class="value">{size_label_e}</div>
                        </div>
                        <div class="pd-spec">
                            <div class="label">MOQ</div>
                            <div class="value">{moq} pcs</div>
                        </div>
                        <div class="pd-spec">
                            <div class="label">Shades</div>
                            <div class="value">{shade_count}</div>
                        </div>
                        <div class="pd-spec">
                            <div class="label">Made In</div>
                            <div class="value">Nagpur, India</div>
                        </div>
                    </div>

                    <div class="pd-cta">
                        <a href="{wa_enquire}" class="btn btn-whatsapp" target="_blank" rel="noopener">
                            <i class="fab fa-whatsapp"></i> Enquire on WhatsApp
                        </a>
                        <a href="../wholesale.html" class="btn btn-outline">Wholesale Policy</a>
                    </div>

                    <div class="pd-description">
{long_description}
                    </div>

                    <ul class="pd-feature-list">
{feature_list_html}
                    </ul>
                </div>
            </article>
{story_section_html}{hook_section_html}

            <!-- Related products -->
            <section class="related-section">
                <div class="section-title">
                    <div class="section-label">You might also like</div>
                    <h2>More from {category_name_e}</h2>
                </div>
                <div class="related-grid">
{related_html}
                </div>
                <div style="text-align:center;margin-top:30px;">
                    <a href="../products.html#{category}" class="btn btn-outline">
                        <i class="fas fa-arrow-left"></i> Back to full catalogue
                    </a>
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

    <!-- Lightbox -->
    <div class="lightbox-overlay" id="lightbox">
        <button class="lightbox-close" type="button">
            <i class="fas fa-times"></i>
        </button>
        <img class="lightbox-img" id="lightbox-img" src="" alt="Product zoom">
    </div>

    <a href="https://wa.me/917588447595" class="floating-whatsapp" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
    <button class="back-to-top" aria-label="Back to top"><i class="fas fa-chevron-up"></i></button>

    <script src="../js/main.js"></script>
    <script src="../js/quote-cart.js"></script>
    <script>
        // Per-product page interactions. Bound via addEventListener so
        // that a future strict Content-Security-Policy with a
        // script-src that disallows 'unsafe-inline' can land without
        // breaking the gallery / lightbox.
        (function () {{
            const mainImg = document.getElementById('pd-main-img');
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');
            const closeBtn = lightbox && lightbox.querySelector('.lightbox-close');

            function pdSwitchImg(thumb) {{
                mainImg.src = thumb.dataset.full;
                document.querySelectorAll('.pd-thumbs img').forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
                if (lightbox.classList.contains('open')) {{
                    lightboxImg.src = thumb.dataset.full;
                }}
            }}
            function openLightbox() {{
                lightboxImg.src = mainImg.src;
                lightbox.classList.add('open');
                document.body.style.overflow = 'hidden';
            }}
            function closeLightbox(e) {{
                // Close only when the click is on the overlay backdrop or
                // the close button (matches the previous inline behaviour).
                if (!e || e.target === lightbox || e.target.closest('.lightbox-close')) {{
                    lightbox.classList.remove('open');
                    document.body.style.overflow = '';
                }}
            }}

            // Bindings
            const wrap = document.querySelector('.pd-main-img-wrap');
            if (wrap) wrap.addEventListener('click', openLightbox);
            if (lightbox) lightbox.addEventListener('click', closeLightbox);
            if (closeBtn) closeBtn.addEventListener('click', () => {{
                lightbox.classList.remove('open');
                document.body.style.overflow = '';
            }});
            document.querySelectorAll('.pd-thumbs img').forEach(thumb => {{
                thumb.addEventListener('click', () => pdSwitchImg(thumb));
            }});

            // Esc closes the lightbox even if a thumbnail or button has
            // focus elsewhere on the page.
            document.addEventListener('keydown', e => {{
                if (e.key === 'Escape' && lightbox && lightbox.classList.contains('open')) {{
                    lightbox.classList.remove('open');
                    document.body.style.overflow = '';
                }}
            }});
        }})();
    </script>
</body>
</html>
"""


def render_thumbs(p: dict[str, Any]) -> str:
    """Render the thumbnail grid HTML."""
    name_e = html.escape(p["name"])
    rows = []
    for n, idx in enumerate(p["image_indices"], start=1):
        active = " active" if n == 1 else ""
        url = img_url(p["image_prefix"], idx)
        rows.append(
            f'                        <img src="{url}" data-full="{url}" '
            f'class="{active.strip()}" loading="lazy" '
            f'alt="{name_e} shade {n}">'
        )
    return "\n".join(rows)


def render_related(p: dict[str, Any]) -> str:
    """Render the 'related products' grid HTML."""
    cards = []
    for r in related_products(p):
        url = f"{r['slug']}.html"  # sibling page within /products/
        img = img_url(r["image_prefix"], r["image_indices"][0])
        cards.append(
            f"""                    <div class="related-card">
                        <a class="cover" href="{url}">
                            <div class="img-wrap">
                                <img src="{img}" alt="{html.escape(r['name'])}" loading="lazy">
                            </div>
                            <div class="body">
                                <h3>{html.escape(r['name'])}</h3>
                                <span class="price">{html.escape(r['price_display'])}</span>
                            </div>
                        </a>
                    </div>"""
        )
    return "\n".join(cards)


def render_page(p: dict[str, Any]) -> str:
    """Render the full HTML for one product page."""
    main_image = img_url(p["image_prefix"], p["image_indices"][0])

    return PAGE_TEMPLATE.format(
        title_e=html.escape(page_title(p)),
        description_e=html.escape(meta_description(p)),
        canonical=f"{SITE_URL}/products/{p['slug']}.html",
        og_image=img_abs_url(p["image_prefix"], p["image_indices"][0]),
        product_jsonld=json.dumps(product_jsonld(p), indent=2),
        breadcrumb_jsonld=json.dumps(breadcrumb_jsonld(p), indent=2),
        category=p["category"],
        category_name_e=html.escape(CATEGORY_NAMES[p["category"]]),
        main_image=main_image,
        name_e=html.escape(p["name"]),
        size_label_e=html.escape(p["size_label"]),
        tagline_e=html.escape(p["tagline"]),
        price_display_e=html.escape(p["price_display"]),
        moq=p["moq"],
        shade_count=p["shade_count"],
        wa_enquire=wa_link(f"Enquiry for {p['name']}"),
        long_description=long_description_html(p),
        feature_list_html=feature_list_html(p),
        story_section_html=story_section_html(p),
        hook_section_html=hook_section_html(p),
        thumbs_html=render_thumbs(p),
        related_html=render_related(p),
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    seen_slugs: set[str] = set()
    for p in PRODUCTS:
        if p["slug"] in seen_slugs:
            raise SystemExit(f"Duplicate slug: {p['slug']}")
        seen_slugs.add(p["slug"])

        out_path = OUT_DIR / f"{p['slug']}.html"
        out_path.write_text(render_page(p), encoding="utf-8")
        print(f"  wrote {out_path.relative_to(ROOT)}")

    print(f"\nGenerated {len(PRODUCTS)} product pages in {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
