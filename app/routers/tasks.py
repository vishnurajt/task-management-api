from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.core.auth import get_current_user
from app.models.db_models import UserDB

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# --- CREATE TASK ---
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    new_task = TaskDB(
        **task.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# --- GET ALL TASKS ---
@router.get("/", response_model=TaskListResponse)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    tasks = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id).all()
    return {"tasks": tasks, "total": len(tasks)}


# --- GET SINGLE TASK ---
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


# --- UPDATE TASK ---
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Only update fields that were actually sent
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# --- DELETE TASK ---
@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    db.delete(task)
    db.commit()