from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import JSON
from sqlalchemy import DateTime
from datetime import datetime
from database import Base

# JOB TABLE
class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(200))
    description = Column(Text)
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    # Changed from String(100) to Text
    experience = Column(Text)
    education = Column(Text)

# CANDIDATE TABLE

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    skills = Column(JSON)
    # Changed from String(100) to Text
    experience = Column(Text)
    # Changed from String(200) to Text
    education = Column(Text)
    projects = Column(JSON)
    certifications = Column(JSON)
    resume_filename = Column(String(300))

# SCREENING TABLE
class Screening(Base):
    __tablename__ = "screenings"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)
    candidate_id = Column(Integer)
    match_percentage = Column(Float)
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    explanation = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )