"""Environment configuration loaded once at startup.

Every secret/URL the bot needs lives here. Set them in `.env` for local
runs and in your hosting platform's env panel in production. Nothing
else in the codebase reads `os.environ` directly — this module is the
single source of truth.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── OpenRouter ──────────────────────────────────────────────
    # MODEL is a single string so we can swap quality without code
    # changes. See .env.example for the recommended ladder.
    openrouter_api_key: str
    model: str = "openai/gpt-4o-mini"

    # ── Meta WhatsApp Cloud API ─────────────────────────────────
    wa_phone_number_id: str
    wa_access_token: str
    # We pick this string; Meta echoes it back during the GET handshake
    # so we know the webhook config came from us.
    wa_verify_token: str

    # ── Apps Script tool layer ──────────────────────────────────
    # All bot tools (lookup_pricing, log_lead, ...) hit this single
    # /exec endpoint with {action, ...args}. See apps_script/Code.gs.
    tools_endpoint: str

    # ── Optional ────────────────────────────────────────────────
    owner_phone: str = ""
    checkpoint_db: str = "data/checkpoints.sqlite"


settings = Settings()  # type: ignore[call-arg]
