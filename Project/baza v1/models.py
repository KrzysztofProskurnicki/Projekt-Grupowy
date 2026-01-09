from datetime import datetime
from sqlalchemy import String, LargeBinary, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class VaultMetadata(Base):
    __tablename__ = "vault_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Sól do KDF
    verifier: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # Hash do sprawdzenia czy hasło master jest OK


class PasswordEntry(Base):
    __tablename__ = "password_entry"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Tytuł trzymamy jawnie dla wygody szukania (można też szyfrować)
    title: Mapped[str] = mapped_column(String, nullable=False)

    # Pola zaszyfrowane (dlatego typ bytes/LargeBinary)
    enc_username: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    enc_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    enc_url: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    # Nonce (Unikalny numer dla każdego szyfrowania - wymagany przez AES-GCM)
    nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())