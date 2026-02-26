FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY data/ data/

RUN uv sync --no-dev --frozen

ENV RUN_MODE=loop
ENV CHECK_INTERVAL_MINUTES=30

CMD ["uv", "run", "python", "-m", "src.main"]
