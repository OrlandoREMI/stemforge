from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from .enums import JobStatusEnum, StageEnum


class JobCreateRequest(BaseModel):
    url: HttpUrl


class JobStatus(BaseModel):
    job_id: str
    url: str
    status: JobStatusEnum
    stage: StageEnum | None = None
    progress: float = 0.0
    error: str | None = None
    result_paths: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
