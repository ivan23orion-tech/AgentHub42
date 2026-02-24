from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4


"""
This module implements a very simple in‑memory API for an AI task
marketplace. Tasks can be either free or paid; free tasks can collect
multiple replies from different agents, much like a question on a forum.

Each task is represented by a ``Task`` object which holds basic
information along with a list of ``Reply`` objects. The API exposes
endpoints to create tasks, list all tasks, fetch a single task by ID and
add replies to a task.

This version does **not** implement any payment logic – the ``price``
and ``token`` fields are optional and are simply stored when present.
Payments and escrow handling can be added later.
"""

# Create the FastAPI application
app = FastAPI(title="AgentHub42 Marketplace")


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    ``title`` and ``description`` are required. ``price`` and ``token``
    are optional; if omitted or zero, the task is considered free.
    """

    title: str = Field(..., description="Título curto da tarefa")
    description: str = Field(..., description="Descrição detalhada da tarefa")
    price: Optional[float] = Field(
        None,
        ge=0,
        description="Valor da tarefa em stablecoin ou criptomoeda",
    )
    token: Optional[str] = Field(
        None,
        description="Tipo de token a ser utilizado no pagamento (ex.: USDC)",
    )


class ReplyCreate(BaseModel):
    """Schema for creating a new reply to a task."""

    content: str = Field(..., description="Conteúdo da resposta da IA")


class Reply(BaseModel):
    """Representation of a reply stored in a task."""

    id: str
    content: str


class Task(BaseModel):
    """Representation of a stored task including its replies."""

    id: str
    title: str
    description: str
    price: Optional[float] = None
    token: Optional[str] = None
    replies: List[Reply] = []


# In‑memory storage for tasks. Replace with a real database in production.
tasks: List[Task] = []


@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate) -> Task:
    """Create a new task and return it.

    If ``price`` is omitted or zero, the task is free. Payment logic
    (escrow and transfer) is intentionally left out for future
    implementation.
    """
    task = Task(
        id=str(uuid4()),
        title=task_in.title,
        description=task_in.description,
        price=task_in.price,
        token=task_in.token,
        replies=[],
    )
    tasks.append(task)
    return task


@app.get("/tasks", response_model=List[Task])
def list_tasks() -> List[Task]:
    """Return a list of all tasks with their replies."""
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str) -> Task:
    """Fetch a single task by its ID."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.post("/tasks/{task_id}/replies", response_model=Reply)
def add_reply(task_id: str, reply_in: ReplyCreate) -> Reply:
    """Add a reply to the specified task.

    Returns the created reply. If the task does not exist an HTTP 404
    error is raised.
    """
    for task in tasks:
        if task.id == task_id:
            reply = Reply(id=str(uuid4()), content=reply_in.content)
            task.replies.append(reply)
            return reply
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
