"""Tools the LangGraph agent can call.

Each tool is a thin HTTP wrapper around the Apps Script `/exec` endpoint.
The contract is intentionally narrow: the LLM gets back exactly what
Apps Script returns, with no client-side massaging. This keeps Apps
Script the single source of truth for prices, sheet writes, and side
effects — and lets you change pricing logic without redeploying Python.

Adding a new tool:
  1. Add a `case` to the switch in apps_script/Code.gs.
  2. Add a `@tool` function here that calls _call("your_action", ...).
  3. Append it to TOOLS at the bottom.
The agent picks it up on next restart — no other wiring needed.
"""
import json

import httpx
from langchain_core.tools import tool

from .config import settings

# Sync client is fine — tool calls run inside LangGraph's ToolNode
# which already manages concurrency at the graph level. Async would
# add complexity for no measurable win at WhatsApp's QPS.
_client = httpx.Client(timeout=10.0)


def _call(action: str, payload: dict) -> dict:
    """POST {action, ...payload} as text/plain to bypass CORS preflight.

    Apps Script Web Apps return 405 if you send application/json (CORS
    preflight requires OPTIONS handling Apps Script doesn't do). The
    text/plain workaround is documented in Google's own samples and is
    the same pattern used by the existing lead-capture pipeline — see
    .kiro/steering/lead-capture.md.
    """
    body = json.dumps({"action": action, **payload})
    r = _client.post(
        settings.tools_endpoint,
        headers={"Content-Type": "text/plain;charset=utf-8"},
        content=body,
        follow_redirects=True,  # Apps Script 302s through googleusercontent
    )
    r.raise_for_status()
    return r.json()


@tool
def lookup_pricing(product_slug: str, quantity: int) -> dict:
    """Get the wholesale price for a product at a given quantity.

    ALWAYS use this tool to answer any pricing question — never quote
    a price from memory.

    Args:
        product_slug: Product identifier from the catalog in the system
            prompt, e.g. "60-inch-giant-flora".
        quantity: Number of pieces the buyer wants.

    Returns dict with keys:
        product_slug, quantity, price_per_piece, total, tier_label,
        lead_time_days, moq_met. If quantity is below MOQ, returns
        {"error": "..."} instead.
    """
    return _call("lookup_pricing", {
        "product_slug": product_slug,
        "quantity": quantity,
    })


@tool
def log_lead(
    phone: str,
    name: str,
    requirement: str,
    items: str,
    tier: str,
) -> dict:
    """Append a qualified lead to the Sales sheet.

    Call this once you have at least name + a clear requirement +
    a quantity tier. Don't wait for the conversation to end — log
    early so the team can follow up even if the customer drops off.
    """
    return _call("log_lead", {
        "phone": phone, "name": name,
        "requirement": requirement, "items": items, "tier": tier,
    })


@tool
def qualify_buyer(phone: str, buyer_type: str) -> dict:
    """Record buyer qualification.

    Args:
        buyer_type: Exactly "decorator" or "personal".
    """
    return _call("qualify_buyer", {
        "phone": phone, "buyer_type": buyer_type,
    })


@tool
def escalate_to_human(phone: str, reason: str, context: str) -> dict:
    """Hand off to the Florista team.

    Use for: custom orders, AI/Pinterest references, unusual colors or
    sizes, payment-term negotiations, complaints, or any question you
    cannot confidently answer with the other tools.

    Args:
        reason: Short tag, e.g. "custom_color", "off_menu_size",
            "payment_terms", "complaint".
        context: One- or two-sentence summary of what the buyer asked.
    """
    return _call("escalate_to_human", {
        "phone": phone, "reason": reason, "context": context,
    })


# Order matters only for human readability — the LLM picks tools by name.
TOOLS = [lookup_pricing, log_lead, qualify_buyer, escalate_to_human]
