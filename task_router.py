from enum import Enum

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field


class Status(Enum):
    DO_WYKONANIA = "do wykonania"
    W_TRAKCIE = "w trakcie"
    ZAKONCZONE = "zakończone"

tasks = []

class NewTask(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default="", max_length=300)
    status: Status = Status.DO_WYKONANIA

class UpdateTask(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: Status | None = Field(default=None)

def get_new_task_id():
    if len(tasks) == 0:
        return 1

    return tasks[-1]["id"] + 1

def task_exists(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
           return True

    return False

tasks_router = APIRouter(prefix="/tasks")

@tasks_router.get(
    "/",
    responses={
        200: {
            "content": {
               "application/json": {
                   "schema": {
                       "example": [
                          {
                            "id": 1,
                            "title": "Nauka FastAPI",
                            "description": "Przygotować przykładowe API z dokumentacją",
                            "status": "w trakcie",
                          }
                       ]
                   }
               }
            }
       }
    }
)
def get_tasks(status: Status = None):
    if status is None:
        return tasks

    return [task for task in tasks if task["status"].value is status.value]

@tasks_router.post(
    "/",
    responses={
        200: {
            "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "id": 2,
                           "title": "Nowe zadanie",
                           "description": "Przygotować przykładowe API z dokumentacją",
                           "status": "w trakcie"
                      }
                   }
               }
            }
        },
        409: {
            "description": "Task exists",
            "content": {
              "application/json": {
                "schema": {
                  "example": {
                    "detail": "Task with that title already exists"
                  }
                }
              }
            }
        }
    }
)
def add_task(task: NewTask):

    for t in tasks:
        if t["title"] == task.title:
            raise HTTPException(status_code=409, detail="Task with that title already exists")

    task = {
        "id": get_new_task_id(),
        "title": task.title,
        "description": task.description,
        "status": task.status
    }

    tasks.append(task)

    return task

@tasks_router.get(
   "/{task_id}",
   responses={
        200: {
            "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "id": 1,
                           "title": "Nauka FastAPI",
                           "description": "Przygotować przykładowe API z dokumentacją",
                           "status": "w trakcie"
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
                           "detail": "Task with that ID doesn't exist"
                       }
                   }
               }
           }
       }
   }
)
def get_task_details(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task with that ID doesn't exist")


@tasks_router.put(
    "/{task_id}",
    responses={
        200: {
            "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "id": 1,
                           "title": "Zaktualizowany tytuł",
                           "description": "Przygotować przykładowe API z dokumentacją",
                           "status": "w trakcie"
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
                               "detail": "Task with that ID doesn't exist"
                           }
                       }
                   }
               }
        }
   }
)
def update_task(task_id: int, task: UpdateTask):
    updates = {
        "title": task.title,
        "description": task.description,
        "status": task.status
    }

    for task in tasks:
        if task["id"] != task_id:
            continue

        for key, value in updates.items():
            if value is None:
                continue

            task[key] = value

        return task

    raise HTTPException(status_code=404, detail="Task with that ID doesn't exist")

@tasks_router.delete(
    "/{task_id}",
    responses={
        200: {
            "content": {
               "application/json": {
                   "schema": {
                       "example": {
                           "id": 1,
                           "title": "Nauka FastAPI",
                           "description": "Przygotować przykładowe API z dokumentacją",
                           "status": "w trakcie"
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
                           "detail": "Task with that ID doesn't exist"
                       }
                   }
               }
           }
        }
   }
)
def delete_task(task_id: int):
    for i in range(len(tasks)):
        if tasks[i]["id"] == task_id:
            return tasks.pop(i)

    raise HTTPException(status_code=404, detail="Task with that ID doesn't exist")
