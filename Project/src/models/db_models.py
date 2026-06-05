"""Modele ORM SQLAlchemy dla szyfrowanego sejfu"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, LargeBinary, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    verifier: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    entries: Mapped[List["PasswordEntry"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PasswordEntry(Base):
    __tablename__ = "password_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Dane jawne (potrzebne do listowania, filtrowania i odznak sidebara).
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False, default="#333333")
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weak_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Szyfrowane bloby: nonce(12B) || ciphertext
    enc_email: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    enc_password: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    enc_notes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="entries")
