/**
 * Florista Quote Cart
 *
 * A localStorage-backed multi-product quote builder. Wholesale buyers
 * usually want several SKUs at once ("50 × 24-inch + 30 × 36-inch +
 * 10 × 60-inch"). The single-product Enquire button is great for one-off
 * questions but forces three back-and-forths for a real bulk order.
 * This cart lets buyers add as many products as they want across the
 * catalogue (and even from the home page best-sellers), tweak quantities
 * with MOQ-aware steppers, and send one consolidated WhatsApp message.
 *
 * Behaviour highlights:
 *   - Cart survives navigation (localStorage), so users can browse home
 *     → products.html → back, and the cart sticks.
 *   - Floating cart button is hidden until at least one item is in cart,
 *     so first-time visitors aren't distracted by it.
 *   - WhatsApp open is synchronous inside the click handler (popup-blocker
 *     friendly, same lesson as the contact form fix).
 *   - Quote sends are also POSTed to the Google Apps Script endpoint if
 *     FORM_ENDPOINT_URL is set, so anonymous interest is captured even if
 *     the user doesn't tap Send in WhatsApp.
 *
 * Hash-based deep linking:
 *   - Each product card gets a stable id like `card-60-giant-flora`,
 *     derived from the <h3> text via slugify().
 *   - Visiting `products.html#card-60-giant-flora` scrolls to that card
 *     and applies a brief spotlight pulse so the buyer's eye lands
 *     immediately. Used by the home page "View Details" buttons.
 *
 * Public API (mostly for debugging in the console):
 *   FloristaCart.add(id) / .remove(id) / .setQty(id, qty) / .clear()
 *   FloristaCart.openDrawer() / .closeDrawer()
 *   FloristaCart.getItems()
 */
(function () {
    'use strict';

    // ─── Config ────────────────────────────────────────────────────
    const STORAGE_KEY = 'florista-quote-cart';
    const WA_NUMBER = '917588447595';

    // Reuse the same Google Apps Script endpoint that the contact form
    // uses (see .kiro/steering/lead-capture.md). Until configured, the
    // cart still works as a WhatsApp redirect — it just won't log
    // anonymous quote-builds to the spreadsheet.
    //
    // Both this constant and the one in main.js need the same URL.
    // Paste it in both places when you wire up Apps Script.
    const FORM_ENDPOINT_URL = '';

    // ─── Slugify ──────────────────────────────────────────────────
    // Same rules used to generate hardcoded anchors on the home page
    // ("60-giant-flora") so JS-derived IDs match the hrefs perfectly.
    function slugify(text) {
        return String(text).toLowerCase()
            .replace(/['"]/g, '')           // strip quote marks first
            .replace(/[^a-z0-9]+/g, '-')    // any other run → single dash
            .replace(/^-+|-+$/g, '');       // trim leading/trailing dashes
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, (c) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
    }

    // ─── State (localStorage) ─────────────────────────────────────
    function loadCart() {
        // The try/catch alone isn't enough: valid JSON like "null", "42",
        // "[1,2,3]" parses cleanly but isn't a plain object. If we hand
        // that back to addToCart() / setQty(), the next property write
        // either crashes (TypeError on null) or silently no-ops (on a
        // primitive). Coerce anything that isn't a plain object to {}.
        try {
            const v = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            return (v && typeof v === 'object' && !Array.isArray(v)) ? v : {};
        } catch (_) {
            return {};
        }
    }

    function saveCart(cart) {
        // iOS Safari private browsing historically had a 0-byte localStorage
        // quota — every setItem() throws QuotaExceededError. Modern Safari
        // 16+ lifted this, but enough older devices still exist among older
        // buyer segments to make the unwrapped call risky. Swallow the
        // failure: the cart UI still updates from the in-memory `cart`
        // object passed in, and the next page load will simply start with
        // an empty cart instead of crashing.
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        } catch (e) {
            console.warn('[FloristaCart] localStorage write failed:', e);
        }
        renderCartButton();
        if (drawer && drawer.classList.contains('open')) renderDrawer();
    }

    // ─── Catalogue index (built from DOM at init) ────────────────
    /** id -> { name, price, moq, image } */
    const catalogue = {};

    function indexProductCards() {
        document.querySelectorAll('.product-card[data-price]').forEach((card) => {
            const h3 = card.querySelector('h3');
            const name = h3 ? h3.textContent.trim() : '(unknown)';
            const slug = card.dataset.id || slugify(name);

            // Persist back to DOM so other features (anchor links, JS
            // queries) can rely on a stable id.
            card.dataset.id = slug;
            if (!card.id) card.id = 'card-' + slug;

            const price = parseInt(card.dataset.price, 10) || 0;
            const moq   = parseInt(card.dataset.moq, 10) || 1;
            const img   = card.querySelector('.main-img') || card.querySelector('img');
            const image = img ? img.src : '';

            catalogue[slug] = { name, price, moq, image };

            injectAddButton(card, slug, name);
            updateCardButtonState(card, slug);
        });
    }

    function injectAddButton(card, slug, name) {
        if (card.querySelector('.quote-add-btn')) return;

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'quote-add-btn';
        btn.dataset.productId = slug;
        btn.setAttribute('aria-label', `Add ${name} to quote`);
        btn.innerHTML =
            '<i class="fas fa-plus" aria-hidden="true"></i>' +
            '<span class="quote-add-tip">Add to quote</span>';

        btn.addEventListener('click', (e) => {
            // Stop the parent card's lightbox / link click from also firing.
            e.stopPropagation();
            e.preventDefault();
            addToCart(slug);
        });

        // Prefer the image wrap so the button lands on top of the photo;
        // fall back to the card itself for layouts (e.g. home best-sellers)
        // that don't use card-img-wrap.
        const wrap = card.querySelector('.card-img-wrap');
        if (wrap) {
            wrap.appendChild(btn);
        } else {
            card.insertBefore(btn, card.firstChild);
        }
    }

    function updateCardButtonState(card, slug) {
        const btn = card.querySelector('.quote-add-btn');
        if (!btn) return;
        const cart = loadCart();
        const inCart = !!cart[slug];
        btn.classList.toggle('is-added', inCart);
        if (inCart) {
            btn.innerHTML =
                '<i class="fas fa-check" aria-hidden="true"></i>' +
                '<span class="quote-add-tip">In quote · click to remove</span>';
        } else {
            btn.innerHTML =
                '<i class="fas fa-plus" aria-hidden="true"></i>' +
                '<span class="quote-add-tip">Add to quote</span>';
        }
    }

    function refreshAllCardStates() {
        document.querySelectorAll('.product-card[data-id]').forEach((card) => {
            updateCardButtonState(card, card.dataset.id);
        });
    }

    // ─── Cart operations ──────────────────────────────────────────
    function addToCart(id) {
        const item = catalogue[id];
        if (!item) {
            console.warn('[FloristaCart] Unknown product:', id);
            return;
        }
        const cart = loadCart();
        if (cart[id]) {
            // Second click on a card that's already in the cart removes it,
            // matching the "In quote · click to remove" tooltip.
            delete cart[id];
        } else {
            cart[id] = {
                id: id,
                name: item.name,
                price: item.price,
                moq: item.moq,
                qty: item.moq, // start at MOQ, buyer adjusts in drawer
            };
        }
        saveCart(cart);
        refreshAllCardStates();
        flashCartButton();
    }

    function removeFromCart(id) {
        const cart = loadCart();
        delete cart[id];
        saveCart(cart);
        refreshAllCardStates();
    }

    function setQty(id, qty) {
        const cart = loadCart();
        if (!cart[id]) return;
        const moq = cart[id].moq || 1;
        // Sanity-cap the upper bound. Without this, `Infinity`, `1e15`,
        // or any pasted-in absurd value sails through Math.floor() (which
        // is itself an identity on Infinity) and lands in the WhatsApp
        // message body and Apps Script lead row. 100,000 pcs is far above
        // any plausible single-SKU bulk order — adjust if business needs
        // it bigger.
        const MAX_QTY = 100000;
        const parsed = Math.floor(qty);
        const safe = Number.isFinite(parsed) ? parsed : moq;
        cart[id].qty = Math.min(MAX_QTY, Math.max(moq, safe || moq));
        saveCart(cart);
    }

    function clearCart() {
        saveCart({});
        refreshAllCardStates();
    }

    // ─── UI: Floating cart button ─────────────────────────────────
    let cartButton;

    function buildCartButton() {
        cartButton = document.createElement('button');
        cartButton.id = 'florista-quote-btn';
        cartButton.type = 'button';
        cartButton.setAttribute('aria-label', 'Open your quote');
        cartButton.innerHTML =
            '<i class="fas fa-clipboard-list" aria-hidden="true"></i>' +
            '<span class="quote-btn-count" aria-hidden="true">0</span>';
        cartButton.addEventListener('click', openDrawer);
        document.body.appendChild(cartButton);
    }

    function renderCartButton() {
        if (!cartButton) return;
        const cart = loadCart();
        const count = Object.keys(cart).length;
        cartButton.querySelector('.quote-btn-count').textContent = count;
        cartButton.classList.toggle('has-items', count > 0);
    }

    function flashCartButton() {
        if (!cartButton) return;
        cartButton.classList.add('is-flashing');
        setTimeout(() => cartButton.classList.remove('is-flashing'), 600);
    }

    // ─── UI: Drawer ───────────────────────────────────────────────
    let drawer, drawerOverlay;

    function buildDrawer() {
        drawerOverlay = document.createElement('div');
        drawerOverlay.id = 'florista-quote-overlay';
        drawerOverlay.addEventListener('click', closeDrawer);

        drawer = document.createElement('aside');
        drawer.id = 'florista-quote-drawer';
        drawer.setAttribute('role', 'dialog');
        drawer.setAttribute('aria-modal', 'true');
        drawer.setAttribute('aria-label', 'Your quote');
        drawer.innerHTML = '' +
            '<header class="quote-drawer-head">' +
                '<h2><i class="fas fa-clipboard-list" aria-hidden="true"></i> Your Quote</h2>' +
                '<button type="button" class="quote-close" aria-label="Close quote">&times;</button>' +
            '</header>' +
            '<div class="quote-drawer-body" id="quote-drawer-body"></div>' +
            '<footer class="quote-drawer-foot" id="quote-drawer-foot"></footer>';

        drawer.querySelector('.quote-close').addEventListener('click', closeDrawer);

        document.body.appendChild(drawerOverlay);
        document.body.appendChild(drawer);

        // ESC closes when open.
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && drawer.classList.contains('open')) closeDrawer();
        });

        // Focus trap. Without this, pressing Tab inside the drawer cycles
        // focus into the page beneath, putting screen-reader and keyboard
        // users in a confusing state where the "modal" is silently
        // backgrounded but visually still on top. Confine Tab to the
        // drawer's own focusable elements while it's open.
        drawer.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab' || !drawer.classList.contains('open')) return;
            const focusable = drawer.querySelectorAll(
                'button:not([disabled]), [href], input:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                last.focus();
                e.preventDefault();
            } else if (!e.shiftKey && document.activeElement === last) {
                first.focus();
                e.preventDefault();
            }
        });
    }

    function renderDrawer() {
        if (!drawer) return;
        const cart = loadCart();
        const items = Object.values(cart);
        const body = drawer.querySelector('#quote-drawer-body');
        const foot = drawer.querySelector('#quote-drawer-foot');

        if (items.length === 0) {
            body.innerHTML =
                '<div class="quote-empty">' +
                    '<i class="fas fa-clipboard-list" aria-hidden="true"></i>' +
                    '<p><strong>Your quote is empty.</strong></p>' +
                    '<p>Browse the catalogue and tap the <i class="fas fa-plus"></i> on any product to start building a multi-item quote.</p>' +
                '</div>';
            foot.innerHTML = '';
            return;
        }

        let estTotal = 0;
        let html = '<ul class="quote-items">';
        items.forEach((item) => {
            // Defensive defaults: if a future schema change leaves old
            // localStorage entries lacking price/qty/moq, render with
            // safe fallbacks instead of crashing the whole drawer with
            // `Cannot read properties of undefined (reading 'toLocaleString')`.
            const moq   = typeof item.moq   === 'number' && item.moq   > 0 ? item.moq   : 1;
            const price = typeof item.price === 'number' ? item.price : 0;
            const qty   = typeof item.qty   === 'number' ? item.qty   : moq;
            const lineTotal = price * qty;
            estTotal += lineTotal;
            html +=
                '<li class="quote-item" data-id="' + escapeHtml(item.id) + '">' +
                    '<div class="quote-item-info">' +
                        '<strong>' + escapeHtml(item.name) + '</strong>' +
                        '<span class="quote-item-meta">Rs. ' + price.toLocaleString('en-IN') + '/pc · MOQ ' + moq + '</span>' +
                    '</div>' +
                    '<div class="quote-qty">' +
                        '<button type="button" class="quote-qty-btn" data-action="decrement" aria-label="Decrease quantity">&minus;</button>' +
                        '<input type="number" class="quote-qty-input" value="' + qty + '" min="' + moq + '" max="100000" step="1" inputmode="numeric" aria-label="Quantity">' +
                        '<button type="button" class="quote-qty-btn" data-action="increment" aria-label="Increase quantity">+</button>' +
                    '</div>' +
                    '<button type="button" class="quote-remove" aria-label="Remove from quote">&times;</button>' +
                '</li>';
        });
        html += '</ul>';
        body.innerHTML = html;

        // Wire up qty steppers + remove buttons.
        body.querySelectorAll('.quote-item').forEach((li) => {
            const id = li.dataset.id;
            const input = li.querySelector('.quote-qty-input');

            li.querySelector('.quote-remove').addEventListener('click', () => {
                removeFromCart(id);
            });

            li.querySelectorAll('.quote-qty-btn').forEach((btn) => {
                btn.addEventListener('click', () => {
                    const cur = parseInt(input.value, 10) || 0;
                    const delta = btn.dataset.action === 'increment' ? 1 : -1;
                    setQty(id, cur + delta);
                });
            });

            // Commit free-form edits when the user blurs / changes the input.
            input.addEventListener('change', () => {
                setQty(id, parseInt(input.value, 10) || 0);
            });
        });

        foot.innerHTML =
            '<div class="quote-total">' +
                '<span>Estimated at base prices</span>' +
                '<strong>Rs. ' + estTotal.toLocaleString('en-IN') + '</strong>' +
            '</div>' +
            '<p class="quote-total-note">Final wholesale pricing &amp; slab discounts will be confirmed by Florista on WhatsApp once we see your full requirement.</p>' +
            '<button type="button" class="btn btn-whatsapp quote-send-btn">' +
                '<i class="fab fa-whatsapp" aria-hidden="true"></i> Send Quote on WhatsApp' +
            '</button>' +
            '<button type="button" class="quote-clear-btn">Clear all</button>';

        foot.querySelector('.quote-send-btn').addEventListener('click', sendQuote);
        foot.querySelector('.quote-clear-btn').addEventListener('click', () => {
            if (confirm('Remove all items from your quote?')) clearCart();
        });
    }

    function openDrawer() {
        if (!drawer) return;
        renderDrawer();
        drawerOverlay.classList.add('open');
        drawer.classList.add('open');
        document.body.style.overflow = 'hidden';
        // Move focus into the drawer so keyboard / screen-reader users
        // land on the modal content instead of an arbitrary spot
        // (typically the cart button they just clicked, which is
        // visually behind the overlay now). Use rAF so it fires after
        // the drawer becomes visible — focusing a display:none element
        // is a silent no-op in some browsers.
        requestAnimationFrame(() => {
            const closeBtn = drawer.querySelector('.quote-close');
            if (closeBtn) closeBtn.focus();
        });
    }

    function closeDrawer() {
        if (!drawer) return;
        drawerOverlay.classList.remove('open');
        drawer.classList.remove('open');
        document.body.style.overflow = '';
        // Return focus to the trigger so keyboard navigation continues
        // from where it left off, instead of jumping to <body>.
        if (cartButton) cartButton.focus();
    }

    // ─── Send quote ──────────────────────────────────────────────
    function sendQuote() {
        const cart = loadCart();
        const items = Object.values(cart);
        if (items.length === 0) return;

        let estTotal = 0;
        const lines = items.map((item) => {
            // Same defensive defaults as renderDrawer(): never trust
            // older localStorage shapes.
            const price = typeof item.price === 'number' ? item.price : 0;
            const qty   = typeof item.qty   === 'number' ? item.qty
                          : (typeof item.moq === 'number' && item.moq > 0 ? item.moq : 1);
            estTotal += price * qty;
            return '• ' + item.name + ' × ' + qty + ' pcs (Rs. ' +
                   price.toLocaleString('en-IN') + '/pc)';
        });

        // Tag this send with the same utm_source taxonomy used by main.js's
        // WhatsApp click attribution, so cart sends and ad-hoc card clicks
        // show up consistently in the lead-capture sheet.
        const SOURCE = 'quote_cart_send';
        const message =
            "Hi Florista! I'd like a quote for the following:\n\n" +
            lines.join('\n') + '\n\n' +
            'Estimated at base prices: Rs. ' + estTotal.toLocaleString('en-IN') + '\n\n' +
            'Please share final wholesale pricing and dispatch timeline. Thanks!\n\n' +
            '— via: ' + SOURCE;

        const waUrl = 'https://wa.me/' + WA_NUMBER +
                      '?text=' + encodeURIComponent(message) +
                      '&utm_source=' + encodeURIComponent(SOURCE) +
                      '&utm_medium=whatsapp&utm_campaign=enquiry';

        // (1) GA4 conversion event. `generate_lead` is GA4's recommended
        //     event for B2B lead capture; one-click promotable to a Key
        //     Event in the GA4 UI. Fire BEFORE window.open below — same
        //     reasoning as the contact form: popup-block fallback can
        //     navigate the active tab and kill in-flight beacons. gtag()
        //     queues into dataLayer synchronously, and Consent Mode (set
        //     up in every page header) drops the hit for declined users.
        //
        //     NOTE: gtag is loaded by the page-level <script> tag, not
        //     this file. If a host page never loaded GA, window.gtag is
        //     undefined and this no-ops cleanly.
        if (window.gtag) {
            window.gtag('event', 'generate_lead', {
                method: 'quote_cart',
                source: SOURCE,            // mirrors utm_source for cross-system attribution
                items_count: items.length,
                value: estTotal,
                currency: 'INR',
            });
        }

        // (2) Fire-and-forget anonymous capture to Google Sheets if configured.
        //     We don't have the buyer's name/phone yet (those come back via
        //     the WhatsApp conversation), so we fill the lead-capture
        //     'company' field with a clear marker. Owner can spot these
        //     anonymous quote rows in the sheet vs. real form submissions.
        if (FORM_ENDPOINT_URL) {
            try {
                const interestStr = items
                    .map((i) => i.name + ' × ' + i.qty + ' pcs')
                    .join(', ') +
                    ' (est. Rs. ' + estTotal.toLocaleString('en-IN') + ')';
                fetch(FORM_ENDPOINT_URL, {
                    method: 'POST',
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                    body: JSON.stringify({
                        company: '(Quote — anonymous; awaiting WhatsApp reply)',
                        phone: '',
                        city: '',
                        interest: '[' + SOURCE + '] ' + interestStr,
                        page: window.location.href,
                        userAgent: navigator.userAgent,
                        timestamp: new Date().toISOString(),
                    }),
                });
            } catch (_) { /* never block the WhatsApp open */ }
        }

        // (3) Synchronous popup so blockers treat it as a direct user gesture.
        const popup = window.open(waUrl, '_blank');
        if (!popup || popup.closed || typeof popup.closed === 'undefined') {
            // Popup blocked → fall back to navigating the current tab.
            window.location.href = waUrl;
            return;
        }

        // (4) Close the drawer but DON'T clear the cart. Buyers often want
        //     to tweak quantities and re-send, or reuse the list for a
        //     follow-up event.
        closeDrawer();
        flashCartButton();
    }

    // ─── Hash-based scroll + spotlight ───────────────────────────
    function handleHash() {
        const hash = window.location.hash || '';
        if (!hash.startsWith('#card-')) return;
        const target = document.getElementById(hash.slice(1));
        if (!target) return;

        // Wait a tick for layout (sticky toolbar + reveal animations
        // can shift positions during paint).
        setTimeout(() => {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            target.classList.add('is-spotlit');
            setTimeout(() => target.classList.remove('is-spotlit'), 2400);
        }, 120);
    }

    // ─── Styles (injected once, scoped via id/class prefixes) ────
    function injectStyles() {
        if (document.getElementById('florista-quote-style')) return;
        const css = '' +
            // The "+" overlay on each product card.
            '.product-card { position: relative; }' +
            '.product-card .card-img-wrap { position: relative; }' +
            '.quote-add-btn {' +
                'position: absolute; top: 12px; right: 12px;' +
                'width: 38px; height: 38px;' +
                'border-radius: 50%; border: none;' +
                'background: rgba(255,255,255,0.92);' +
                '-webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);' +
                'color: var(--color-primary-dark, #b66a8e);' +
                'font-size: 0.95rem;' +
                'cursor: pointer;' +
                'box-shadow: 0 4px 14px rgba(80,30,60,0.18);' +
                'display: flex; align-items: center; justify-content: center;' +
                'transition: all 0.25s ease;' +
                'z-index: 5;' +
                'font-family: inherit;' +
            '}' +
            '.quote-add-btn:hover {' +
                'background: var(--color-primary-dark, #b66a8e);' +
                'color: white;' +
                'transform: scale(1.08);' +
            '}' +
            '.quote-add-btn:focus-visible {' +
                'outline: 2px solid var(--color-primary-dark, #b66a8e);' +
                'outline-offset: 2px;' +
            '}' +
            '.quote-add-btn.is-added { background: #25D366; color: white; }' +
            '.quote-add-btn.is-added:hover { background: #128C7E; }' +
            '.quote-add-tip {' +
                'position: absolute; top: 50%;' +
                'right: calc(100% + 8px);' +
                'transform: translateY(-50%);' +
                'background: rgba(0,0,0,0.85); color: white;' +
                'padding: 4px 10px; border-radius: 6px;' +
                'font-size: 0.72rem; font-weight: 500;' +
                'white-space: nowrap;' +
                'opacity: 0; pointer-events: none;' +
                'transition: opacity 0.2s ease;' +
            '}' +
            '.quote-add-btn:hover .quote-add-tip,' +
            '.quote-add-btn:focus-visible .quote-add-tip { opacity: 1; }' +

            // Floating quote button (bottom-right, above the WhatsApp FAB).
            '#florista-quote-btn {' +
                'position: fixed; right: 20px; bottom: 90px;' +
                'width: 56px; height: 56px;' +
                'border-radius: 50%;' +
                'background: var(--color-primary-dark, #b66a8e);' +
                'color: white; border: none;' +
                'cursor: pointer;' +
                'box-shadow: 0 6px 22px rgba(80,30,60,0.32);' +
                'font-size: 1.3rem;' +
                'z-index: 9998;' +
                'display: none;' +
                'align-items: center; justify-content: center;' +
                'transition: transform 0.25s ease, box-shadow 0.25s ease;' +
                'font-family: inherit;' +
            '}' +
            '#florista-quote-btn.has-items { display: flex; }' +
            '#florista-quote-btn:hover {' +
                'transform: translateY(-3px) scale(1.05);' +
                'box-shadow: 0 10px 28px rgba(80,30,60,0.4);' +
            '}' +
            '#florista-quote-btn.is-flashing { animation: quote-flash 0.6s ease; }' +
            '@keyframes quote-flash {' +
                '0%,100% { transform: scale(1); }' +
                '30%     { transform: scale(1.18); }' +
                '60%     { transform: scale(0.94); }' +
            '}' +
            '.quote-btn-count {' +
                'position: absolute; top: -4px; right: -4px;' +
                'background: white;' +
                'color: var(--color-primary-dark, #b66a8e);' +
                'border-radius: 50px;' +
                'min-width: 22px; height: 22px;' +
                'padding: 0 6px;' +
                'font-size: 0.78rem; font-weight: 700;' +
                'display: flex; align-items: center; justify-content: center;' +
                'box-shadow: 0 2px 6px rgba(0,0,0,0.18);' +
            '}' +

            // Drawer + overlay.
            '#florista-quote-overlay {' +
                'position: fixed; inset: 0;' +
                'background: rgba(10,10,20,0.55);' +
                '-webkit-backdrop-filter: blur(4px); backdrop-filter: blur(4px);' +
                'z-index: 9998;' +
                'opacity: 0; pointer-events: none;' +
                'transition: opacity 0.3s ease;' +
            '}' +
            '#florista-quote-overlay.open { opacity: 1; pointer-events: auto; }' +
            '#florista-quote-drawer {' +
                'position: fixed; top: 0; right: 0; bottom: 0;' +
                'width: min(100%, 440px);' +
                'background: #fdfaf8;' +
                'z-index: 9999;' +
                'box-shadow: -16px 0 48px rgba(0,0,0,0.2);' +
                'transform: translateX(100%);' +
                'transition: transform 0.34s cubic-bezier(0.25,0.8,0.25,1);' +
                'display: flex; flex-direction: column;' +
                'font-family: var(--font-sans, "Inter", sans-serif);' +
            '}' +
            '#florista-quote-drawer.open { transform: translateX(0); }' +
            '.quote-drawer-head {' +
                'padding: 22px 24px;' +
                'border-bottom: 1px solid rgba(0,0,0,0.06);' +
                'display: flex; align-items: center; justify-content: space-between;' +
            '}' +
            '.quote-drawer-head h2 {' +
                'font-size: 1.25rem; margin: 0;' +
                'color: var(--color-dark, #2d1b25);' +
                'display: flex; align-items: center; gap: 10px;' +
                'font-family: var(--font-sans, "Inter", sans-serif);' +
            '}' +
            '.quote-drawer-head h2 i {' +
                'color: var(--color-primary-dark, #b66a8e);' +
                'font-size: 1rem;' +
            '}' +
            '.quote-close {' +
                'background: none; border: none;' +
                'font-size: 1.6rem; line-height: 1;' +
                'cursor: pointer;' +
                'color: var(--color-gray, #6b6770);' +
                'padding: 4px 12px;' +
                'border-radius: 8px;' +
                'transition: background 0.2s, color 0.2s;' +
                'font-family: inherit;' +
            '}' +
            '.quote-close:hover {' +
                'background: rgba(0,0,0,0.05);' +
                'color: var(--color-dark, #2d1b25);' +
            '}' +
            '.quote-drawer-body {' +
                'flex: 1; overflow-y: auto;' +
                'padding: 8px 0;' +
            '}' +
            '.quote-empty {' +
                'text-align: center;' +
                'padding: 60px 28px;' +
                'color: var(--color-gray, #6b6770);' +
            '}' +
            '.quote-empty i {' +
                'font-size: 2.4rem;' +
                'color: var(--color-primary-light, #f5d5e4);' +
                'margin-bottom: 14px;' +
                'display: block;' +
            '}' +
            '.quote-empty p { margin: 0 0 8px; line-height: 1.55; }' +
            '.quote-empty p strong { color: var(--color-dark, #2d1b25); }' +
            '.quote-items { list-style: none; padding: 0; margin: 0; }' +
            '.quote-item {' +
                'display: grid;' +
                'grid-template-columns: 1fr auto auto;' +
                'gap: 12px;' +
                'align-items: center;' +
                'padding: 14px 24px;' +
                'border-bottom: 1px solid rgba(0,0,0,0.05);' +
            '}' +
            '.quote-item-info { min-width: 0; }' +
            '.quote-item-info strong {' +
                'display: block;' +
                'font-size: 0.92rem;' +
                'color: var(--color-dark, #2d1b25);' +
                'margin-bottom: 4px;' +
                'font-weight: 600;' +
                'line-height: 1.3;' +
            '}' +
            '.quote-item-meta {' +
                'font-size: 0.78rem;' +
                'color: var(--color-gray, #6b6770);' +
            '}' +
            '.quote-qty {' +
                'display: flex; align-items: center; gap: 0;' +
                'background: rgba(245,213,228,0.3);' +
                'border-radius: 30px; padding: 2px;' +
            '}' +
            '.quote-qty-btn {' +
                'width: 26px; height: 26px;' +
                'border: none; background: white;' +
                'border-radius: 50%; cursor: pointer;' +
                'font-size: 0.95rem; font-weight: 600;' +
                'color: var(--color-primary-dark, #b66a8e);' +
                'line-height: 1;' +
                'font-family: inherit;' +
                'transition: background 0.2s;' +
            '}' +
            '.quote-qty-btn:hover {' +
                'background: var(--color-primary-light, #f5d5e4);' +
            '}' +
            '.quote-qty-input {' +
                'width: 44px; border: none;' +
                'background: transparent;' +
                'text-align: center;' +
                'font-size: 0.9rem; font-weight: 600;' +
                'color: var(--color-dark, #2d1b25);' +
                'font-family: inherit;' +
                '-moz-appearance: textfield;' +
            '}' +
            '.quote-qty-input::-webkit-outer-spin-button,' +
            '.quote-qty-input::-webkit-inner-spin-button {' +
                '-webkit-appearance: none; margin: 0;' +
            '}' +
            '.quote-remove {' +
                'background: none; border: none;' +
                'color: var(--color-gray, #6b6770);' +
                'font-size: 1.4rem;' +
                'cursor: pointer;' +
                'padding: 4px 6px;' +
                'border-radius: 6px;' +
                'line-height: 1;' +
                'transition: background 0.2s, color 0.2s;' +
                'font-family: inherit;' +
            '}' +
            '.quote-remove:hover { background: #ffe5e5; color: #d04545; }' +
            '.quote-drawer-foot {' +
                'padding: 18px 24px 24px;' +
                'border-top: 1px solid rgba(0,0,0,0.08);' +
                'background: white;' +
            '}' +
            '.quote-total {' +
                'display: flex; align-items: baseline; justify-content: space-between;' +
                'margin-bottom: 6px;' +
                'font-size: 0.95rem;' +
                'color: var(--color-dark, #2d1b25);' +
            '}' +
            '.quote-total strong {' +
                'font-size: 1.4rem;' +
                'font-family: var(--font-serif, "Playfair Display", serif);' +
                'color: var(--color-primary-dark, #b66a8e);' +
            '}' +
            '.quote-total-note {' +
                'font-size: 0.74rem;' +
                'color: var(--color-gray, #6b6770);' +
                'line-height: 1.5;' +
                'margin: 0 0 14px;' +
            '}' +
            '.quote-send-btn {' +
                'width: 100%;' +
                'margin-bottom: 8px;' +
                'font-size: 0.92rem;' +
            '}' +
            '.quote-clear-btn {' +
                'width: 100%;' +
                'background: none;' +
                'border: 1px solid rgba(0,0,0,0.12);' +
                'color: var(--color-gray, #6b6770);' +
                'font-size: 0.82rem;' +
                'padding: 8px;' +
                'border-radius: 50px;' +
                'cursor: pointer;' +
                'transition: background 0.2s, color 0.2s;' +
                'font-family: inherit;' +
            '}' +
            '.quote-clear-btn:hover {' +
                'background: rgba(0,0,0,0.04);' +
                'color: var(--color-dark, #2d1b25);' +
            '}' +

            // Hash-arrival spotlight pulse on the targeted card.
            '.product-card.is-spotlit { animation: quote-spotlight 2.4s ease-out; }' +
            '@keyframes quote-spotlight {' +
                '0%   { box-shadow: 0 0 0 0 rgba(201,126,160,0.7); }' +
                '40%  { box-shadow: 0 0 0 16px rgba(201,126,160,0); }' +
                '100% { box-shadow: 0 0 0 0 rgba(201,126,160,0); }' +
            '}' +

            '@media (max-width: 600px) {' +
                '#florista-quote-btn { width: 50px; height: 50px; bottom: 80px; right: 16px; font-size: 1.15rem; }' +
                '.quote-add-btn { width: 34px; height: 34px; top: 10px; right: 10px; font-size: 0.85rem; }' +
                '.quote-add-tip { display: none; }' + // tooltip pointless on mobile
                '.quote-item { padding: 12px 16px; gap: 8px; }' +
                '.quote-drawer-head { padding: 18px; }' +
                '.quote-drawer-foot { padding: 16px 18px 20px; }' +
            '}';

        const style = document.createElement('style');
        style.id = 'florista-quote-style';
        style.textContent = css;
        document.head.appendChild(style);
    }

    // ─── Public API ──────────────────────────────────────────────
    window.FloristaCart = {
        add: addToCart,
        remove: removeFromCart,
        setQty: setQty,
        clear: clearCart,
        openDrawer: openDrawer,
        closeDrawer: closeDrawer,
        getItems: function () { return Object.values(loadCart()); },
    };

    // ─── Init ────────────────────────────────────────────────────
    function init() {
        injectStyles();
        indexProductCards();
        buildCartButton();
        buildDrawer();
        renderCartButton();
        handleHash();

        // If the user clicks an in-page anchor (e.g. another card link)
        // re-run the spotlight logic.
        window.addEventListener('hashchange', handleHash);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
