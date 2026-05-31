"""Meta WhatsApp Cloud API: webhook parsing + outbound text send.

Scope is deliberately tiny in v1:
  - parse_webhook: extract a single inbound TEXT message from Meta's
    deeply-nested envelope. Status updates, reactions, and non-text
    media are ignored (we ack them but don't process).
  - send_message: send a plain text reply.

Buttons / lists / templates are not used — the LLM asks free-form
questions instead, which is the whole point of the Option D shape.
If you ever add the catalogue PDF send (UC3 from the n8n workflow),
add a `send_document(phone, link, caption)` here and expose it as a
tool in tools.py.
"""
from dataclasses import dataclass

import httpx

from .config import settings

# v20.0 is current as of mid-2025. Bump as Meta releases new versions;
# they're backwards compatible for ~2 years.
_WA_BASE = "https://graph.facebook.com/v20.0"


@dataclass
class IncomingMessage:
    from_phone: str        # E.164 without leading +, e.g. "917588447595"
    text: str
    name: str | None       # WhatsApp profile name (only present on first contact in some cases)
    message_id: str        # Meta wamid; useful for read-receipts later


def parse_webhook(body: dict) -> IncomingMessage | None:
    """Pull the first text message out of a Meta webhook payload.

    Returns None for status updates, non-text messages, or malformed
    payloads. Callers should ack with 200 either way to prevent Meta
    from retrying.
    """
    try:
        change = body["entry"][0]["changes"][0]["value"]
        msgs = change.get("messages") or []
        if not msgs:
            return None
        m = msgs[0]
        if m.get("type") != "text":
            return None
        contacts = change.get("contacts") or [{}]
        return IncomingMessage(
            from_phone=m["from"],
            text=m["text"]["body"],
            name=contacts[0].get("profile", {}).get("name"),
            message_id=m["id"],
        )
    except (KeyError, IndexError, TypeError):
        return None


async def send_message(phone: str, text: str) -> None:
    """Send a plain-text WhatsApp message.

    Splits silently on Meta's 4096-char limit by truncating; LLM replies
    rarely exceed 500 chars so this is just a guardrail.
    """
    if len(text) > 4000:
        text = text[:3997] + "..."

    url = f"{_WA_BASE}/{settings.wa_phone_number_id}/messages"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.wa_access_token}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": text, "preview_url": False},
            },
        )
        r.raise_for_status()
