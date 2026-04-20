# syntax=docker/dockerfile:1.7

# --- builder ---------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /workspace

COPY pyproject.toml ./pyproject.toml
COPY shared/schemas/pyproject.toml ./shared/schemas/pyproject.toml
COPY shared/schemas/src ./shared/schemas/src
COPY shared/jobstore/pyproject.toml ./shared/jobstore/pyproject.toml
COPY shared/jobstore/src ./shared/jobstore/src
COPY services/download-service/pyproject.toml ./services/download-service/pyproject.toml
COPY services/download-service/src ./services/download-service/src

# TODO: añadir --frozen tras commitear uv.lock
RUN uv sync --no-dev --package download-service

# --- runtime ---------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /workspace /workspace

WORKDIR /workspace/services/download-service

CMD ["sh", "-c", "exec rq worker --url \"$REDIS_URL\" downloads"]
