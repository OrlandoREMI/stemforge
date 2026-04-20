import asyncio
import os
import uuid
from datetime import datetime, timezone

import redis
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from rq import Queue
from sse_starlette.sse import EventSourceResponse

from stemforge_jobstore import get_job, update_job
from stemforge_schemas import (
    QUEUE_DOWNLOADS,
    JobCreateRequest,
    JobStatus,
    JobStatusEnum,
    job_channel,
)

REDIS_URL = os.environ["REDIS_URL"]
TERMINAL_STATUSES = {JobStatusEnum.DONE, JobStatusEnum.FAILED}

sync_redis = redis.Redis.from_url(REDIS_URL)
async_redis = aioredis.from_url(REDIS_URL)
download_queue = Queue(QUEUE_DOWNLOADS, connection=sync_redis)

app = FastAPI(title="stemforge api-gateway")


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "api-gateway", "status": "ok"}


@app.post("/jobs")
async def create_job(req: JobCreateRequest) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    await asyncio.to_thread(
        update_job,
        sync_redis,
        job_id,
        url=str(req.url),
        status=JobStatusEnum.PENDING.value,
        progress=0.0,
        created_at=now,
    )
    await asyncio.to_thread(
        download_queue.enqueue,
        "download_service.main.process_download",
        job_id,
    )
    return {"job_id": job_id}


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def read_job(job_id: str) -> JobStatus:
    status = await asyncio.to_thread(get_job, sync_redis, job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="job not found")
    return status


@app.get("/jobs/{job_id}/events")
async def job_events(job_id: str) -> EventSourceResponse:
    initial = await asyncio.to_thread(get_job, sync_redis, job_id)
    if initial is None:
        raise HTTPException(status_code=404, detail="job not found")

    async def event_stream():
        pubsub = async_redis.pubsub()
        await pubsub.subscribe(job_channel(job_id))
        try:
            yield {"data": initial.model_dump_json()}
            if initial.status in TERMINAL_STATUSES:
                return
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                yield {"data": data}
                parsed = JobStatus.model_validate_json(data)
                if parsed.status in TERMINAL_STATUSES:
                    break
        finally:
            await pubsub.unsubscribe(job_channel(job_id))
            await pubsub.aclose()

    return EventSourceResponse(event_stream())
