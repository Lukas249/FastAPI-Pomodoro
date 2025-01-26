import math
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from models.task import Task
from models.pomodoro_session import Pomodoro_Session

from db_storage import session

pomodoro_router = APIRouter(prefix="/pomodoro")

def is_active_pomodoro_session(pomodoro_session):
    curr_datetime = datetime.now()

    end_time = datetime.strptime(pomodoro_session.end_time, "%Y-%m-%d %H:%M:%S.%f")

    return not end_time < curr_datetime


class Pomodoro(BaseModel):
    task_id: int
    duration: int = Field(gt=0, default=25)

def update_pomodoro_sessions(curr_datetime: datetime):
    statement = select(Pomodoro_Session).where(Pomodoro_Session.completed == False, Pomodoro_Session.end_time < curr_datetime)

    for pomodoro_session in session.exec(statement).all():
        pomodoro_session.completed = True

        session.add(pomodoro_session)

    session.commit()

@pomodoro_router.post(
    "/",
    responses={
        200: {
           "content": {
               "application/json": {
                   "schema": {
                       "example": {
                            "task_id": 1,
                            "start_time": "2025-01-09T12:00:00",
                            "end_time": "2025-01-09T12:25:00",
                            "completed": False,
                       }
                   }
               }
           }
        },
        404: {
           "description": "Not found",
           "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "detail": "Task with the given ID doesn't exist"
                       }
                   }
               }
           }
        },
        409: {
           "description": "Already exists",
           "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "detail": "Pomodoro with the given task ID already exists"
                       }
                   }
               }
           }
       }
   }
)
def create_pomodoro_session(pomodoro: Pomodoro):
    curr_datetime = datetime.now()

    task = session.get(Task, pomodoro.task_id)
    pomodoro_session = session.exec(select(Pomodoro_Session).where(Pomodoro_Session.task_id == pomodoro.task_id, Pomodoro_Session.completed == False)).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task with the given ID doesn't exist")

    if pomodoro_session and is_active_pomodoro_session(pomodoro_session):
        raise HTTPException(status_code=409, detail="Pomodoro with the given task ID already exists")

    if pomodoro_session:
        pomodoro_session.completed = True
        session.add(pomodoro_session)

    new_pomodoro_session = Pomodoro_Session(task_id=pomodoro.task_id, start_time=str(curr_datetime), end_time=str(curr_datetime + timedelta(minutes=pomodoro.duration)), completed=False)

    session.add(new_pomodoro_session)
    session.commit()
    session.refresh(new_pomodoro_session)

    return new_pomodoro_session

@pomodoro_router.post(
    "/{task_id}/stop",
    responses={
        200: {
           "content": {
               "application/json": {
                   "schema": {
                       "example": {
                            "task_id": 1,
                            "start_time": "2025-01-09T12:00:00",
                            "end_time": "2025-01-09T12:25:00",
                            "completed": True,
                       }
                   }
               }
           }
        },
        404: {
           "description": "Not found",
           "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "detail": "Active pomodoro with the given task ID doesn't exist"
                       }
                   }
               }
           }
        }
   }
)
def stop_pomodoro_session(task_id: int):
    statement = select(Pomodoro_Session).where(Pomodoro_Session.task_id == task_id, Pomodoro_Session.completed == False)
    pomodoro_session = session.exec(statement).first()

    if not pomodoro_session:
        raise HTTPException(status_code=404, detail="Active pomodoro with the given task ID doesn't exist")

    pomodoro_session.completed = True

    if not is_active_pomodoro_session(pomodoro_session):
        session.add(pomodoro_session)
        session.commit()
        raise HTTPException(status_code=404, detail="Active pomodoro with the given task ID doesn't exist")

    curr_datetime = datetime.now()

    pomodoro_session.end_time = str(curr_datetime)

    session.add(pomodoro_session)
    session.commit()
    session.refresh(pomodoro_session)

    return pomodoro_session

@pomodoro_router.get(
    "/stats",
    responses={
        200: {
           "description": "",
           "content": {
               "application/json": {
                   "schema": {
                        "type": "object",
                        "properties": {
                            "1": {
                                "type": "integer",
                                "description": "Number of completed pomodoro sessions for task with ID 1"
                            },
                            "2": {
                                "type": "integer",
                                "description": "Number of completed pomodoro sessions for task with ID 2"
                            },
                            "3": {
                                "type": "integer",
                                "description": "Number of completed pomodoro sessions for task with ID 3"
                            },
                            "total_time": {
                                "type": "integer",
                                "description": "Total time spent on tasks in seconds"
                            }
                        },
                       "example": {
                            "1": 1,
                            "2": 3,
                            "3": 2,
                            "total_time": 100
                       }
                   }
               }
           }
        }
    }
)
def get_pomodoro_sessions_stats():
    tasks = session.exec(select(Task)).all()

    stats = {
        task.id: 0 for task in tasks
    }

    stats["total_time"] = 0

    pomodoro_sessions = session.exec(select(Pomodoro_Session)).all()

    for pomodoro_session in pomodoro_sessions:
        if is_active_pomodoro_session(pomodoro_session):
            continue

        task_id = pomodoro_session.task_id

        stats[task_id] = stats.get(task_id, 0) + 1

        start_time = datetime.strptime(pomodoro_session.start_time, "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(pomodoro_session.end_time, "%Y-%m-%d %H:%M:%S.%f")

        stats["total_time"] += math.floor((end_time - start_time).total_seconds())

    return stats