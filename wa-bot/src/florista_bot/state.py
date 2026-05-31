"""Agent conversation state.

LangGraph keys state per `thread_id` (set in main.py to the customer's
phone number), so each WhatsApp thread gets its own persistent state
across process restarts via the SQLite checkpointer.

We deliberately keep this minimal in v1 — the LLM tracks qualification
(decorator vs personal) by calling `qualify_buyer` and remembering its
own tool calls in conversation history. If you find yourself reaching
for more state fields, that's usually a smell that you should be making
a tool call instead.
"""
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """One row per WhatsApp thread."""

    # Conversation history. The `add_messages` reducer appends rather
    # than overwriting, which is what every agent loop needs.
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Customer's phone in E.164 (no leading +). Set on every invoke
    # from the inbound webhook so tools that need it (log_lead,
    # escalate_to_human) can read it from the system prompt suffix.
    phone: str
