# backend/Dockerfile
# ----------------------------------------------------------------------
# Multi-stage build. The "builder" stage compiles dependencies that need
# gcc, the "runtime" stage is a clean slim image with only what's needed
# to run the app. Result: smaller image, smaller attack surface.
# ----------------------------------------------------------------------

# ---- Stage 1: builder ----
# This stage has compilers and dev libs. It exists only to produce the
# installed Python packages, then it gets discarded.
FROM python:3.12-slim AS builder

WORKDIR /app

# Install OS-level build dependencies. psycopg2-binary technically doesn't
# need these (it ships precompiled), but we keep them for consistency
# in case we add packages with C extensions later.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST, install, THEN copy code. This is a Docker
# layer-caching trick: as long as requirements.txt doesn't change,
# Docker reuses the cached "pip install" layer across rebuilds.
# Saves minutes on every rebuild during development.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: runtime ----
# This is the actual image we ship. No gcc, no source headers, no build
# tooling — just Python and the installed packages.
FROM python:3.12-slim

WORKDIR /app

# Runtime needs libpq5 (the Postgres client library) but NOT the dev headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Run as a non-root user. Containers running as root are flagged by
# basically every security scanner — including the one we're building.
# We'd be embarrassed to ship root containers in a supply chain security
# tool, so we don't.
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy app code with correct ownership in one step
COPY --chown=appuser:appuser . .

EXPOSE 8000

# Healthcheck lets Docker (and orchestrators like k8s later) know whether
# this container is actually serving traffic, not just running.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# --reload restarts uvicorn whenever code changes. Great for dev,
# strip this flag before deploying to production.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]