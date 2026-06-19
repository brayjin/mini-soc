from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)

    timestamp = Column(String)

    ip = Column(String)

    type = Column(String)

    status = Column(String)

    attempts = Column(Integer, nullable=True)


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True)

    ip = Column(String, unique=True)
