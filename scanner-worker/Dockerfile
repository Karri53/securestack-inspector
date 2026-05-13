# scanner-worker/Dockerfile
# Lean image for the scanner worker. Notably includes git because it
# clones target repos into /workspace at runtime.

FROM python:3.12-slim

WORKDIR /app

# git is the one OS-level tool we need at runtime - cloning repos
# is the worker's main job.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the non-root worker user AND pre-create /workspace with the
# right ownership in a single step.
#
# Why this matters: docker-compose mounts a named volume (scan-workspace)
# at /workspace. When Docker initializes that volume for the first time,
# it copies the metadata (including ownership) of the directory at this
# path in the image. So if /workspace exists here as worker:worker, the
# volume comes up worker-owned. If we skip this step, the volume defaults
# to root:root and our non-root worker can't write into it.
RUN useradd --create-home --shell /bin/bash worker \
    && mkdir -p /workspace \
    && chown worker:worker /workspace

USER worker

COPY --chown=worker:worker . .

CMD ["python", "worker.py"]