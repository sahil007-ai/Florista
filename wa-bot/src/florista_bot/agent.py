"""LangGraph definition: agent ↔ tools loop with SQLite checkpointing.

Graph shape (intentionally minimal in v1):

      ┌───────┐   no tool calls    ┌─────┐
      │ agent │ ──────────────────▶│ END │
      └───────┘                    └─────┘
         ▲ │ tool calls
         │ ▼
      ┌───────┐
      │ tools │ (ToolNode runs every requested tool, returns results)
      └───────┘

The qualifier (decorator vs personal) and tier-discovery logic are NOT
graph nodes — they're enforced by the system prompt + the qualify_buyer
tool. This is the LangGraph philosophy: keep the graph thin, push
behavior into prompts and tools. If conversations start drifting in
production, promote the qualifier to a real conditional node here.

Persistence: SqliteSaver keyed by `thread_id` (set in main.py to the
customer's phone). Each phone gets its own conversation history that
survives process restarts.
"""
import os
import sqlite3

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from .config import settings
from .prompts import SYSTEM_PROMPT
from .state import AgentState
from .tools import TOOLS


def _llm():
    """Build the chat model bound to our tools.

    OpenRouter is OpenAI-API-compatible, so we just point langchain-openai
    at openrouter.ai/api/v1. To swap to native Anthropic later, replace
    this with ChatAnthropic and remove the base_url.
    """
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        # OpenRouter recommends these headers for usage attribution.
        default_headers={
            "HTTP-Referer": "https://www.theflorista.in",
            "X-Title": "Florista WhatsApp Bot",
        },
        # Low temperature: B2B sales should be predictable, not creative.
        temperature=0.3,
    ).bind_tools(TOOLS)


def _agent_node(state: AgentState) -> dict:
    """Single LLM step: read history, decide reply or tool call."""
    sys_text = SYSTEM_PROMPT
    # Surface the customer's phone to the LLM so it can pass it to
    # tools that need it (log_lead, qualify_buyer, escalate_to_human)
    # without us having to wire it through every tool args manually.
    if state.get("phone"):
        sys_text += f"\n\n# Current customer\nphone: {state['phone']}"
    response = _llm().invoke(
        [SystemMessage(content=sys_text), *state["messages"]]
    )
    return {"messages": [response]}


def _route(state: AgentState) -> str:
    """If the LLM wants tools, run them; otherwise we're done."""
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    """Build, compile, and return the agent graph.

    Side-effect: creates the checkpoint sqlite file's parent dir if
    missing, and runs SqliteSaver.setup() to ensure tables exist.
    """
    db_dir = os.path.dirname(settings.checkpoint_db)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # check_same_thread=False because uvicorn workers/asyncio reuse
    # the connection across event-loop tasks. SQLite-WAL handles this
    # safely; the saver itself locks per-write.
    conn = sqlite3.connect(settings.checkpoint_db, check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()

    g = StateGraph(AgentState)
    g.add_node("agent", _agent_node)
    g.add_node("tools", ToolNode(TOOLS))
    g.set_entry_point("agent")
    g.add_conditional_edges("agent", _route, {"tools": "tools", END: END})
    g.add_edge("tools", "agent")
    return g.compile(checkpointer=saver)


# Build once at import. FastAPI workers share this; the SqliteSaver
# is thread-safe for our QPS.
graph = build_graph()
