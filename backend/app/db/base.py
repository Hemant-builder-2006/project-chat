"""
SQLAlchemy base configuration for async ORM.
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
import uuid


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def generate_uuid():
    """Generate a UUID as a string."""
    return str(uuid.uuid4())
