from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Union
from app.database import get_db
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, OrderEnum, SortFieldEnum
from app.core.auth import get_current_user
from app.models.db_models import UserDB,  PriorityEnum, StatusEnum

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
def get_tasks(status:  Union[StatusEnum, None]  = Query(default=None, description="Filter by status"),
              priority: Union[PriorityEnum, None]  = Query(default=None, description="Filter by priority"),
              search: Optional[str] = Query(default=None),
              order: OrderEnum = Query(default=OrderEnum.desc),
              skip: int = Query(default=0, ge=0),
              limit: int = Query(default=10, ge=1, le=100),
              sort_by: SortFieldEnum = Query(default=SortFieldEnum.created_at, description="created_at, due_date, priority"),
              db: Session = Depends(get_db),
              current_user: UserDB = Depends(get_current_user)
   ):
    query = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id)

    if status is not None:
        query = query.filter(TaskDB.status == status)

    if priority is not None:
        query = query.filter(TaskDB.priority == priority)

    if search is not None:
        query = query.filter(TaskDB.title.ilike(f"%{search}%"))

    sort_fields = {
        "created_at": TaskDB.created_at,
        "due_date": TaskDB.due_date,
        "priority": TaskDB.priority
    }

    sort_column = sort_fields.get(sort_by, TaskDB.created_at)

    if order == OrderEnum.asc:
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())



    total = query.count()

    tasks = query.offset(skip).limit(limit).all()

    return {"tasks": tasks, "total": total}
   



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