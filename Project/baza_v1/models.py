from datetime import datetime

from sqlalchemy import Boolean, DateTime, LargeBinary, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VaultMetadata(Base):
    __tablename__ = "vault_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    verifier: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)


class PasswordEntry(Base):
    __tablename__ = "password_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    enc_username: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    enc_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    enc_url: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    enc_notes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, default=b"")
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
