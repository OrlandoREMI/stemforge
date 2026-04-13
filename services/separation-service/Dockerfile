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
COPY services/separation-service/pyproject.toml ./services/separation-service/pyproject.toml
COPY services/separation-service/src ./services/separation-service/src

# TODO: añadir --frozen tras commitear uv.lock
RUN uv sync --no-dev --package separation-service

# --- runtime ---------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /workspace/services/separation-service/src ./src
COPY --from=builder /workspace/shared/schemas/src ./shared_src

ENV PYTHONPATH=/app/src:/app/shared_src

CMD ["python", "-m", "separation_service.main"]
