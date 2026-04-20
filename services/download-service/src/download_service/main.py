import os
import time

import redis
from rq import Queue

from stemforge_jobstore import update_job
from stemforge_schemas import (
    QUEUE_SEPARATION,
    JobStatusEnum,
    StageEnum,
)

REDIS_URL = os.environ["REDIS_URL"]

_redis_client: "redis.Redis | None" = None


def _redis() -> "redis.Redis":
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL)
    return _redis_client


def process_download(job_id: str) -> None:
    r = _redis()
    print(f"[download-service] starting job {job_id}", flush=True)
    try:
        update_job(
            r,
            job_id,
            status=JobStatusEnum.DOWNLOADING.value,
            stage=StageEnum.DOWNLOAD.value,
            progress=0.0,
        )
        for progress in (0.5, 1.0):
            time.sleep(1)
            update_job(r, job_id, progress=progress)
        update_job(r, job_id, status=JobStatusEnum.DOWNLOADED.value)

        Queue(QUEUE_SEPARATION, connection=r).enqueue(
            "separation_service.main.process_separation",
            job_id,
        )
        print(f"[download-service] finished {job_id}, enqueued separation", flush=True)
    except Exception as exc:
        print(f"[download-service] job {job_id} failed: {exc}", flush=True)
        update_job(
            r,
            job_id,
            status=JobStatusEnum.FAILED.value,
            error=str(exc),
        )
        raise
