import math
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from task_router import task_exists, tasks

pomodoro_router = APIRouter(prefix="/pomodoro")

pomodoro_sessions = []

class Pomodoro(BaseModel):
    task_id: int
    duration: int = Field(gt=0, default=25)

def update_pomodoro_sessions(pomodoro_sessions, curr_datetime: datetime):
    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session["completed"]:
            continue

        end_time = datetime.strptime(pomodoro_session["end_time"], "%Y-%m-%d %H:%M:%S.%f")

        if curr_datetime > end_time:
            pomodoro_session["completed"] = True

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
    if not task_exists(pomodoro.task_id):
        raise HTTPException(status_code=404, detail="Task with the given ID doesn't exist")

    curr_datetime = datetime.now()

    update_pomodoro_sessions(pomodoro_sessions, curr_datetime)

    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session["task_id"] != pomodoro.task_id or pomodoro_session["completed"]:
            continue

        raise HTTPException(status_code=409, detail="Pomodoro with the given task ID already exists")

    pomodoro_session = {
        "task_id": pomodoro.task_id,
        "start_time": str(curr_datetime),
        "end_time": str(curr_datetime + timedelta(minutes=pomodoro.duration)),
        "completed": False,
    }

    pomodoro_sessions.append(pomodoro_session)

    return pomodoro_session

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
    curr_datetime = datetime.now()

    update_pomodoro_sessions(pomodoro_sessions, curr_datetime)

    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session["task_id"] != task_id or pomodoro_session["completed"]:
            continue

        pomodoro_session["completed"] = True
        pomodoro_session["end_time"] = str(curr_datetime)

        return pomodoro_session

    raise HTTPException(status_code=404, detail="Active pomodoro with the given task ID doesn't exist")

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
    curr_datetime = datetime.now()

    update_pomodoro_sessions(pomodoro_sessions, curr_datetime)

    stats = {
        task["id"]: 0 for task in tasks
    }

    stats["total_time"] = 0

    for pomodoro_session in pomodoro_sessions:
        if not pomodoro_session["completed"]:
            continue

        task_id = pomodoro_session["task_id"]

        stats[task_id] = stats.get(task_id, 0) + 1

        start_time = datetime.strptime(pomodoro_session["start_time"], "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(pomodoro_session["end_time"], "%Y-%m-%d %H:%M:%S.%f")

        stats["total_time"] += math.floor((end_time - start_time).total_seconds())

    return stats