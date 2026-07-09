from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Import all models here so Alembic autogenerate can discover them.
from app.models.user import User  # noqa: E402, F401
