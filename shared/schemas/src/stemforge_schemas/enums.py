from enum import Enum


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    SEPARATING = "separating"
    DONE = "done"
    FAILED = "failed"


class StageEnum(str, Enum):
    DOWNLOAD = "download"
    SEPARATION = "separation"
