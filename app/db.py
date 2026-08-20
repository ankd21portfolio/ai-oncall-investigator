from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import config
from app.models import Base

# Create engine from Postgres URL
engine = create_engine(config.POSTGRES_URL)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)