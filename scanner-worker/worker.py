# scanner-worker/worker.py
"""
Phase 1 worker — proves the container can boot and reach Redis.

In Phase 2 this gets replaced with a real job consumer that does BLPOP on
a queue, dispatches to specific scanners (dependency, Dockerfile, SBOM),
and writes findings to Postgres. For now, it's just a heartbeat.
"""
import logging
import os
import time

import redis

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] worker: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    logger.info("Connecting to Redis at %s:%s", redis_host, redis_port)
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    # Fail loud if Redis isn't reachable. Better to crash now and let
    # docker-compose restart us than to loop silently forever.
    r.ping()
    logger.info("Redis connection OK. Worker idle (Phase 1 placeholder).")

    # Heartbeat loop — keeps the container alive and gives us a visible
    # log line every 30s so we know it's still running.
    while True:
        r.set("worker:last_heartbeat", time.time())
        logger.info("heartbeat")
        time.sleep(30)


if __name__ == "__main__":
    main()