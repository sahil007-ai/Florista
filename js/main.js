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
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) link.classList.add('active');
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

    // ── Form Submission (WhatsApp Redirect) ──────────────────────
    const enquiryForm = document.getElementById('b2b-enquiry-form');
    if (enquiryForm) {
        enquiryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const company  = document.getElementById('companyName').value;
            const phone    = document.getElementById('phone').value;
            const city     = document.getElementById('city').value;
            const interest = document.getElementById('interest').value;
            const message  = `Hi Florista! I'm enquiring from ${company} (${city}). My WhatsApp is ${phone}. I'm interested in: ${interest}. Please share bulk pricing details.`;
            window.open(`https://wa.me/917588447595?text=${encodeURIComponent(message)}`, '_blank');
        });
    }
});
