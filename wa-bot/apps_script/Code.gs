/**
 * Florista WA Bot — Tool Layer (Google Apps Script Web App)
 *
 * Single endpoint exposing every tool the LangGraph agent calls.
 * Bind this script to a Google Sheet named "Florista Sales" (or
 * similar). The bot POSTs JSON {action, ...args} to /exec; this
 * script dispatches by action and returns JSON.
 *
 * ── Required sheet tabs ───────────────────────────────────────
 * Pricing      | slug | tier_min_qty | tier_max_qty | price_per_piece | lead_time_days
 * Leads        | timestamp | phone | name | requirement | items | tier | status
 * Qualified    | phone | buyer_type | timestamp
 * Escalations  | timestamp | phone | reason | context
 *
 * The `Pricing` sheet is the SINGLE SOURCE OF TRUTH for what the
 * bot quotes. The Python agent never sees prices — it asks this
 * script for them on every quote. To change pricing: edit the
 * sheet. No redeploy needed.
 *
 * ── Deployment ────────────────────────────────────────────────
 * 1. In your sheet: Extensions → Apps Script. Paste this file.
 * 2. Save. Click Deploy → New deployment.
 * 3. Type: Web app. Execute as: Me. Who has access: Anyone.
 * 4. Copy the /exec URL into wa-bot/.env as TOOLS_ENDPOINT.
 * 5. After ANY edit to this script: Deploy → Manage deployments →
 *    pencil icon → New version → Deploy. URL stays the same.
 */

const SHEETS = {
  PRICING: 'Pricing',
  LEADS: 'Leads',
  QUALIFIED: 'Qualified',
  ESCALATIONS: 'Escalations',
};

// ── Entry points ────────────────────────────────────────────────

function doPost(e) {
  try {
    const req = JSON.parse(e.postData.contents);
    const action = req.action;
    let result;
    switch (action) {
      case 'lookup_pricing':    result = lookupPricing_(req); break;
      case 'log_lead':          result = logLead_(req); break;
      case 'qualify_buyer':     result = qualifyBuyer_(req); break;
      case 'escalate_to_human': result = escalateToHuman_(req); break;
      default: throw new Error('Unknown action: ' + action);
    }
    return _json({ ok: true, ...result });
  } catch (err) {
    // The Python tool wrapper passes our error string back to the
    // LLM, which can decide to escalate. Don't throw HTTP errors —
    // Apps Script handles those poorly.
    return _json({ ok: false, error: String(err) });
  }
}

function doGet() {
  return _json({
    ok: true,
    msg: 'Florista WA Bot tool layer alive. POST {action, ...args}.',
  });
}

// ── Tools ───────────────────────────────────────────────────────

/**
 * lookup_pricing: find the matching pricing tier for a (slug, qty).
 * Returns the price, lead time, and tier label, OR an error if the
 * quantity falls below MOQ.
 */
function lookupPricing_({ product_slug, quantity }) {
  if (!product_slug || !quantity) {
    throw new Error('product_slug and quantity required');
  }
  const sh = _sheet(SHEETS.PRICING);
  const rows = sh.getDataRange().getValues();
  // Row 0 is the header; data starts at row 1.
  for (let i = 1; i < rows.length; i++) {
    const [slug, minQ, maxQ, price, lead] = rows[i];
    if (slug !== product_slug) continue;
    if (quantity >= Number(minQ) && quantity <= Number(maxQ)) {
      return {
        product_slug,
        quantity,
        price_per_piece: Number(price),
        total: Number(price) * quantity,
        tier_label: minQ + '-' + maxQ + ' pcs',
        lead_time_days: Number(lead),
        moq_met: true,
      };
    }
  }
  // No tier matched. Either below MOQ or product not in sheet.
  return {
    product_slug,
    quantity,
    error: 'No matching tier. Quantity may be below MOQ, or product slug is unknown.',
    moq_met: false,
  };
}

function logLead_({ phone, name, requirement, items, tier }) {
  const sh = _ensureHeader_(SHEETS.LEADS,
    ['Timestamp', 'Phone', 'Name', 'Requirement', 'Items', 'Tier', 'Status']);
  sh.appendRow([new Date(), phone || '', name || '', requirement || '',
                items || '', tier || '', 'new']);
  return { logged: true };
}

function qualifyBuyer_({ phone, buyer_type }) {
  const sh = _ensureHeader_(SHEETS.QUALIFIED,
    ['Phone', 'Buyer Type', 'Timestamp']);
  sh.appendRow([phone || '', buyer_type || '', new Date()]);
  return { recorded: true };
}

function escalateToHuman_({ phone, reason, context }) {
  const sh = _ensureHeader_(SHEETS.ESCALATIONS,
    ['Timestamp', 'Phone', 'Reason', 'Context']);
  sh.appendRow([new Date(), phone || '', reason || '', context || '']);
  // TODO: also send a WhatsApp/email alert to the owner when this
  // fires. Leaving as a sheet write for v1 so deployment is simpler.
  return { escalated: true };
}

// ── Helpers ─────────────────────────────────────────────────────

function _sheet(name) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

function _ensureHeader_(name, header) {
  const sh = _sheet(name);
  if (sh.getLastRow() === 0) {
    sh.appendRow(header);
    sh.setFrozenRows(1);
  }
  return sh;
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
