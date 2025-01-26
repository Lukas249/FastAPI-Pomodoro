from fastapi import FastAPI

from pomodoro_router import pomodoro_router
from task_router import tasks_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(pomodoro_router)


