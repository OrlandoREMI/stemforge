import json
from datetime import datetime, timezone
from typing import Any

import redis
from stemforge_schemas import JobStatus, job_channel, job_key


def _decode(value: Any) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else value


def _load_hash(raw: dict[Any, Any]) -> dict[str, Any]:
    return {_decode(k): json.loads(_decode(v)) for k, v in raw.items()}


def get_job(r: "redis.Redis", job_id: str) -> JobStatus | None:
    raw = r.hgetall(job_key(job_id))
    if not raw:
        return None
    return JobStatus.model_validate(_load_hash(raw))


def update_job(r: "redis.Redis", job_id: str, **fields: Any) -> JobStatus:
    """
    Atomically HSET provided fields (JSON-encoded) and PUBLISH the full
    resulting JobStatus on the job's channel. Returns the new JobStatus.

    Merges on top of any existing hash. `job_id` and `updated_at` are
    always set by this function; `created_at` must be supplied the first
    time a job is written.
    """
    raw = r.hgetall(job_key(job_id))
    current = _load_hash(raw) if raw else {}
    current.update(fields)
    current["job_id"] = job_id
    current["updated_at"] = datetime.now(timezone.utc)

    status = JobStatus.model_validate(current)

    payload = status.model_dump(mode="json")
    mapping = {k: json.dumps(v) for k, v in payload.items()}
    message = status.model_dump_json()

    pipe = r.pipeline(transaction=True)
    pipe.hset(job_key(job_id), mapping=mapping)
    pipe.publish(job_channel(job_id), message)
    pipe.execute()

    return status
