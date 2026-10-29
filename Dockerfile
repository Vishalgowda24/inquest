# Stage 1: Build dependencies and wheels
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY inquest/ inquest/
COPY simulator/ simulator/

# Build wheel
RUN pip install --no-cache-dir --upgrade pip build && \
    python -m build --wheel

# Stage 2: Final runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Install runtime dependencies and wheels
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /tmp/*.whl fastapi uvicorn httpx && \
    rm -rf /tmp/*.whl

# Copy application files
COPY config.yaml /app/config.yaml
COPY simulator /app/simulator
COPY inquest /app/inquest
COPY demo /app/demo
COPY docs /app/docs
COPY eval /app/eval
COPY scripts /app/scripts

# Fetch assets if missing
RUN python scripts/fetch_assets.py || true

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "demo.api:app", "--host", "0.0.0.0", "--port", "8000"]
