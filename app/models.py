import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Investigation(Base):
    __tablename__ = "investigations"

    investigation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    issue_status = Column(String, nullable=False, default="PENDING")
    current_task = Column(String, nullable=True)
    final_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = relationship("InvestigationStep", back_populates="investigation", order_by="InvestigationStep.task_order")


class InvestigationStep(Base):
    __tablename__ = "investigation_steps"

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.investigation_id"), nullable=False)
    task_name = Column(String, nullable=False)
    task_status = Column(String, nullable=False, default="PENDING")
    task_order = Column(Integer, nullable=False)
    result = Column(JSONB, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="steps")