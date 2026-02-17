from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4


app = FastAPI(title="AI Tasks Marketplace")


class TaskCreate(BaseModel):
    """Modelo para criação de nova tarefa."""
    title: str = Field(..., description="Título curto da tarefa")
    description: str = Field(..., description="Descrição detalhada da tarefa")
    price: float = Field(..., gt=0, description="Valor da tarefa em stablecoin ou criptomoeda")
    token: str = Field(..., description="Tipo de token a ser utilizado no pagamento (ex.: USDC)")


class Task(TaskCreate):
    """Representação de uma tarefa armazenada."""
    id: str
    solved: bool = False
    solution: Optional[str] = None


# Armazenamento simples em memória. Em produção, substitua por um banco de dados.
tasks: List[Task] = []


@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate) -> Task:
    """Criar uma nova tarefa."""
    task = Task(id=str(uuid4()), **task_in.dict())
    tasks.append(task)
    return task


@app.get("/tasks", response_model=List[Task])
def list_tasks() -> List[Task]:
    """Listar todas as tarefas."""
    return tasks


@app.post("/tasks/{task_id}/solve")
def solve_task(task_id: str, solution: str) -> dict:
    """Enviar uma solução para a tarefa indicada."""
    for task in tasks:
        if task.id == task_id:
            if task.solved:
                raise HTTPException(status_code=400, detail="Tarefa já foi resolvida")
            # Aqui seria implementada a lógica de verificação da solução e liberação de pagamento.
            task.solved = True
            task.solution = solution
            # Pagamento e taxa ainda não implementados.
            return {"message": "Solução registrada. (Verificação e pagamento pendentes)"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
