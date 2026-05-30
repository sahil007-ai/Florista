/**
 * Main JavaScript for Florista Website
 */

// ── Lead-capture endpoint ────────────────────────────────────────
//
// Single shared URL for the B2B contact form (below) and the WhatsApp
// click attribution (bottom of file). Setup steps for the Apps Script
// /exec endpoint live in `.kiro/steering/lead-capture.md`.
//
// NOTE: js/quote-cart.js has its own copy of this URL — paste the same
// URL there too when wiring up Apps Script. (The duplication is
// intentional: each file is small and self-contained, and there are
// only two callsites.)
const FORM_ENDPOINT_URL = ''; // <-- paste your Apps Script /exec URL here

/**
 * Send a fire-and-forget POST to the lead-capture endpoint.
 *
 * Prefers navigator.sendBeacon() because it's specifically designed to
 * survive a page navigation — exactly the situation we hit when the
 * user clicks a wa.me link or submits the contact form. With plain
 * fetch(), if the page navigates before the request completes, the
 * browser cancels it; on mobile Safari this is aggressive and frequent.
 *
 * Falls back to fetch({ keepalive: true }) for browsers without
 * sendBeacon (very rare in 2026, but keepalive on the fetch is the
 * idiomatic backup so the modern browser still treats it as
 * navigation-survivable).
 *
 * Returns true if the request was queued (regardless of whether the
 * server eventually accepted it — we can't read the response in either
 * mode). Returns false if no endpoint is configured.
 */
function postLeadCapture(payload) {
    if (!FORM_ENDPOINT_URL) return false;
    const body = JSON.stringify(payload);
    try {
        if (navigator.sendBeacon) {
            // Apps Script accepts text/plain bodies; Blob preserves the
            // encoding header that sendBeacon would otherwise default to
            // application/x-www-form-urlencoded.
            const blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
            return navigator.sendBeacon(FORM_ENDPOINT_URL, blob);
        }
        // Older browsers: fetch with keepalive=true so the modern
        // versions still prioritize completion across navigation.
        fetch(FORM_ENDPOINT_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body,
            keepalive: true,
        });
        return true;
    } catch (_) {
        return false;
    }
}

document.addEventListener('DOMContentLoaded', () => {

    // ── Mobile Menu Toggle ──────────────────────────────────────
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', () => {
            mainNav.classList.toggle('show');
            const icon = mobileMenuBtn.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });
        // Close on nav link click (mobile)
        mainNav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mainNav.classList.remove('show');
                const icon = mobileMenuBtn.querySelector('i');
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            });
        });
    }

    // ── Active Navigation Link ───────────────────────────────────
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const currentFile = currentPath === '' ? 'index.html' : currentPath;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        // Match exact filename or handle hash links (e.g. products.html#section)
        if (href === currentFile || href.split('#')[0] === currentFile) {
            link.classList.add('active');
        }
    });

    // ── Header Scroll Effect ─────────────────────────────────────
    const header = document.querySelector('.site-header');
    const backToTop = document.querySelector('.back-to-top');

    window.addEventListener('scroll', () => {
        if (header) header.classList.toggle('scrolled', window.scrollY > 50);
        if (backToTop) backToTop.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    if (backToTop) {
        backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }

    // ── Scroll Reveal ────────────────────────────────────────────
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    // ── Lazy Image Loading ────────────────────────────────────────
    if ('loading' in HTMLImageElement.prototype) {
        document.querySelectorAll('img').forEach(img => { img.loading = 'lazy'; });
    }

    // ── FAQ Accordion ─────────────────────────────────────────────
    document.querySelectorAll('.faq-question').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.closest('.faq-item');
            const isOpen = item.classList.contains('open');

            // Close all open items first
            document.querySelectorAll('.faq-item.open').forEach(openItem => {
                openItem.classList.remove('open');
                openItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
            });

            // Open clicked item if it was closed
            if (!isOpen) {
                item.classList.add('open');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // ── Form Submission (WhatsApp Redirect) ──────────────────────
    // ── B2B Enquiry Form ─────────────────────────────────────────
    //
    // Two things happen on submit:
    //   1. Lead is logged to a Google Sheet via Apps Script (background).
    //   2. WhatsApp opens with a pre-filled message (foreground).
    //
    // Lead capture matters because step 2 only opens WhatsApp; the user
    // still has to tap Send inside WhatsApp for the message to actually
    // reach Florista. If they bail, step 1 has already saved the lead.
    //
    // FORM_ENDPOINT_URL is declared at the top of this file — same URL is
    // also referenced by the WhatsApp click attribution at the bottom.
    // Setup steps in .kiro/steering/lead-capture.md.
    const enquiryForm = document.getElementById('b2b-enquiry-form');
    if (enquiryForm) {
        // Helper: flag a field as invalid + show a one-time hint placeholder.
        const flagInvalid = (field, hint) => {
            field.style.borderColor = '#e05c5c';
            field.focus();
            const orig = field.getAttribute('placeholder') || '';
            if (hint) field.setAttribute('placeholder', hint);
            setTimeout(() => {
                field.style.borderColor = '';
                if (hint) field.setAttribute('placeholder', orig);
            }, 3500);
        };

        // Phone-field input normalization.
        // The naive `phone.replace(/\D/g, '')` rejects every Indic digit
        // glyph (Devanagari, Tamil, Bengali, Arabic-Indic) as "non-digit",
        // which silently fails for buyers typing on a Hindi keyboard.
        // Map those Unicode-numeric ranges to ASCII before stripping.
        //
        // Note: a tempting one-liner is `(c.charCodeAt(0) & 0xF) + 48`,
        // but that only works for ranges whose "0" digit is at .._0
        // (Arabic-Indic). Devanagari starts at U+0966, Bengali at
        // U+09E6, etc. — the low 4 bits of "0" aren't zero in most Indic
        // scripts, so the bitmask approach silently corrupts those.
        // Subtract from the known range start instead.
        const DIGIT_RANGE_STARTS = [
            0x0660, // Arabic-Indic           ٠-٩
            0x06F0, // Extended Arabic-Indic  ۰-۹
            0x0966, // Devanagari             ०-९
            0x09E6, // Bengali                ০-৯
            0x0A66, // Gurmukhi               ੦-੯
            0x0AE6, // Gujarati               ૦-૯
            0x0B66, // Oriya                  ୦-୯
            0x0BE6, // Tamil                  ௦-௯
            0x0C66, // Telugu                 ౦-౯
            0x0CE6, // Kannada                ೦-೯
            0x0D66, // Malayalam              ൦-൯
        ];
        function toAsciiDigits(s) {
            return String(s).replace(
                /[\u0660-\u0669\u06F0-\u06F9\u0966-\u096F\u09E6-\u09EF\u0A66-\u0A6F\u0AE6-\u0AEF\u0B66-\u0B6F\u0BE6-\u0BEF\u0C66-\u0C6F\u0CE6-\u0CEF\u0D66-\u0D6F]/g,
                (c) => {
                    const code = c.charCodeAt(0);
                    for (const start of DIGIT_RANGE_STARTS) {
                        if (code >= start && code <= start + 9) {
                            return String.fromCharCode((code - start) + 0x30);
                        }
                    }
                    return c; // unreachable given the regex above
                }
            );
        }

        // Clear red border as soon as user types — feels reactive.
        ['companyName', 'phone', 'city'].forEach((id) => {
            const f = document.getElementById(id);
            if (f) f.addEventListener('input', () => { f.style.borderColor = ''; });
        });

        enquiryForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const companyField  = document.getElementById('companyName');
            const phoneField    = document.getElementById('phone');
            const cityField     = document.getElementById('city');
            const interestField = document.getElementById('interest');

            const company  = companyField.value.trim().slice(0, 120);
            const phone    = phoneField.value.trim().slice(0, 25);
            const city     = cityField.value.trim().slice(0, 80);
            const interest = interestField.value.trim().slice(0, 200);

            // Validate required fields, focus the first invalid one.
            if (!company) {
                flagInvalid(companyField, 'Please enter your name & business');
                return;
            }
            const digits = toAsciiDigits(phone).replace(/\D/g, '');
            // Strip leading country code (91) if user typed +91 or 91 prefix
            const normalizedDigits = digits.length === 12 && digits.startsWith('91') ? digits.slice(2) : digits;
            if (normalizedDigits.length < 10) {
                flagInvalid(phoneField, 'Please enter a valid 10-digit number');
                return;
            }
            if (!city) {
                flagInvalid(cityField, 'Please enter your city');
                return;
            }

            // Build the WhatsApp pre-fill text.
            const message = `Hi Florista! I'm enquiring from ${company} (${city}). My WhatsApp is ${phone}. I'm interested in: ${interest || 'your products'}. Please share bulk pricing details.`;
            const waUrl = `https://wa.me/917588447595?text=${encodeURIComponent(message)}`;

            // (1) GA4 conversion event. `generate_lead` is GA4's recommended
            //     event for B2B lead capture and is one-click promotable to
            //     a Key Event in the GA4 UI. Fire BEFORE window.open below,
            //     because popup-block fallback navigates the active tab and
            //     can kill in-flight beacons. gtag() queues into dataLayer
            //     synchronously, and Consent Mode (default-deny in every
            //     page header, granted on accept in the banner above) drops
            //     the hit for declined users automatically — no extra guard
            //     needed here.
            if (window.gtag) {
                window.gtag('event', 'generate_lead', {
                    method: 'contact_form',
                    form_id: 'b2b-enquiry-form',
                    city: city,
                    interest: interest || '(unspecified)',
                });
            }

            // (2) Fire-and-forget lead capture to Google Sheets via
            //     postLeadCapture() — prefers navigator.sendBeacon() so
            //     the request survives the WhatsApp tab-open below.
            if (FORM_ENDPOINT_URL) {
                postLeadCapture({
                    company,
                    phone,
                    city,
                    // Tag with [contact_form] so this row is easy to
                    // distinguish in the sheet from the anonymous
                    // [<source>] WhatsApp-click rows below.
                    interest: '[contact_form] ' + interest,
                    page: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString(),
                });
            }

            // (3) Open WhatsApp SYNCHRONOUSLY in the same click handler so
            //     popup blockers treat it as a direct user gesture. The old
            //     setTimeout-then-window.open pattern was being blocked.
            const popup = window.open(waUrl, '_blank');
            if (!popup || popup.closed || typeof popup.closed === 'undefined') {
                // Popup was blocked — fall back to navigating the current
                // tab so the enquiry can still go through.
                window.location.href = waUrl;
                return;
            }

            // (4) Show success confirmation message above the form.
            let successMsg = enquiryForm.parentElement.querySelector('.form-success-msg');
            if (!successMsg) {
                successMsg = document.createElement('div');
                successMsg.className = 'form-success-msg';
                successMsg.style.cssText = 'background:#d4edda;color:#155724;border:1px solid #c3e6cb;border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:0.92rem;display:none;';
                enquiryForm.parentElement.insertBefore(successMsg, enquiryForm);
            }
            successMsg.innerHTML = '<i class="fas fa-check-circle" style="margin-right:8px;"></i>Enquiry sent! WhatsApp has been opened — please tap <strong>Send</strong> in WhatsApp to complete.';
            successMsg.style.display = 'block';

            // (5) Button feedback.
            const btn = enquiryForm.querySelector('button[type="submit"]');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fab fa-whatsapp"></i> WhatsApp opened — tap Send to finish';
            btn.style.background = 'linear-gradient(135deg, #25D366, #128C7E)';
            btn.disabled = true;
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
                btn.style.background = '';
                enquiryForm.reset();
                successMsg.style.display = 'none';
            }, 8000);
        });
    }
});



/**
 * ── DPDP Act Cookie / Analytics Consent Banner ──────────────────
 *
 * India's Digital Personal Data Protection Act 2023 (DPDP Act) requires
 * that non-essential tracking (e.g. Google Analytics) only run with
 * explicit user consent. This banner gates the GA tag accordingly.
 *
 * - First visit: shows banner, GA does NOT track until consent.
 * - "Accept": stores `florista-consent=accepted` for 365 days, GA fires.
 * - "Decline": stores `florista-consent=declined`, GA stays disabled.
 * - Returning visitor: banner hidden, prior choice respected.
 */
(function () {
    const STORAGE_KEY = 'florista-consent';
    const stored = localStorage.getItem(STORAGE_KEY);

    // Default: deny analytics until user opts in.
    if (window.gtag) {
        window.gtag('consent', 'default', {
            analytics_storage: 'denied',
            ad_storage: 'denied',
        });
        if (stored === 'accepted') {
            window.gtag('consent', 'update', { analytics_storage: 'granted' });
        }
    }

    // If user already chose, do nothing further.
    if (stored === 'accepted' || stored === 'declined') return;

    // Build the banner once DOM is ready.
    function buildBanner() {
        const banner = document.createElement('div');
        banner.id = 'florista-consent';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-label', 'Cookie consent');
        banner.innerHTML = `
            <div class="fc-inner">
                <div class="fc-text">
                    <strong>We use cookies for analytics.</strong>
                    We use Google Analytics to understand how visitors use our site.
                    Nothing is sold or shared. You can change your choice anytime in your browser.
                    <a href="privacy.html">Read our Privacy Policy</a>.
                </div>
                <div class="fc-actions">
                    <button type="button" class="fc-btn fc-btn-decline">Decline</button>
                    <button type="button" class="fc-btn fc-btn-accept">Accept</button>
                </div>
            </div>
        `;
        document.body.appendChild(banner);

        // Inject styles only if not already present (idempotent).
        if (!document.getElementById('florista-consent-style')) {
            const style = document.createElement('style');
            style.id = 'florista-consent-style';
            style.textContent = `
                #florista-consent {
                    position: fixed;
                    bottom: 0; left: 0; right: 0;
                    background: rgba(24, 32, 46, 0.97);
                    backdrop-filter: blur(14px);
                    color: rgba(255,255,255,0.92);
                    z-index: 99999;
                    box-shadow: 0 -8px 32px rgba(0,0,0,0.18);
                    transform: translateY(100%);
                    animation: fc-slide-up 0.45s cubic-bezier(0.25,0.8,0.25,1) 0.6s forwards;
                }
                @keyframes fc-slide-up { to { transform: translateY(0); } }
                #florista-consent .fc-inner {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 18px 24px;
                    display: flex;
                    align-items: center;
                    gap: 24px;
                    flex-wrap: wrap;
                }
                #florista-consent .fc-text {
                    flex: 1;
                    min-width: 240px;
                    font-size: 0.88rem;
                    line-height: 1.55;
                }
                #florista-consent .fc-text strong { display: block; margin-bottom: 4px; color: #fff; }
                #florista-consent .fc-text a {
                    color: #f5d5e4;
                    text-decoration: underline;
                    text-underline-offset: 2px;
                }
                #florista-consent .fc-actions {
                    display: flex;
                    gap: 10px;
                    flex-shrink: 0;
                }
                #florista-consent .fc-btn {
                    padding: 9px 22px;
                    border-radius: 50px;
                    font-family: inherit;
                    font-size: 0.85rem;
                    font-weight: 600;
                    cursor: pointer;
                    border: none;
                    transition: all 0.25s ease;
                }
                #florista-consent .fc-btn-decline {
                    background: transparent;
                    color: rgba(255,255,255,0.78);
                    border: 1px solid rgba(255,255,255,0.25);
                }
                #florista-consent .fc-btn-decline:hover {
                    background: rgba(255,255,255,0.08);
                    color: #fff;
                }
                #florista-consent .fc-btn-accept {
                    background: #c97ea0;
                    color: white;
                    box-shadow: 0 4px 14px rgba(201,126,160,0.35);
                }
                #florista-consent .fc-btn-accept:hover {
                    background: #b66a8e;
                    transform: translateY(-1px);
                }
                @media (max-width: 600px) {
                    #florista-consent .fc-inner { padding: 14px 16px; gap: 12px; }
                    #florista-consent .fc-actions { width: 100%; }
                    #florista-consent .fc-btn { flex: 1; padding: 10px 14px; }
                }
            `;
            document.head.appendChild(style);
        }

        const closeAndStore = (choice) => {
            localStorage.setItem(STORAGE_KEY, choice);
            if (window.gtag && choice === 'accepted') {
                window.gtag('consent', 'update', { analytics_storage: 'granted' });
            }
            banner.style.transition = 'transform 0.35s ease';
            banner.style.transform = 'translateY(100%)';
            setTimeout(() => banner.remove(), 380);
        };

        banner.querySelector('.fc-btn-accept').addEventListener('click', () => closeAndStore('accepted'));
        banner.querySelector('.fc-btn-decline').addEventListener('click', () => closeAndStore('declined'));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildBanner);
    } else {
        buildBanner();
    }
})();



/**
 * ── WhatsApp click attribution ──────────────────────────────────
 *
 * Every wa.me/... anchor on the page is decorated with utm_source so the
 * lead-capture sheet shows exactly which page/section drove each enquiry.
 *
 * Three layers of attribution (each captures a different dropout point):
 *
 *   1. utm_source / utm_medium / utm_campaign params on the wa.me URL.
 *      wa.me itself ignores them, but the URL becomes self-documenting
 *      in dev tools and GA4's outbound-link click events pick them up.
 *
 *   2. Fire-and-forget beacon to FORM_ENDPOINT_URL on click. Writes a
 *      row to the lead-capture sheet so the owner sees source attribution
 *      even when the user opens WhatsApp but never taps Send. The row
 *      appears with company="(WhatsApp click — anonymous; awaiting reply)"
 *      so it's easy to filter from real form submissions.
 *
 *   3. A short "\n\n— via: <source>" appended to the pre-filled message
 *      text. Survives the wa.me hop into WhatsApp itself, so the source
 *      is also visible inside the chat for any message the customer
 *      actually sends.
 *
 * Source slug taxonomy (auto-derived per anchor)
 *   - data-wa-source="..." attribute on the anchor wins (use for things
 *     the auto-derivation can't infer — e.g. "home_hero").
 *   - .floating-whatsapp           → "<page>_floating"
 *   - inside .footer-social        → "<page>_footer_social"
 *   - inside .product-card           → "<page>_card_<slug>"
 *     (slug is data-id if present, else extracted from the card's title
 *      link "products/<slug>.html", else "size_<data-size>" as fallback)
 *   - inside .uc-final-cta         → "<page>_final_cta"
 *   - inside .uc-hero              → "<page>_hero"
 *   - inside .size-guide           → "<page>_size_guide"
 *   - inside .cat-sidebar / .sidebar-cta → "<page>_sidebar"
 *   - inside .pd-cta (per-product) → "<page>_enquire"
 *   - everything else              → "<page>_unknown"
 *     (rename via data-wa-source as needed; rows in the sheet tagged
 *      "*_unknown" are a TODO list of links worth attributing more
 *      precisely.)
 *
 * <page> is derived from the URL path:
 *   /                                  → "home"
 *   /products.html                     → "products"
 *   /products/60-inch-giant-flora.html → "product_60-inch-giant-flora"
 *   /use-cases/wedding-backdrops.html  → "use_case_wedding-backdrops"
 *
 * Public API (for code that injects WA links dynamically — e.g. quote-cart):
 *   window.FloristaWA.tagAll(rootElement)   // re-tag a subtree
 *   window.FloristaWA.deriveSource(anchor)  // for inspection / overrides
 */
(function () {
    'use strict';

    const UTM_MEDIUM = 'whatsapp';
    const UTM_CAMPAIGN = 'enquiry';

    function pageSlug() {
        // Allow per-page override via <body data-wa-page="...">.
        const explicit = document.body && document.body.dataset && document.body.dataset.waPage;
        if (explicit) return explicit;

        const path = window.location.pathname;
        let m;
        if ((m = path.match(/^\/products\/(.+?)\.html$/)))  return 'product_'  + m[1];
        if ((m = path.match(/^\/use-cases\/(.+?)\.html$/))) return 'use_case_' + m[1];

        m = path.match(/\/([^\/]+?)(?:\.html)?$/);
        const f = (m && m[1]) || '';
        return (f === '' || f === 'index') ? 'home' : f;
    }

    function deriveSource(anchor) {
        const explicit = anchor.getAttribute('data-wa-source');
        if (explicit) return explicit;

        const page = pageSlug();
        if (anchor.classList.contains('floating-whatsapp')) return page + '_floating';
        if (anchor.closest('.footer-social'))               return page + '_footer_social';

        const card = anchor.closest('.product-card');
        if (card) {
            // Best-effort card identifier:
            //   - explicit data-id (set by quote-cart.js or by PR #12 on
            //     home best-sellers and use-case recommended grids)
            //   - else slug extracted from the card's title link to a
            //     /products/<slug>.html page (the catalogue on
            //     products.html doesn't carry data-id at parse time)
            //   - else fall back to data-size as a last resort
            let id = card.dataset.id;
            if (!id) {
                const link = card.querySelector('a.card-title-link, a[href*="products/"]');
                const m = link && link.getAttribute('href').match(/products\/(.+?)\.html/);
                if (m) id = m[1];
            }
            if (!id && card.dataset.size) id = 'size_' + card.dataset.size;
            if (id) return page + '_card_' + id;
        }

        if (anchor.closest('.uc-final-cta'))                return page + '_final_cta';
        if (anchor.closest('.uc-hero'))                     return page + '_hero';
        if (anchor.closest('.size-guide'))                  return page + '_size_guide';
        if (anchor.closest('.cat-sidebar') ||
            anchor.closest('.sidebar-cta'))                 return page + '_sidebar';
        if (anchor.closest('.pd-cta'))                      return page + '_enquire';

        return page + '_unknown';
    }

    function decorateUrl(rawUrl, source) {
        // Idempotent: don't double-tag if utm_source is already present.
        if (rawUrl.indexOf('utm_source=') !== -1) return rawUrl;
        const params =
            'utm_source='    + encodeURIComponent(source) +
            '&utm_medium='   + UTM_MEDIUM +
            '&utm_campaign=' + UTM_CAMPAIGN;
        const sep = rawUrl.indexOf('?') === -1 ? '?' : '&';
        return rawUrl + sep + params;
    }

    function appendMessageMarker(rawUrl, source) {
        // Append "\n\n— via: <source>" to the &text= portion if present.
        // Customer-visible (last line of the WhatsApp message they're
        // about to send) but unobtrusive — feels like a sign-off.
        try {
            const u = new URL(rawUrl);
            const text = u.searchParams.get('text');
            if (!text) return rawUrl;                            // no pre-filled message
            if (text.indexOf('— via:') !== -1) return rawUrl;    // idempotent
            u.searchParams.set('text', text + '\n\n— via: ' + source);
            return u.toString();
        } catch (_) {
            return rawUrl;
        }
    }

    function beaconClick(source, anchor) {
        // typeof check is safe even if FORM_ENDPOINT_URL is somehow not
        // declared (e.g. if someone strips out the constant): we silently
        // no-op instead of throwing inside the click handler.
        if (typeof FORM_ENDPOINT_URL === 'undefined' || !FORM_ENDPOINT_URL) return;

        // Snippet of the pre-filled message for context in the sheet.
        let interestHint = '';
        try {
            const u = new URL(anchor.href);
            interestHint = (u.searchParams.get('text') || '').slice(0, 200);
        } catch (_) { /* unparsable URL — no hint */ }

        // postLeadCapture() prefers navigator.sendBeacon, which is
        // specifically designed to survive the page navigation that
        // happens when the active tab follows a wa.me link (popup
        // blocked path). The previous fetch() implementation was being
        // cancelled mid-flight on mobile Safari before the row hit the
        // sheet.
        postLeadCapture({
            company:   '(WhatsApp click — anonymous; awaiting reply)',
            phone:     '',
            city:      '',
            interest:  '[' + source + '] ' + interestHint,
            page:      window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
        });
    }

    function tagAll(root) {
        const scope = root || document;
        const links = scope.querySelectorAll('a[href*="wa.me/"]');
        links.forEach(function (a) {
            // Process each anchor only once per page lifetime.
            if (a.dataset.waTagged === '1') return;
            a.dataset.waTagged = '1';

            const source = deriveSource(a);
            let url = a.getAttribute('href');
            url = decorateUrl(url, source);
            url = appendMessageMarker(url, source);
            a.setAttribute('href', url);

            a.addEventListener('click', function () {
                // GA4 click signal. Soft event (`select_content`) rather
                // than `generate_lead` — the user has only opened WhatsApp,
                // they haven't sent. The form submit / quote-cart send
                // handlers fire `generate_lead` for the harder signal.
                // `item_id: source` mirrors the utm_source slug, so GA4
                // and the lead-capture sheet stay aligned on attribution.
                if (window.gtag) {
                    window.gtag('event', 'select_content', {
                        content_type: 'whatsapp_cta',
                        item_id: source,
                    });
                }
                beaconClick(source, a);
            });
        });
    }

    // Public API for code that injects WA anchors dynamically.
    window.FloristaWA = {
        tagAll: tagAll,
        deriveSource: deriveSource,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { tagAll(document); });
    } else {
        tagAll(document);
    }
})();
