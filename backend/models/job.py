from pydantic import BaseModel
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class Job(BaseModel):
    job_id: str
    prompt: str
    duration: int
    resolution: str
    style: Optional[str] = "realistic"
    status: JobStatus = JobStatus.PENDING
    output_path: Optional[str] = None
    error: Optional[str] = None
