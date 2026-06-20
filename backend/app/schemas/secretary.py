"""
Pydantic-схемы для модуля «Секретарь».

Для каждой сущности три схемы:
  - Create:   данные для создания
  - Update:   все поля опциональны (частичное обновление)
  - Response: что отдаём клиенту
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.secretary import TaskPriority


# ──────────────────────────── EVENT ────────────────────────────

class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    event_type: str = Field(default="meeting", max_length=50)
    location: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def check_times(self):
        """end_time должен быть позже start_time."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time должен быть позже start_time")
        return self


class EventUpdate(BaseModel):
    """Все поля опциональны — обновляем только переданные."""
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    event_type: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=255)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    event_type: str
    location: str | None
    created_at: datetime


# ──────────────────────────── TASK ────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Все поля опциональны. Позволяет, например, только отметить is_done."""
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_done: bool | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    is_done: bool
    priority: TaskPriority
    due_date: datetime | None
    created_at: datetime
