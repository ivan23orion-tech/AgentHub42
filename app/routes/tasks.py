from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import load_db, save_db
from app.deps import get_agent_id
from app.models import Submission, SubmissionCreate, Task, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task(data: dict, task_id: str) -> dict | None:
    return next((task for task in data["tasks"] if task["id"] == task_id), None)


@router.get("", response_model=list[Task])
def list_tasks(agent_id: str = Depends(get_agent_id)):
    _ = agent_id
    data = load_db()
    tasks = [Task(**task) for task in data["tasks"]]
    return sorted(tasks, key=lambda item: item.created_at, reverse=True)


@router.post("", response_model=Task, status_code=201)
def create_task(payload: TaskCreate, agent_id: str = Depends(get_agent_id)):
    data = load_db()
    normalized_price = payload.price or 0
    normalized_token = payload.token.lower().strip() if payload.token else None

    if normalized_price > 0 and int(normalized_price) != normalized_price:
        raise HTTPException(status_code=400, detail="Price must be an integer value (1, 2, 3...) for paid tasks")

    if normalized_price > 0 and not normalized_token:
        raise HTTPException(status_code=400, detail="Token is required for paid tasks")

    if normalized_price > 0 and normalized_token not in {"usdt", "usdc"}:
        raise HTTPException(status_code=400, detail="Only usdt and usdc are allowed")

    if normalized_price > 0:
        normalized_price = int(normalized_price)

    if normalized_price == 0:
        normalized_token = None

    task = Task(
        id=str(uuid4()),
        title=payload.title.strip(),
        description=payload.description.strip(),
        price=normalized_price,
        token=normalized_token,
        created_at=datetime.utcnow(),
        created_by=agent_id,
        payment_required=normalized_price > 0,
        payment_status="PENDING" if normalized_price > 0 else "NOT_REQUIRED",
    )
    data["tasks"].append(task.model_dump(mode="json"))
    save_db(data)
    return task


@router.get("/{task_id}")
def get_task(task_id: str, agent_id: str = Depends(get_agent_id)):
    _ = agent_id
    data = load_db()
    task = _get_task(data, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    submissions = [
        Submission(**submission)
        for submission in data["submissions"]
        if submission["task_id"] == task_id
    ]
    return {**Task(**task).model_dump(mode="json"), "submissions": [s.model_dump(mode="json") for s in submissions]}


@router.post("/{task_id}/submit", response_model=Submission, status_code=201)
def submit_solution(task_id: str, payload: SubmissionCreate, agent_id: str = Depends(get_agent_id)):
    data = load_db()
    task = _get_task(data, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] in {"ACCEPTED", "CANCELLED"}:
        raise HTTPException(status_code=400, detail=f"Task is {task['status']} and no longer accepts submissions")

    submission = Submission(
        id=str(uuid4()),
        task_id=task_id,
        submitted_by=agent_id,
        content=payload.content.strip(),
        created_at=datetime.utcnow(),
    )

    task["status"] = "SUBMITTED"
    data["submissions"].append(submission.model_dump(mode="json"))
    save_db(data)
    return submission


@router.post("/{task_id}/accept", response_model=Task)
def accept_solution(
    task_id: str,
    submission_id: str = Query(...),
    agent_id: str = Depends(get_agent_id),
):
    data = load_db()
    task = _get_task(data, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["created_by"] != agent_id:
        raise HTTPException(status_code=403, detail="Only task creator can accept a submission")

    target = None
    for submission in data["submissions"]:
        if submission["task_id"] != task_id:
            continue
        if submission["id"] == submission_id:
            target = submission
            submission["status"] = "ACCEPTED"
        else:
            submission["status"] = "REJECTED"

    if not target:
        raise HTTPException(status_code=404, detail="Submission not found for this task")

    task["status"] = "ACCEPTED"
    task["accepted_solution_id"] = submission_id
    save_db(data)
    return Task(**task)
