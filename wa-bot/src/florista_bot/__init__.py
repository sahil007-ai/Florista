"""Florista WhatsApp wholesale sales bot.

LangGraph agent that handles inbound WhatsApp messages, qualifies the
buyer (decorator vs personal), quotes from a Google Sheet via tool calls,
and logs every qualified lead. See `.kiro/steering/whatsapp-bot.md` in
the repo root for the deployment runbook.
"""

__version__ = "0.1.0"
