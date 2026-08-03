
from fastapi import Depends
from sqlalchemy.orm import Session
from langgraph.checkpoint.postgres import PostgresSaver
from infrastructure.database import SessionLocal, engine

# 1. Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. LangGraph Checkpointer Dependency
def get_checkpointer():
    # In production, use connection pooling
    with PostgresSaver.from_conn_string("postgresql://user:pass@localhost:5432/db") as saver:
        yield saver