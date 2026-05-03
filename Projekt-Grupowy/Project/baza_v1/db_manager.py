import hashlib
import shutil
from datetime import datetime
from pathlib import Path

import zxcvbn
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

try:
    from .crypto_utils import crypto_manager
    from .models import Base, PasswordEntry, VaultMetadata
except ImportError:
    from crypto_utils import crypto_manager
    from models import Base, PasswordEntry, VaultMetadata

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_DIR / "data" / "sejfy.db"
LEGACY_DB_FILE = Path(__file__).resolve().parent / "sejfy.db"

engine = create_engine(f"sqlite:///{DB_FILE}")
Session = sessionmaker(bind=engine)


def ensure_database_file():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DB_FILE.exists() and LEGACY_DB_FILE.exists():
        shutil.copy2(LEGACY_DB_FILE, DB_FILE)


def migrate_schema():
    ensure_database_file()
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    if "password_entry" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("password_entry")}
    migrations = {
        "enc_notes": "ALTER TABLE password_entry ADD COLUMN enc_notes BLOB",
        "color": "ALTER TABLE password_entry ADD COLUMN color VARCHAR",
        "favorite": "ALTER TABLE password_entry ADD COLUMN favorite BOOLEAN NOT NULL DEFAULT 0",
    }

    with engine.begin() as connection:
        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                connection.execute(text(statement))


def vault_exists() -> bool:
    ensure_database_file()
    if not DB_FILE.exists():
        return False

    migrate_schema()
    session = Session()
    try:
        return session.query(VaultMetadata).first() is not None
    finally:
        session.close()


def initialize_database(master_password: str):
    migrate_schema()
    session = Session()
    try:
        if session.query(VaultMetadata).first() is not None:
            return False

        salt = crypto_manager.generate_salt()
        key = crypto_manager.derive_key(master_password, salt)
        crypto_manager.master_key = key
        metadata = VaultMetadata(salt=salt, verifier=hashlib.sha256(key).digest())
        session.add(metadata)
        session.commit()
        return True
    finally:
        session.close()


def reset_vault(master_password: str) -> Path | None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    backup_path = None

    engine.dispose()
    if DB_FILE.exists():
        backup_dir = DB_FILE.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"sejfy_reset_{timestamp}.db"
        shutil.move(str(DB_FILE), str(backup_path))

    crypto_manager.master_key = None
    Base.metadata.create_all(engine)

    session = Session()
    try:
        salt = crypto_manager.generate_salt()
        key = crypto_manager.derive_key(master_password, salt)
        crypto_manager.master_key = key
        metadata = VaultMetadata(salt=salt, verifier=hashlib.sha256(key).digest())
        session.add(metadata)
        session.commit()
        return backup_path
    finally:
        session.close()


def login(password: str) -> bool:
    migrate_schema()
    session = Session()
    try:
        meta = session.query(VaultMetadata).first()
        if meta is None:
            return False

        derived_key = crypto_manager.derive_key(password, meta.salt)
        if hashlib.sha256(derived_key).digest() != meta.verifier:
            return False

        crypto_manager.master_key = derived_key
        return True
    finally:
        session.close()


def is_unlocked() -> bool:
    return crypto_manager.master_key is not None


def _encrypt_packed(data: str) -> bytes:
    ciphertext, nonce = crypto_manager.encrypt(data)
    return nonce + ciphertext


def _decrypt_packed(data: bytes | None) -> str:
    if not data:
        return ""
    nonce = data[:12]
    ciphertext = data[12:]
    return crypto_manager.decrypt(ciphertext, nonce)


def _entry_color(title: str) -> str:
    palette = [
        "#0a84ff",
        "#30d158",
        "#ff9f0a",
        "#ff453a",
        "#bf5af2",
        "#64d2ff",
        "#ffd60a",
        "#5e5ce6",
    ]
    return palette[sum(title.encode("utf-8")) % len(palette)]


def _is_weak(password: str) -> bool:
    try:
        return zxcvbn.zxcvbn(password)["score"] < 3
    except Exception:
        return True


def _to_view_model(entry: PasswordEntry) -> dict:
    password = _decrypt_packed(entry.enc_password)
    username = _decrypt_packed(entry.enc_username)
    url = _decrypt_packed(entry.enc_url)
    notes = _decrypt_packed(entry.enc_notes)
    color = entry.color or _entry_color(entry.title)

    return {
        "id": entry.id,
        "name": entry.title,
        "email": username,
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "color": color,
        "letter": entry.title[:1].upper() if entry.title else "?",
        "favorite": bool(entry.favorite),
        "weak_password": _is_weak(password),
        "created_at": entry.created_at,
    }


def add_password(title, username, password, url="", notes=""):
    if not is_unlocked():
        raise ValueError("Sejf zablokowany. Najpierw podaj haslo glowne.")

    migrate_schema()
    session = Session()
    try:
        clean_title = title.strip()
        entry = PasswordEntry(
            title=clean_title,
            enc_username=_encrypt_packed(username.strip()),
            enc_password=_encrypt_packed(password),
            enc_url=_encrypt_packed(url.strip()),
            enc_notes=_encrypt_packed(notes.strip()),
            nonce=b"",
            color=_entry_color(clean_title),
            favorite=False,
        )
        session.add(entry)
        session.commit()
        return entry.id
    finally:
        session.close()


def get_all_passwords():
    migrate_schema()
    session = Session()
    try:
        entries = session.query(PasswordEntry).order_by(PasswordEntry.title.asc()).all()
        return [_to_view_model(entry) for entry in entries]
    finally:
        session.close()


def update_favorite(entry_id: int, is_favorite: bool):
    migrate_schema()
    session = Session()
    try:
        entry = session.get(PasswordEntry, entry_id)
        if entry is not None:
            entry.favorite = bool(is_favorite)
            session.commit()
    finally:
        session.close()
