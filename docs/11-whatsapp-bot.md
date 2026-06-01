# 11 — The WhatsApp Bot

The site captures leads. The **WhatsApp bot** answers them — automatically,
24/7, like a junior salesperson who never sleeps and never invents prices.

This chapter is for the day-to-day of running it: changing a price,
swapping in a new product, tweaking the bot's tone, knowing when something
has gone wrong, and knowing when to call a developer.

> **First time setting up the bot from scratch?** Skip ahead to the
> [setup section](#one-time-setup-the-30000-foot-overview) which links
> to `.kiro/steering/whatsapp-bot.md` — the full deployment runbook with
> click-by-click instructions for Meta, OpenRouter, and Google Sheets.
> The chapter you're reading now assumes the bot is already running and
> you want to **change** something.

---

## What the WhatsApp bot does

A wholesale buyer sends a WhatsApp message to Florista's number. The bot:

1. **Greets them and figures out who they are** — decorator/wholesaler vs
   personal-use buyer. Personal-use buyers get politely declined (we're
   wholesale-only). Decorators continue.
2. **Asks what they need** — product, quantity, delivery city, event date.
3. **Looks up the price** in the Google Sheet — never makes one up.
4. **Quotes them with the correct lead time** for that quantity.
5. **Logs the lead** to the Sales sheet so the team can follow up.
6. **Hands off to a human** when something needs judgment — custom orders,
   AI/Pinterest references, payment-term negotiations, complaints.

The conversation feels natural — not like clicking through buttons. The
bot mirrors the customer's language (English, Hindi, or Hinglish).

---

## Why the bot is in its own folder

The website (`/index.html`, `/products/`, etc.) is **static HTML**. It
runs in the buyer's browser. There's no server.

The bot is a **Python program**. It needs to be running somewhere all
the time so it can reply to WhatsApp messages. That somewhere is a host
like Railway or Fly.io — not the same place the website is hosted.

That's why the bot lives in `wa-bot/` at the repo root. Same Git repo,
two different things:

```
Florista/                       theflorista.in
├── index.html, products.html   ← static HTML, hosted on Vercel/GitHub Pages
├── css/, js/, images/          ← runs in the buyer's browser
│
└── wa-bot/                     bot.theflorista.in (or similar)
    └── (Python service)        ← runs 24/7 on Railway/Fly.io
                                 ← talks to Meta WhatsApp + OpenAI + Google Sheets
```

If you're editing the *website*, you don't need to touch `wa-bot/`. If
you're editing the *bot*, you don't need to touch the website. They're
independent.

---

## The 30-second mental model

```
   ┌─────────────────────┐
   │  Customer's WhatsApp│
   └──────────┬──────────┘
              │ "I need 300 of the 60 inch Giant Flora for an Indore
              │  wedding on the 25th"
              ▼
   ┌─────────────────────┐
   │  Meta (WhatsApp     │
   │  Business Cloud API)│
   └──────────┬──────────┘
              │ webhook
              ▼
   ┌─────────────────────┐         ┌──────────────────────┐
   │  wa-bot/            │  asks   │  ChatGPT-4o-mini     │
   │  (Python on Railway)├────────▶│  via OpenRouter      │
   │                     │◀────────┤                      │
   └──────────┬──────────┘ replies └──────────────────────┘
              │ "what's the price for 300 pieces?"
              ▼
   ┌─────────────────────┐         ┌──────────────────────┐
   │  Google Apps Script │  reads  │  Florista Sales      │
   │  /exec endpoint     ├────────▶│  Google Sheet        │
   │                     │◀────────┤  (Pricing tab)       │
   └─────────────────────┘ ₹450/pc └──────────────────────┘
```

Three jobs, three different tools:

| Job | Tool | Why this tool |
|-----|------|---------------|
| Talk to WhatsApp | Meta Business Cloud API | Only official way to send/receive on a business number |
| Talk like a salesperson | ChatGPT-4o-mini via OpenRouter | The "brain". Cheap, reliable, swappable |
| Store prices, log leads | Google Apps Script + Sheets | You can edit the sheet without touching code |

---

## The two unbreakable rules

If you remember nothing else from this chapter, remember these.

### Rule 1: Prices live in the Sheet, never in code

The bot is **forbidden** from quoting a price from memory. Every time it
needs to quote, it looks up the price in the **Pricing** tab of the
Florista Sales Google Sheet via a "tool call".

This is the single most important safety property of the bot. If prices
ever leak into the bot's prompt (the text that tells it how to behave),
the AI will misquote ~1–3% of conversations — wrong tier, wrong product,
wrong arithmetic. At Florista's order sizes, one misquote = ₹50K–₹2L
mistake.

**To change a price:** edit the Sheet. That's it. No deploy, no code
change, no developer.

### Rule 2: Voice and rules live in the prompt

What the bot says, how warm it sounds, what topics it must escalate —
all of that lives in `wa-bot/src/florista_bot/prompts.py`.

**To change the bot's tone or behavior:** edit `prompts.py` and redeploy.
This is more work than a Sheet edit, but still one file.

These two rules cover ~95% of the changes you'll ever want to make. The
rest is Recipes below.

---

## One-time setup (the 30,000-foot overview)

If the bot has never been deployed, you'll need to do this once. Plan
on **2–3 hours** the first time.

| Step | What you do | Where |
|------|-------------|-------|
| 1 | Get a permanent Meta WhatsApp Business token + Phone Number ID | <https://developers.facebook.com> |
| 2 | Create an OpenRouter API key, add ₹500 credit | <https://openrouter.ai/keys> |
| 3 | Create a "Florista Sales" Google Sheet, paste `wa-bot/apps_script/Code.gs`, deploy as Web App | sheets.google.com |
| 4 | Fill in the **Pricing** tab with real prices (one row per product, per quantity tier) | The Sheet |
| 5 | Sign up for Railway, deploy `wa-bot/` from the repo, paste env vars, attach a 1 GB volume to `/app/data` | <https://railway.app> |
| 6 | Paste the public Railway URL + verify token into Meta's webhook config | Meta dashboard |
| 7 | Send a WhatsApp test message to your number — you should get a reply within 5 seconds | Your phone |

**Click-by-click instructions for every step** are in
[`.kiro/steering/whatsapp-bot.md`](../.kiro/steering/whatsapp-bot.md).
Don't try to do this from this chapter — go to the steering file. It has
all the screenshots-worth-of-detail you need.

---

## Daily operations — recipes

### Recipe 1 — Change a price

**Time:** 30 seconds. **No deploy. No developer.**

1. Open your "Florista Sales" Google Sheet.
2. Go to the **Pricing** tab.
3. Find the row for the product + quantity tier you want to change.
4. Edit the `price_per_piece` cell. Save (auto-saves).
5. Done. The next quote the bot generates uses the new price immediately.

> **Why this works:** the bot looks up prices fresh on every quote. It
> has no cache, no memory of past prices. The Sheet is the source of
> truth, full stop.

### Recipe 2 — Change a lead time

Same as Recipe 1, but edit the `lead_time_days` cell instead. The bot
will tell the next customer the new lead time. No deploy.

### Recipe 3 — Add a new pricing tier (e.g. 5000+ pieces)

1. Open the Pricing sheet.
2. Add a new row for the same product slug. Example:
   ```
   60-inch-giant-flora | 5000 | 50000 | 290 | 21
   ```
   (slug, min qty for this tier, max qty, price per piece, lead time days)
3. Save. Done.

The bot will pick the right tier automatically based on the quantity the
customer asks for.

> **Watch out:** the tier ranges must not overlap. If you have rows for
> `100–499`, `500–999`, `1000+` and you add `5000+`, change the previous
> tier's max from "infinity" (or 50000) to 4999. Otherwise the bot might
> pick the wrong one.

### Recipe 4 — Add a brand-new product to the bot

This one needs **two edits + a redeploy**, because the bot needs to know
the new product's slug exists.

1. Add the product to the **website** first — see
   [Chapter 03](./03-managing-products.md). You'll create a new entry in
   `tools/generate_product_pages.py` with a `slug` like
   `120-inch-mega-flora`.
2. Add a row to the bot's product catalog file:
   `wa-bot/data/products.json`. Match the slug exactly:
   ```json
   {"slug": "120-inch-mega-flora", "name": "120-inch Mega Flora",
    "size_inches": 120, "category": "giant"}
   ```
3. Add Pricing rows in the Sheet for the new slug, one per quantity tier.
4. Commit + push. The Python service redeploys automatically (Railway
   watches the repo).

> **Why two files?** The Sheet is the price source. `products.json` is
> what the bot uses to *recognize* the product when a customer says "the
> 120 inch ones". The bot needs to know the product exists before it
> can ask the Sheet for its price.

### Recipe 5 — Rename a product

1. Edit `wa-bot/data/products.json` → change the `name` (and `slug` if
   needed).
2. If you changed the slug, update every row in the Pricing sheet to use
   the new slug.
3. Commit + push.

### Recipe 6 — Change the bot's tone

For example: "be more formal," "stop using emojis," "always end with a
namaskar."

1. Open `wa-bot/src/florista_bot/prompts.py`.
2. Find the `SYSTEM_PROMPT` block — it's all plain English.
3. Add or change a sentence. Examples:
   - To make it more formal: change *"Warm, professional, India B2B"* to
     *"Formal, courteous, India B2B"*.
   - To remove emojis: change *"Never use more than one emoji per message"*
     to *"Never use emojis"*.
   - To change greetings: add a line *"Always begin first replies with
     'Namaste 🙏'"*.
4. Commit + push. Next conversation uses the new tone.

> **Test the change.** Send yourself a WhatsApp message after the deploy
> finishes (~2 minutes on Railway). Check that the new tone shows up. If
> not, the prompt edit might be ambiguous — make it more specific.

### Recipe 7 — Add a thing the bot must always say or never say

Open `prompts.py`, find the `# Hard rules — never break these` section,
add a new bullet. Examples:

- `- Never quote a delivery date faster than 7 days for orders above 1000 pieces.`
- `- Always mention that custom colors take 7–14 extra days.`
- `- Never use the word "cheap" — say "competitive" or "affordable".`

Commit + push. The next conversation honors the new rule.

> **Hard rules are stronger than soft suggestions.** If you find the bot
> ignoring a guideline you wrote in casual language, move it into the
> "Hard rules" block. The wording "Never X" is treated almost like an
> if-statement by modern AI.

### Recipe 8 — Upgrade the AI brain (better quality, more cost)

The default model is `openai/gpt-4o-mini` — cheap and good enough for
routine quoting. If you find the bot fumbling Hinglish or missing nuance,
upgrade.

1. Open Railway → your project → **Variables** tab.
2. Find the `MODEL` variable.
3. Change the value:
   - `openai/gpt-4o` — ~10× cost, much better Hinglish
   - `anthropic/claude-sonnet-4` — best for Indian B2B, ~12× cost
   - `anthropic/claude-haiku-4` — middle ground, ~3× cost
4. Save. Railway redeploys automatically (~30 seconds).

No code change needed. To go back to mini, just set the variable back.

### Recipe 9 — Switch the bot off temporarily

You're going on vacation. Or there's a price update in progress and you
don't want the bot quoting old numbers.

**Easiest way:**
1. Railway → your project → **Settings** → **Pause Service**.
2. Customers can still WhatsApp the number; nobody replies until you
   un-pause. Inbound messages are NOT lost — Meta queues them and they
   get delivered when you resume.

**To resume:** Settings → Resume Service.

> **Not a permanent fix.** If you'll be off for >24 hours, post a status
> message on the Florista Instagram or website ("Replies after Monday")
> so customers know what to expect.

### Recipe 10 — Take manual control of one specific customer

The bot is doing fine in general but THIS particular VIP buyer needs
your personal attention.

**Today's workaround** (until we build a proper kill-switch):

1. Open the Apps Script "Florista Sales" sheet → **Escalations** tab.
2. Add a row manually with that customer's phone number and reason.
3. Reply to the customer yourself on WhatsApp from the business app.
4. Tell the bot to stop responding by editing the conversation state —
   developer's job for now.

> **TODO** for the next sprint: a `manual_takeover` tool the bot can be
> told to call (via your own admin chat to the bot), which silences
> the bot for a specific phone number. Tracked in `ROADMAP.md`.

### Recipe 11 — See what the bot has been saying

Two ways:

**A. The Sheets:**
- **Leads** tab — every qualified lead the bot logged
- **Qualified** tab — every decorator-vs-personal answer
- **Escalations** tab — every time the bot handed off to a human

These give you the *outcomes*. Each row has a timestamp and a phone
number; cross-reference with WhatsApp to see the conversation.

**B. Railway logs (the full conversation transcript):**
1. Railway → your project → **Deployments** → click the active deployment.
2. Click **View Logs**.
3. Search by phone number — every inbound message and the bot's reply
   is logged with `inbound from=...` and `outbound to=...`.

Logs are kept for 7 days on Railway free, longer on paid. For longer
retention, see "Add a Conversations sheet" in the steering file.

### Recipe 12 — A customer says the bot quoted them the wrong price

**Don't panic. Investigate before you blame the bot.**

1. Get the customer's phone number and the rough time of the conversation.
2. Open Railway logs, search by phone, find the conversation.
3. Look for the `lookup_pricing` tool call in the logs — you'll see what
   product slug + quantity the bot asked about, and what price the Sheet
   returned.
4. Three possible causes:
   - **Sheet was wrong at the time.** Someone fat-fingered an edit, then
     fixed it. Apologize and honor whichever is more reasonable.
   - **Bot picked the wrong product slug.** The customer said "the giant
     ones" and the bot picked the wrong giant. Fix: tighten the prompt
     to tell the bot *"always confirm the slug with the customer before
     quoting"* (already there in the default prompt — make it firmer if
     this keeps happening).
   - **Bot ignored the Sheet entirely.** Should be impossible by design,
     but if it does happen, this is a bug — file an issue with the log
     line and we'll fix the prompt.

The Apps Script Executions log (in the script editor) also stores every
`lookup_pricing` call with full timestamp + arguments + return value.
That's the legal-level audit trail.

---

## What lives where (one-line reference)

```
Bot's brain (model)              Railway env var: MODEL
Bot's tone, rules, persona       wa-bot/src/florista_bot/prompts.py
Bot's product list               wa-bot/data/products.json
Prices, lead times               Google Sheet → Pricing tab
What the bot calls the world     wa-bot/src/florista_bot/tools.py
What the tools read/write        wa-bot/apps_script/Code.gs
Conversation state               SQLite at /app/data on Railway (don't touch)
Inbound webhook URL              <your Railway URL>/webhook
Logs / past conversations        Railway → Deployments → View Logs
Lead records                     Google Sheet → Leads tab
Qualifications                   Google Sheet → Qualified tab
Hand-offs to humans              Google Sheet → Escalations tab
```

---

## Architecture for the curious

You can skip this section if all you want is to operate the bot. It's
here for when you're trying to understand WHY something works the way
it does.

### LangGraph — what it is

The bot is built on a Python library called **LangGraph**. Think of it
as a flowchart engine for AI conversations:

```
   START
     │
     ▼
   ┌────────┐    no tool needed
   │ agent  │───────────────────▶ END (send reply to customer)
   └───┬────┘
       │ tool call needed
       ▼
   ┌────────┐
   │ tools  │ (run the lookup_pricing or log_lead or whatever)
   └───┬────┘
       │
       └──── back to agent (feed the tool result, decide next step)
```

That's the whole graph. The agent is the AI; the tools are the things
the AI can DO (look up prices, log leads, hand off to humans). The graph
just routes between them.

### Tool calling — why it matters

The breakthrough that makes this design work is **tool calling**: the AI
doesn't just produce text, it can produce a structured request like
*"call lookup_pricing with product='60-inch-giant-flora' and quantity=300"*.
Our code receives that, runs the actual function, and feeds the result
back. The AI then writes a customer-facing reply that includes the real
number.

This is the fundamental fix for hallucinations: the AI never gets to
*be* the source of facts. It just orchestrates the conversation around
facts that come from real systems (your Sheet).

### Why SQLite for conversation state

When a customer sends a follow-up message ("Make that 500 pieces
instead"), the bot needs to remember the previous turn. LangGraph stores
the conversation in a tiny SQLite file on disk, keyed by phone number.

We chose SQLite (not a database server) because:
- Free
- One file, easy to back up
- Plenty fast for hundreds of customers a day
- No moving parts to break

Trade-off: the bot must run on a host that gives you a persistent disk.
That's why the setup pins you to Railway/Fly/Render and rules out Vercel
(no persistent disk → bot would forget every customer between messages).

### Why OpenRouter, not OpenAI directly

OpenRouter is a thin proxy in front of every major AI model. By using
it, the same code runs against ChatGPT, Claude, Gemini, Mistral, or any
new model that comes out, with no code change — just edit the `MODEL`
env var.

Cost is the same as going to OpenAI directly (OpenRouter takes a tiny
markup, ~3%, in exchange for the convenience).

---

## Troubleshooting

### "The bot doesn't reply at all"

In order:

1. **Is the service running?** Railway → your project → check status is
   "Active" not "Crashed" or "Paused".
2. **Is Meta still authorized?** Meta tokens can expire (check that you
   used the **System User permanent** token, not the 24-hour one). If
   the token is bad, you'll see auth errors in Railway logs.
3. **Did your sandbox-mode allowlist run out?** During Meta development
   mode you can only message numbers you've added to a test allowlist.
   Once you upgrade to production access in Meta, this restriction lifts.
4. **Is the webhook still configured?** Meta dashboard → WhatsApp →
   Configuration → Webhook. Make sure your Railway URL is still pasted
   there and the `messages` field is subscribed.

### "The bot replies but quotes the wrong price"

Almost always a Pricing sheet issue:
- A row is missing for that quantity tier.
- The slug in the Pricing sheet doesn't match `products.json` exactly
  (case-sensitive, no extra spaces).
- Two tier ranges overlap (e.g. one row says 100–999 and another says
  500–999 — the bot picks the first match it sees).

Open the Pricing sheet and audit the rows for that product. Check the
Apps Script Executions log to see what the bot asked for vs what got
returned.

### "The bot escalates everything to a human"

The prompt is probably too cautious. Open `prompts.py` and find the
escalation guidance:

```
- For custom orders, AI/Pinterest reference designs, unusual colors, ...
```

If everyday questions are getting escalated, that section is too broad.
Tighten it to only the genuinely judgment-needing cases.

If the bot escalates because *it can't find the answer in its tools*,
the fix is to add a new tool, not to reword the prompt. See the steering
file's "Adding a new tool" section.

### "The bot doesn't escalate when it should"

Opposite problem. Add explicit examples to the escalation list. Be
specific:

```
- If the customer mentions any of the following, escalate immediately:
  "Pinterest", "AI image", "custom color", "EMI", "credit", "pay later",
  "GST invoice", "complaint", "refund", "broken", "damaged".
```

Concrete trigger words work better than abstract categories.

### "Customer says the bot feels robotic"

Three levers, in order of cost:

1. **Add real conversation examples to the prompt.** Find 3–5 *good*
   conversations (real ones, anonymized) that you'd want the bot to
   imitate. Paste them into `prompts.py` under a new section
   `# Example conversations`. AI models are excellent at imitating
   examples.
2. **Raise temperature.** In `wa-bot/src/florista_bot/agent.py`, find
   `temperature=0.3` and try `0.5`. Higher = more variety. Don't go
   above 0.7 for a sales bot.
3. **Upgrade the model.** Recipe 8. Mini → 4o or Sonnet is a big jump
   in conversational naturalness.

### "The bot keeps asking the same question over and over"

This is a state bug — the bot isn't reading conversation history. Two
likely causes:

- The SQLite file isn't persisting across deploys. Check that Railway
  has a **Volume** mounted at `/app/data`. If not, every deploy wipes
  state.
- The bot got into a bad state for one customer. Easiest fix: ask a
  developer to delete that customer's row from the SQLite file. Or
  wait — most customers send a fresh message after a few hours, which
  the bot will respond to fresh.

### "The bot is sending too many messages per minute"

WhatsApp rate-limits at ~80 messages/sec for new business numbers (more
once Meta certifies you). For a sales bot, this is far above realistic
demand and shouldn't matter.

If you're seeing "rate limit exceeded" errors in the logs, you may have
a runaway loop (bot replying to its own messages, broadcast accidentally
fired). Pause the service, audit the recent logs, and contact a
developer.

---

## When to call a developer

| Situation | DIY or developer? |
|-----------|-------------------|
| Update a price | DIY (Sheet) |
| Update a lead time | DIY (Sheet) |
| Change tone, add hard rule, change escalation list | DIY (`prompts.py`) |
| Upgrade or downgrade the AI model | DIY (Railway env var) |
| Add a new product | DIY (Sheet + `products.json`) |
| Pause the bot | DIY (Railway) |
| Look at conversation logs | DIY (Railway logs) |
| Bot is hallucinating prices | **Developer** — prompt or tool bug |
| Bot is replying with the wrong format (no message body, just an error) | **Developer** — code bug |
| Add a new bot capability (e.g. send catalogue PDF, schedule a follow-up) | **Developer** — needs new tool |
| Switch hosting platform | **Developer** |
| Add a "manual takeover" feature | **Developer** |
| Bot needs to read images / videos | **Developer** — needs Meta media handling |

If you're not sure, file an issue on GitHub describing what you tried
and what happened. The repo has the full bot source in `wa-bot/`, so any
Python developer can diagnose.

---

## What's deliberately NOT built (yet)

The original n8n workflow design (in `florista_wa_bot_complete.json` —
legacy, can be deleted) had several use-cases that aren't in v1 of the
Python bot. Each is a 1–3 hour follow-up:

- **Catalogue PDF send** — when a buyer asks "do you have a catalogue?",
  the bot DMs them the PDF. (Tool: `send_catalogue_pdf`.)
- **24-hour follow-up** — if a quote was sent and no reply, the bot pings
  the customer the next day. Requires a Meta-approved message template.
- **Stock broadcast** — owner triggers a "new stock arrived" announcement
  to all opted-in numbers.
- **Post-event review request** — three days after the event date, ask
  for a photo or testimonial.
- **Inbound from website contact form** — when someone fills the contact
  form on the site, the bot proactively WhatsApps them.

These are all noted in `.kiro/steering/whatsapp-bot.md` ("Things
deliberately NOT in v1") and in `ROADMAP.md`. If any of them become
priority, they ship as separate PRs without disrupting the working
basics.

---

← [Previous: 10 — Cookbook](./10-cookbook.md) ・ [Back to the Manual Index →](./README.md)
