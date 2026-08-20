from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.celery_app import test_task
from app.db import create_tables, get_db

app = FastAPI(title="AI On-Call Investigation Assistant")

@app.on_event("startup")
def startup():
    create_tables()
    print("Tables created")

@app.post("/test-publish")
def test_publish(message: str, db: Session = Depends(get_db)):
    task = test_task.delay(message)
    return {"task_id": task.id, "status": "published", "message": message}