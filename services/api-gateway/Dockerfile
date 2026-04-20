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
COPY services/api-gateway/pyproject.toml ./services/api-gateway/pyproject.toml
COPY services/api-gateway/src ./services/api-gateway/src

# TODO: añadir --frozen tras commitear uv.lock
RUN uv sync --no-dev --package api-gateway

# --- runtime ---------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy venv + the whole workspace at the same path the editable .pth entries
# point to, so imports of workspace packages resolve at runtime.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /workspace /workspace

WORKDIR /workspace/services/api-gateway

EXPOSE 8000
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
