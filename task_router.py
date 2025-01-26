from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field
from sqlmodel import select

from db_storage import Task, session
from task_status import Status

class NewTask(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default="", max_length=300)
    status: Status = Status.DO_WYKONANIA

class UpdateTask(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: Status | None = Field(default=None)

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
        return session.exec(select(Task)).all()

    statement = select(Task).where(Task.status == status)
    return session.exec(statement).all()

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
                    "detail": "Task with the given title already exists"
                  }
                }
              }
            }
        }
    }
)
def add_task(task: NewTask):
    found_task = session.exec(select(Task).where(Task.title == task.title)).first()

    if found_task:
        raise HTTPException(status_code=409, detail="Task with the given title already exists")

    new_task = Task(title=task.title, description=task.description, status=task.status)

    session.add(new_task)
    session.commit()

    session.refresh(new_task)

    return new_task.model_dump()

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
                           "detail": "Task with the given ID doesn't exist"
                       }
                   }
               }
           }
       }
   }
)
def get_task_details(task_id: int):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task with the given ID doesn't exist")

    return task

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
                               "detail": "Task with the given ID doesn't exist"
                           }
                       }
                   }
               }
        }
   }
)
def update_task(task_id: int, update_task: UpdateTask):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task with the given ID doesn't exist")

    found_task_title = session.exec(select(Task).where(Task.title == update_task.title)).first()

    if found_task_title:
        raise HTTPException(status_code=409, detail="Task with the given title already exists")

    task.title = update_task.title or task.title
    task.description = update_task.description or task.description
    task.status = update_task.status or task.status

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

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
                           "detail": "Task with the given ID doesn't exist"
                       }
                   }
               }
           }
        }
   }
)
def delete_task(task_id: int):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task with the given ID doesn't exist")

    session.delete(task)
    session.commit()

    return task


