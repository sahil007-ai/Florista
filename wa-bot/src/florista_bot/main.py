"""FastAPI entrypoint.

Three routes:
  GET  /          health probe (Railway/Fly use this for liveness)
  GET  /webhook   Meta verification handshake (one-time, on first wire-up)
  POST /webhook   inbound WhatsApp messages

The webhook MUST always return 200 (even on internal errors), or Meta
will keep retrying and exhaust your message quota. Errors are logged
and acked.
"""
import logging

from fastapi import FastAPI, HTTPException, Request
from langchain_core.messages import HumanMessage

from .agent import graph
from .config import settings
from .whatsapp import parse_webhook, send_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("florista_bot")

app = FastAPI(title="Florista WA Bot", version="0.1.0")


@app.get("/")
def health():
    return {"status": "ok", "model": settings.model}


@app.get("/webhook")
def verify(request: Request):
    """Meta's GET handshake: echo hub.challenge if verify_token matches.

    You'll trigger this exactly once, when pasting the public webhook
    URL into Meta → WhatsApp → Configuration → Webhook.
    """
    p = request.query_params
    if (
        p.get("hub.mode") == "subscribe"
        and p.get("hub.verify_token") == settings.wa_verify_token
    ):
        return int(p.get("hub.challenge", 0))
    raise HTTPException(status_code=403, detail="verify_token mismatch")


@app.post("/webhook")
async def receive(request: Request):
    """Process one inbound WhatsApp text message through the agent."""
    body = await request.json()
    msg = parse_webhook(body)
    if msg is None:
        # Status updates, non-text media, etc. — ack and skip.
        return {"ok": True}

    log.info("inbound from=%s text=%r", msg.from_phone, msg.text[:120])

    # thread_id = phone keeps each customer's conversation separate
    # in the SQLite checkpointer.
    config = {"configurable": {"thread_id": msg.from_phone}}

    try:
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=msg.text)],
                "phone": msg.from_phone,
            },
            config=config,
        )
        reply = result["messages"][-1].content
        if isinstance(reply, list):
            # Some models return content as a list of parts; flatten.
            reply = "".join(
                p.get("text", "") if isinstance(p, dict) else str(p)
                for p in reply
            )
        if reply:
            await send_message(msg.from_phone, reply)
    except Exception:
        # Never let an exception bubble back to Meta — they'll retry
        # and we'll spam the customer. Log and ack.
        log.exception("agent failed for phone=%s", msg.from_phone)

    return {"ok": True}
