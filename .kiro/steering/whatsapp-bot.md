# Florista WhatsApp Bot — Setup & Operations Runbook

A LangGraph agent (Python, FastAPI) that handles inbound wholesale
WhatsApp enquiries on Florista's business number. Conversational like
a salesperson, but every price comes from a Google Sheet via tool calls
— the LLM can't invent numbers.

The code lives in `wa-bot/` at the repo root. This doc is the
deploy/operate guide.

## Why prices live in Apps Script, not the prompt

This is the #1 design decision and the easiest one to get wrong.

If you put a price list in the system prompt, the LLM will misquote
~1–3% of conversations: wrong tier picked from messy phrasing, wrong
SKU matched, wrong arithmetic on per-piece × quantity, wrong number
in Hinglish transcription. Each misquote is a real ₹ commitment over
WhatsApp.

The fix is architectural, not prompt-engineering. The LLM owns the
*conversation*, but it does NOT own the *numbers*. To answer any
pricing question, it must call `lookup_pricing(product_slug, quantity)`
which reads the actual `Pricing` sheet. The prompt is fact-free; the
sheet is the single source of truth.

To change pricing: edit the sheet. No redeploy.

## Architecture at a glance

```
WhatsApp customer
       │
       ▼
Meta WhatsApp Cloud API ─── outbound (send_message)
       │
       ▼ inbound webhook
FastAPI POST /webhook
       │
       ▼
LangGraph agent (gpt-4o-mini via OpenRouter)
       │
       │ tool_calls
       ▼
httpx ──► Apps Script /exec  ──►  Google Sheets
                                  - Pricing
                                  - Leads
                                  - Qualified
                                  - Escalations
```

State persistence: `langgraph-checkpoint-sqlite` keyed on `thread_id`
= customer phone. One SQLite file, mounted as a volume in production.

## One-time setup

### 1. Meta WhatsApp Cloud API

1. Go to <https://developers.facebook.com> → Create App → Business.
2. Add the **WhatsApp** product to the app.
3. Under WhatsApp → API Setup, you'll see a test phone number and a
   short-lived token. For production, you must:
   - Add a real phone number (verify via SMS/call).
   - Generate a **System User permanent access token** (24-hour tokens
     will silently break the bot every day). Business Settings → Users
     → System Users → Add → Generate Token (`whatsapp_business_messaging`
     + `whatsapp_business_management` scopes, never expires).
4. Note the **Phone Number ID** (long numeric, NOT the phone itself).
5. Pick any string for `WA_VERIFY_TOKEN` — you'll paste the same value
   in two places (env var + Meta webhook config). It's just a shared
   secret so Meta can prove the webhook URL belongs to you.

### 2. OpenRouter

1. <https://openrouter.ai/keys> → create a key.
2. Top up with credits (₹500 lasts months at gpt-4o-mini volume).
3. Note the key as `OPENROUTER_API_KEY`. Default `MODEL` is
   `openai/gpt-4o-mini`. Swap to `anthropic/claude-sonnet-4` or
   `openai/gpt-4o` later by editing the env var only.

### 3. Apps Script tool layer

1. Create a new Google Sheet titled "Florista Sales" (separate from
   the existing "Florista Leads" sheet — the contact form lead capture
   keeps writing there).
2. Add four tabs with these headers:
   - **Pricing**: `slug | tier_min_qty | tier_max_qty | price_per_piece | lead_time_days`
   - **Leads**: `Timestamp | Phone | Name | Requirement | Items | Tier | Status` (auto-created on first write)
   - **Qualified**: `Phone | Buyer Type | Timestamp` (auto-created)
   - **Escalations**: `Timestamp | Phone | Reason | Context` (auto-created)
3. Populate the **Pricing** sheet. One row per (product, tier). Example:
   ```
   60-inch-giant-flora | 100 | 499  | 450 | 7
   60-inch-giant-flora | 500 | 999  | 380 | 10
   60-inch-giant-flora | 1000| 5000 | 320 | 14
   ```
   Slugs MUST match `wa-bot/data/products.json`. The bot reads the first
   row whose `slug` matches AND `quantity` falls in `[min, max]`.
4. Extensions → Apps Script. Paste `wa-bot/apps_script/Code.gs`.
5. Deploy → New deployment → Web app → Execute as: Me, Who has access:
   Anyone. Authorize. Copy the `/exec` URL → `TOOLS_ENDPOINT`.
6. Smoke test from any terminal:
   ```bash
   curl -L -X POST '<TOOLS_ENDPOINT>' \
     -H 'Content-Type: text/plain;charset=utf-8' \
     -d '{"action":"lookup_pricing","product_slug":"60-inch-giant-flora","quantity":300}'
   ```
   Expected: JSON with `price_per_piece`, `total`, `lead_time_days`.

### 4. Deploy the Python service

Any container host works. Recommendations:

- **Railway** (easiest, ~₹400/mo): `railway init` in `wa-bot/`,
  `railway up`, paste env vars in the dashboard, attach a volume to
  `/app/data`.
- **Fly.io** (cheaper at scale): `fly launch` from `wa-bot/`, set
  secrets with `fly secrets set`, create a volume with `fly volumes
  create`.
- **Self-hosted VPS**: `docker build -t florista-bot wa-bot/`,
  `docker run -d --env-file .env -v $(pwd)/data:/app/data -p 8000:8000
  florista-bot`. Front with Caddy or nginx for HTTPS (Meta requires it).

The healthcheck is `GET /` — returns `{"status":"ok","model":"..."}`.

### 5. Wire Meta → your service

1. Get your public webhook URL: `https://<your-host>/webhook`.
2. Meta → WhatsApp → Configuration → Webhook → Edit.
3. Callback URL: paste the URL above. Verify token: paste your
   `WA_VERIFY_TOKEN`. Click Verify and Save — Meta does the GET
   handshake against your `/webhook` route. If it fails, check that
   your service is actually serving HTTPS publicly.
4. Subscribe to the **messages** field.
5. Send a WhatsApp message to your test number. Within 5 seconds you
   should see the bot reply. If not, check service logs first
   (`railway logs` / `fly logs` / `docker logs`).

## Operations

### Day-1 monitoring

For the first 2 weeks, spot-check the bot daily:

- **Conversations sheet** (TODO: not built yet — add a `conversations`
  sheet write to the Apps Script and have a tool log every turn).
  Until then: Railway/Fly logs include every inbound + the LLM's reply.
- **Escalations sheet**: review every row. If the bot escalates things
  that should have been handled, either tighten the prompt or add a
  new tool. If it fails to escalate things it should, add explicit
  examples to the prompt.
- **Leads sheet**: cross-check vs your sales pipeline. Missing leads =
  prompt isn't telling the bot to log early enough.

### Updating the bot

| Change | Action |
|---|---|
| Pricing | Edit the **Pricing** sheet. No redeploy. |
| Product list (added/renamed page) | Update `wa-bot/data/products.json` AND add Pricing rows. Redeploy Python. |
| Brand voice | Edit `wa-bot/src/florista_bot/prompts.py`. Redeploy Python. |
| New tool | Add `case` to `apps_script/Code.gs`, `@tool` to `tools.py`, append to `TOOLS`. Redeploy both Apps Script (Manage deployments → New version) and Python. |
| Model swap | Change `MODEL` env var, restart service. No code change. |

### Cost ceiling

- gpt-4o-mini at ~10 turns per conversation: ₹0.50–1 per chat.
- 100 chats/day = ₹50–100/day = ~₹2K/month in OpenRouter.
- Container host: ₹0–500/mo depending on choice.
- Total realistic: ₹2–3K/month for ~3000 conversations.

To upgrade quality (better Hinglish, fewer escalations):
`MODEL=anthropic/claude-sonnet-4` → ~10× cost, still trivial.

## Things deliberately NOT in v1

These were in the original n8n workflow (`florista_wa_bot_complete.json`)
and are good ideas, but adding them now would slow down go-live. Each is
a 1–3 hour follow-up:

1. **Catalogue PDF send** — add a `send_catalogue` tool that calls
   Meta's document message endpoint. Needs the PDF on a public URL
   (your `Extended Florista Flowers Catalogue ...` PDF works as-is
   from GitHub Pages).
2. **24h quote follow-up** — a scheduled APScheduler job inside the
   FastAPI process scans the Leads sheet for `Status=new` older than
   24h and pings them. Requires a Meta-approved message template.
3. **Post-event review request** — same shape as #2 but triggered off
   the event date.
4. **Stock broadcast** — webhook that fans out a template to every
   opted-in number in batches.
5. **Inbound from website** — the contact form / quote cart fires a
   webhook into this service so the bot proactively WhatsApps users
   who submitted the form, instead of waiting for them to message
   first. (Was "Option C" in the planning conversation.)

## Troubleshooting

**Meta webhook verification fails (403).**
- Double-check `WA_VERIFY_TOKEN` matches exactly between env and Meta
  UI. No extra whitespace.

**Bot replies but quotes wrong price.**
- Almost certainly a Pricing sheet issue: missing row, slug typo, or
  overlapping tiers. Open Apps Script → Executions to see what the
  `lookup_pricing` call returned.

**Bot doesn't reply at all.**
- Check service logs first. If nothing inbound, Meta isn't reaching
  you — re-verify the webhook URL is publicly HTTPS and the
  `messages` field is subscribed.
- If inbound is logged but no reply, either OpenRouter is down/key is
  bad, or the LLM is stuck in a tool-call loop (rare with gpt-4o-mini;
  raise an issue and we'll add a max-iterations guard).

**Customer says bot "feels robotic".**
- Drop temperature back to 0.5 in `agent.py:_llm()`.
- Add 3–5 real customer-message examples to `prompts.py` showing the
  tone you want.
- Consider upgrading `MODEL` to gpt-4o or claude-sonnet-4.

**Customer complains about a quote.**
- Check the Leads + Qualified sheet rows for that phone, plus the
  Apps Script Executions log for the `lookup_pricing` call. The
  per-call response is logged with timestamp — you can prove what
  the bot said and reconcile.
