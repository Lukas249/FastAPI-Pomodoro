import os
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from models.task import Task
from models.pomodoro_session import Pomodoro_Session

if os.getenv("ENVIRONMENT") == "production":
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

session = Session(engine)