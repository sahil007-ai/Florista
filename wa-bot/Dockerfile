# Florista WA Bot — production container.
# Works on Railway, Fly.io, Render, or any container host.
FROM python:3.12-slim

WORKDIR /app

# uv is 10-100x faster than pip and handles lockfiles natively.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

# Layer-cache deps before copying source.
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --no-dev || uv sync --no-dev --frozen

COPY src/ src/
COPY data/ data/

# SQLite checkpoint dir — mount a persistent volume here in prod
# so conversation state survives redeploys.
RUN mkdir -p data
VOLUME ["/app/data"]

EXPOSE 8000

# --proxy-headers lets the bot trust X-Forwarded-* from the platform's
# load balancer (Railway/Fly inject these). Required for correct https
# detection if you ever return absolute URLs.
CMD ["uv", "run", "uvicorn", "florista_bot.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers"]
