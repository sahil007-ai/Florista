/**
 * Main JavaScript for Florista Website
 */

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
    // Setup steps for FORM_ENDPOINT_URL are in .kiro/steering/lead-capture.md.
    // Until configured (left as ''), the form still opens WhatsApp normally —
    // it just won't log to a spreadsheet.
    const FORM_ENDPOINT_URL = ''; // <-- paste your Apps Script /exec URL here

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

            const company  = companyField.value.trim();
            const phone    = phoneField.value.trim();
            const city     = cityField.value.trim();
            const interest = interestField.value.trim();

            // Validate required fields, focus the first invalid one.
            if (!company) {
                flagInvalid(companyField, 'Please enter your name & business');
                return;
            }
            const digits = phone.replace(/\D/g, '');
            if (digits.length < 10) {
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

            // (1) Fire-and-forget lead capture to Google Sheets.
            //     `mode: 'no-cors'` lets the request go through without a
            //     CORS preflight (Apps Script doesn't return CORS headers
            //     by default). We can't read the response, but Apps Script
            //     still receives and logs it.
            if (FORM_ENDPOINT_URL) {
                try {
                    fetch(FORM_ENDPOINT_URL, {
                        method: 'POST',
                        mode: 'no-cors',
                        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                        body: JSON.stringify({
                            company,
                            phone,
                            city,
                            interest,
                            page: window.location.href,
                            userAgent: navigator.userAgent,
                            timestamp: new Date().toISOString(),
                        }),
                    });
                } catch (_) { /* never block WhatsApp open */ }
            }

            // (2) Open WhatsApp SYNCHRONOUSLY in the same click handler so
            //     popup blockers treat it as a direct user gesture. The old
            //     setTimeout-then-window.open pattern was being blocked.
            const popup = window.open(waUrl, '_blank');
            if (!popup || popup.closed || typeof popup.closed === 'undefined') {
                // Popup was blocked — fall back to navigating the current
                // tab so the enquiry can still go through.
                window.location.href = waUrl;
                return;
            }

            // (3) Honest button feedback. The message is NOT yet sent —
            //     the user must tap Send inside WhatsApp.
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
            }, 5000);
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
