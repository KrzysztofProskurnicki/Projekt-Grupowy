"""Jednorazowa migracja ze starego ``users.json`` do szyfrowanego sejfu SQLite"""

import hashlib
import json
import os
from typing import Any, Dict, List

from config import USERS_FILE
from services.crypto_service import crypto_manager
from services import vault_repository


def _migrate_user(session, raw_user: Dict[str, Any]) -> None:
    username = raw_user.get("user_name", "").strip()
    password = raw_user.get("password", "")
    if not username:
        return
    if vault_repository.find_user(session, username) is not None:
        return

    salt = crypto_manager.generate_salt()
    key = crypto_manager.derive_key(password, salt)
    verifier = hashlib.sha256(key).digest()
    user = vault_repository.create_user(
        session, username=username, salt=salt, verifier=verifier
    )

    previous_key = crypto_manager.master_key
    crypto_manager.unlock(key)
    try:
        for raw_entry in raw_user.get("passwords", []) or []:
            _migrate_entry(session, user.id, raw_entry)
    finally:
        if previous_key is None:
            crypto_manager.lock()
        else:
            crypto_manager.unlock(previous_key)


def _migrate_entry(session, user_id: int, raw: Dict[str, Any]) -> None:
    name = raw.get("name", "").strip()
    if not name:
        return
    email = raw.get("email", "") or ""
    password = raw.get("password", "") or ""
    notes = raw.get("notes", "") or ""
    color = raw.get("color", "#333333")
    favorite = bool(raw.get("favorite", False))
    weak = bool(raw.get("weak_password", False))

    enc_email = crypto_manager.encrypt(email) if email else None
    enc_password = crypto_manager.encrypt(password) if password else None
    enc_notes = crypto_manager.encrypt(notes) if notes else None

    vault_repository.add_entry(
        session,
        user_id=user_id,
        name=name,
        color=color,
        favorite=favorite,
        weak_password=weak,
        enc_email=enc_email,
        enc_password=enc_password,
        enc_notes=enc_notes,
    )


def migrate_if_needed() -> bool:
    """Uruchom migrację. Zwraca True, jeśli dane zostały zmigrowane, inaczej False"""
    if not os.path.exists(USERS_FILE):
        return False

    vault_repository.init_db()

    with vault_repository.session_scope() as session:
        if vault_repository.count_users(session) > 0:
            return False

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as fh:
            raw_users: List[Dict[str, Any]] = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False

    if not raw_users:
        return False

    with vault_repository.session_scope() as session:
        for raw_user in raw_users:
            _migrate_user(session, raw_user)

    backup_path = USERS_FILE + ".migrated.bak"
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(USERS_FILE, backup_path)
    except OSError:
        # Dane migracji są już w bazie; nieudana zmiana nazwy starego pliku
        pass

    return True
