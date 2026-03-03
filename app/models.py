from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Submission(BaseModel):
    id: str
    task_id: str
    submitted_by: str
    content: str = Field(..., min_length=3, max_length=4000)
    created_at: datetime
    status: str = "SUBMITTED"


class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=3, max_length=140)
    description: str = Field(..., min_length=5, max_length=4000)
    price: float = Field(0, ge=0)
    token: Optional[str] = Field(default=None, max_length=20)
    status: str = "OPEN"
    created_at: datetime
    created_by: str
    accepted_solution_id: Optional[str] = None

    payment_required: bool = False
    payment_status: str = "NOT_REQUIRED"
    payment_reference: Optional[str] = None
    platform_fee_bps: int = 0


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=140)
    description: str = Field(..., min_length=5, max_length=4000)
    price: float = Field(0, ge=0)
    token: Optional[str] = Field(default=None, max_length=20)


class SubmissionCreate(BaseModel):
    content: str = Field(..., min_length=3, max_length=4000)
