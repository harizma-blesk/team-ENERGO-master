from sqlalchemy import Column, Integer, String, Time, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class AuditoryNote(Base):
    __tablename__ = 'auditory'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    corpus = Column(String)
    category = Column(String)

class AuditoryJournalNote(Base):
    __tablename__ = 'auditory_journal'

    id = Column(Integer, primary_key=True)
    aud_id = Column(Integer)
    startTime = Column(DateTime, default=datetime.now)
    endTime = Column(DateTime, default=datetime.now)
    duration = Column(Integer)
    dayOfWeek = Column(Integer)
    timeStatus = Column(Integer)

class CameraCabJournalNote(Base):
    __tablename__ = 'camera_cab_journal'

    id = Column(Integer, primary_key=True)
    camera_ip = Column(String)
    id_cab = Column(Integer)
    login_camera = Column(String)
    password_camera = Column(String)
    port_camera = Column(String)
    is_busy = Column(Integer, default=0)

class FindCabinetReq:
    def __init__(self, time_part, auditory):
        self.timePart = time_part
        self.auditory = auditory

class TimePart:
    def __init__(self, start_time, end_time, day_of_week, duration):
        self.startTime = start_time
        self.endTime = end_time
        self.dayOfWeek = day_of_week
        self.duration = duration