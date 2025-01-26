from typing import Optional

from sqlmodel import SQLModel, Field


class Pomodoro_Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    start_time: str
    end_time: str
    completed: bool