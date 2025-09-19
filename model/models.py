from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
