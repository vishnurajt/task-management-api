from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.db_models import PriorityEnum, StatusEnum
from enum import Enum


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str


# --- TASK SCHEMAS ---

class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"

class SortFieldEnum(str, Enum):
    created_at = "created_at"
    due_date = "due_date"
    priority = "priority"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.todo
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    priority: PriorityEnum
    status: StatusEnum
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int

class TaskListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tasks: list[TaskResponse]
    total: int
