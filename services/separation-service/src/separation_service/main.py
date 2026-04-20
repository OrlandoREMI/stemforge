import os
import time

import redis

from stemforge_jobstore import update_job
from stemforge_schemas import JobStatusEnum, StageEnum

REDIS_URL = os.environ["REDIS_URL"]

_redis_client: "redis.Redis | None" = None


def _redis() -> "redis.Redis":
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL)
    return _redis_client


def process_separation(job_id: str) -> None:
    r = _redis()
    print(f"[separation-service] starting job {job_id}", flush=True)
    try:
        update_job(
            r,
            job_id,
            status=JobStatusEnum.SEPARATING.value,
            stage=StageEnum.SEPARATION.value,
            progress=0.0,
        )
        for progress in (0.25, 0.5, 0.75, 1.0):
            time.sleep(1.25)
            update_job(r, job_id, progress=progress)

        result_paths = [
            f"/data/jobs/{job_id}/vocals.mp3",
            f"/data/jobs/{job_id}/drums.mp3",
            f"/data/jobs/{job_id}/bass.mp3",
            f"/data/jobs/{job_id}/other.mp3",
        ]
        update_job(
            r,
            job_id,
            status=JobStatusEnum.DONE.value,
            result_paths=result_paths,
        )
        print(f"[separation-service] finished {job_id}", flush=True)
    except Exception as exc:
        print(f"[separation-service] job {job_id} failed: {exc}", flush=True)
        update_job(
            r,
            job_id,
            status=JobStatusEnum.FAILED.value,
            error=str(exc),
        )
        raise
