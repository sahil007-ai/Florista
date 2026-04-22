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
