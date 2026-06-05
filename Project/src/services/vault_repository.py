"""Repozytorium sejfu - warstwa trwałego zapisu SQLite + SQLAlchemy"""

from contextlib import contextmanager
from typing import Iterator, List, Optional

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker

from config import DB_FILE
from models.db_models import Base, User, PasswordEntry


_engine = create_engine(f"sqlite:///{DB_FILE}", future=True)
_SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def init_db() -> None:
    """Utwórz tabele, jeśli jeszcze nie istnieję"""
    Base.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- Zapytania użytkowników ---

def find_user(session: Session, username: str) -> Optional[User]:
    return session.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def create_user(session: Session, username: str, salt: bytes, verifier: bytes) -> User:
    user = User(username=username, salt=salt, verifier=verifier)
    session.add(user)
    session.flush()
    return user


def count_users(session: Session) -> int:
    return session.execute(select(func.count(User.id))).scalar_one()


# --- Zapytania wpisów ---

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


# --- modyfikacje użytkowników ---

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def update_user_credentials(
    session: Session, user_id: int, new_salt: bytes, new_verifier: bytes
) -> None:
    """Zaktualizuj salt i verifier użytkownika po zmianie hasła głównego"""
    user = session.get(User, user_id)
    if user is not None:
        user.salt = new_salt
        user.verifier = new_verifier


def delete_user(session: Session, user_id: int) -> bool:
    """Usuń użytkownika i wszystkie jego wpisy (kaskadowo). Zwraca True po sukcesie."""
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
    """Zaktualizuj szyfrowane pola pojedynczego wpisu"""
    entry = session.get(PasswordEntry, entry_id)
    if entry is not None:
        entry.enc_email = enc_email
        entry.enc_password = enc_password
        entry.enc_notes = enc_notes

