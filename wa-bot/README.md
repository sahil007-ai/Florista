# Florista WhatsApp Bot

LangGraph agent that handles inbound WhatsApp wholesale enquiries.
Conversational like a salesperson, but every price comes from a Google
Sheet via tool calls — the LLM cannot invent numbers.

> **Full deployment runbook:** `.kiro/steering/whatsapp-bot.md` in the
> repo root. This README is just a 60-second orientation.

## Architecture

```
WhatsApp ─► Meta Cloud API ─► FastAPI /webhook
                                    │
                                    ▼
                              LangGraph agent
                              (gpt-4o-mini via OpenRouter)
                                    │
                  tools ◄───────────┘  (httpx → Apps Script /exec)
                    │
                    ▼
              Google Sheets
              (Pricing | Leads | Qualified | Escalations)
```

## Local dev

```bash
cp .env.example .env       # then fill in real values
uv sync                    # installs deps from pyproject.toml
uv run uvicorn florista_bot.main:app --reload
```

The `/webhook` POST handler will fail without a valid `TOOLS_ENDPOINT`
and Meta credentials. To smoke-test the LangGraph loop in isolation,
import `florista_bot.agent.graph` from a Python REPL and `.invoke()`
it directly with a fake message.

## Deploy

`Dockerfile` is generic — works on Railway, Fly.io, Render, or any
container host. Set the env vars from `.env.example` in your host's
panel. Mount a volume at `/app/data` so SQLite checkpoints (per-
conversation state) persist across redeploys.

## Files

| Path | Purpose |
|---|---|
| `src/florista_bot/main.py` | FastAPI app + Meta webhook routes |
| `src/florista_bot/agent.py` | LangGraph build (agent ↔ tools loop) |
| `src/florista_bot/tools.py` | `@tool` wrappers calling Apps Script |
| `src/florista_bot/whatsapp.py` | Meta Cloud API client |
| `src/florista_bot/prompts.py` | System prompt (NO prices) + product list |
| `src/florista_bot/state.py` | LangGraph state schema |
| `src/florista_bot/config.py` | Env loader (pydantic-settings) |
| `data/products.json` | Product catalog (slugs + names, NO prices) |
| `apps_script/Code.gs` | Tool layer — pricing, lead logging, escalation |
