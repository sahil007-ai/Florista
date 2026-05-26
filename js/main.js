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
    const enquiryForm = document.getElementById('b2b-enquiry-form');
    if (enquiryForm) {
        enquiryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const company  = document.getElementById('companyName').value.trim();
            const phone    = document.getElementById('phone').value.trim();
            const city     = document.getElementById('city').value.trim();
            const interest = document.getElementById('interest').value.trim();

            // Basic phone validation — must have at least 10 digits
            const digits = phone.replace(/\D/g, '');
            if (digits.length < 10) {
                const phoneField = document.getElementById('phone');
                phoneField.style.borderColor = '#e05c5c';
                phoneField.focus();
                phoneField.setAttribute('placeholder', 'Please enter a valid number');
                setTimeout(() => {
                    phoneField.style.borderColor = '';
                    phoneField.setAttribute('placeholder', '+91 XXXXX XXXXX');
                }, 3000);
                return;
            }

            const message = `Hi Florista! I'm enquiring from ${company} (${city}). My WhatsApp is ${phone}. I'm interested in: ${interest || 'your products'}. Please share bulk pricing details.`;
            const waUrl = `https://wa.me/917588447595?text=${encodeURIComponent(message)}`;

            // Visual feedback on the button
            const btn = enquiryForm.querySelector('button[type="submit"]');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fab fa-whatsapp"></i> Opening WhatsApp...';
            btn.disabled = true;
            btn.style.opacity = '0.75';

            setTimeout(() => {
                window.open(waUrl, '_blank');
                btn.innerHTML = '<i class="fas fa-check"></i> Message Sent!';
                btn.style.background = 'linear-gradient(135deg, #25D366, #128C7E)';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                    btn.style.opacity = '';
                    btn.style.background = '';
                    enquiryForm.reset();
                }, 3000);
            }, 400);
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
