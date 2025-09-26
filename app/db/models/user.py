from datetime import datetime
from typing import (
    Optional, List)
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Boolean, Integer, 
    DateTime, JSON, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship)

from app.db.base import (
    Base, BaseModel)


class Users(BaseModel, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    first_name: Mapped[str] = mapped_column(String(255), index=True)
    last_name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String)
    role_id: Mapped[int] = mapped_column(Integer, default=2)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    invited_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    registered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    invited_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    # invited_by_user: Mapped[Optional["Users"]] = relationship(
    #     "Users", 
    #     remote_side="Users.id",
    #     back_populates="invited_users",
    #     foreign_keys=[invited_by]
    # )
    # invited_users: Mapped[List["Users"]] = relationship(
    #     back_populates="invited_by_user",
    #     foreign_keys=[invited_by]
    # )
    