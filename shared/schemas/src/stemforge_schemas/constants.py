QUEUE_DOWNLOADS = "downloads"
QUEUE_SEPARATION = "separation"


def job_key(job_id: str) -> str:
    return f"job:{job_id}"


def job_channel(job_id: str) -> str:
    return f"job:{job_id}:events"
