"""Vault repository - SQLite + SQLAlchemy persistence layer.

Knows nothing about encryption. Higher-level services (AuthenticationService,
PasswordService) handle key derivation / AES-GCM and pass us blobs.
"""

from contextlib import contextmanager
from typing import Iterator, List, Optional

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker

from config import DB_FILE
from models.db_models import Base, User, PasswordEntry


_engine = create_engine(f"sqlite:///{DB_FILE}", future=True)
_SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- user queries ---

def find_user(session: Session, username: str) -> Optional[User]:
    return session.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def create_user(session: Session, username: str, salt: bytes, verifier: bytes) -> User:
    user = User(username=username, salt=salt, verifier=verifier)
    session.add(user)
    session.flush()  # populate user.id
    return user


def count_users(session: Session) -> int:
    return session.execute(select(func.count(User.id))).scalar_one()


# --- entry queries ---

def list_entries(session: Session, user_id: int) -> List[PasswordEntry]:
    return list(session.execute(
        select(PasswordEntry).where(PasswordEntry.user_id == user_id).order_by(PasswordEntry.id)
    ).scalars())


def find_entry_by_name(session: Session, user_id: int, name: str) -> Optional[PasswordEntry]:
    return session.execute(
        select(PasswordEntry).where(
            PasswordEntry.user_id == user_id,
            PasswordEntry.name == name,
        )
    ).scalar_one_or_none()


def add_entry(
    session: Session,
    *,
    user_id: int,
    name: str,
    color: str,
    favorite: bool,
    weak_password: bool,
    enc_email: Optional[bytes],
    enc_password: Optional[bytes],
    enc_notes: Optional[bytes],
) -> PasswordEntry:
    entry = PasswordEntry(
        user_id=user_id,
        name=name,
        color=color,
        favorite=favorite,
        weak_password=weak_password,
        enc_email=enc_email,
        enc_password=enc_password,
        enc_notes=enc_notes,
    )
    session.add(entry)
    session.flush()
    return entry


def set_entry_favorite(session: Session, user_id: int, name: str, favorite: bool) -> None:
    entry = find_entry_by_name(session, user_id, name)
    if entry is not None:
        entry.favorite = favorite


def count_entries(session: Session, user_id: int) -> int:
    return session.execute(
        select(func.count(PasswordEntry.id)).where(PasswordEntry.user_id == user_id)
    ).scalar_one()


def count_favorites(session: Session, user_id: int) -> int:
    return session.execute(
        select(func.count(PasswordEntry.id)).where(
            PasswordEntry.user_id == user_id,
            PasswordEntry.favorite.is_(True),
        )
    ).scalar_one()


def count_weak(session: Session, user_id: int) -> int:
    return session.execute(
        select(func.count(PasswordEntry.id)).where(
            PasswordEntry.user_id == user_id,
            PasswordEntry.weak_password.is_(True),
        )
    ).scalar_one()


# --- user mutations ---

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def update_user_credentials(
    session: Session, user_id: int, new_salt: bytes, new_verifier: bytes
) -> None:
    """Update user salt and verifier after a master password change."""
    user = session.get(User, user_id)
    if user is not None:
        user.salt = new_salt
        user.verifier = new_verifier


def delete_user(session: Session, user_id: int) -> bool:
    """Delete a user and all their entries (cascade). Returns True on success."""
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    return True


def update_entry_encrypted_fields(
    session: Session,
    entry_id: int,
    enc_email: Optional[bytes],
    enc_password: Optional[bytes],
    enc_notes: Optional[bytes],
) -> None:
    """Update the encrypted blobs of a single entry (used during re-encryption)."""
    entry = session.get(PasswordEntry, entry_id)
    if entry is not None:
        entry.enc_email = enc_email
        entry.enc_password = enc_password
        entry.enc_notes = enc_notes

