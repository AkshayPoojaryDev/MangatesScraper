from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class CourseRequest(BaseModel):
    courses: List[str]

class Job(BaseModel):
    id: str
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    logs: List[str] = []
    success: List[str] = []
    failed: List[str] = []
    
    class Config:
        from_attributes = True
