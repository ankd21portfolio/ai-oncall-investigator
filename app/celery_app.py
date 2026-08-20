from celery import Celery
import os
from app import config

app = Celery("oncall_investigator", broker=config.RABBITMQ_URL)

@app.task
def test_task(message: str):
    print(f"Received message: {message}")
    return f"Processed: {message}"