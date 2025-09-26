from datetime import datetime

from sqlalchemy import (
    DateTime, Boolean, func)
from sqlalchemy.orm import (
    declarative_base, DeclarativeBase, 
    Mapped, mapped_column)


# Base = declarative_base()

class Base(DeclarativeBase):
    pass

class  BaseModel:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    # created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # updated_at: Mapped[datetime] = mapped_column(
    #     DateTime, 
    #     default=datetime.utcnow, 
    #     onupdate=datetime.utcnow
    # )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    # Use func.now() for default and onupdate for updated_at
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )