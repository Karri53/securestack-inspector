# scanner-worker/Dockerfile
# Lean image for the scanner worker. Notably includes `git` because
# Phase 2 will clone repositories under analysis. Everything else here
# mirrors the backend Dockerfile pattern.

FROM python:3.12-slim

WORKDIR /app

# git is the one OS-level tool we need at runtime — cloning repos
# to /workspace is the worker's main job.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user — same reasoning as the API container. The worker
# touches untrusted code, so locking down its privileges is even more
# important here than elsewhere.
RUN useradd --create-home --shell /bin/bash worker
USER worker

COPY --chown=worker:worker . .

CMD ["python", "worker.py"]