from typing import Optional

from sqlmodel import Field, SQLModel

from task_status import Status

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default="", max_length=300)
    status: Status = Status.DO_WYKONANIA