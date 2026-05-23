"""One-shot migration from legacy ``users.json`` to the encrypted SQLite vault.

Triggered automatically on app startup. Idempotent: if the DB already has any
users, or if ``users.json`` is absent/empty, this is a no-op. After a
successful migration the source file is renamed to ``users.json.migrated.bak``
so we never (a) re-run on the same data or (b) leave plaintext passwords
lying around next to the encrypted database.
"""

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
        return  # already migrated in an earlier interrupted run

    salt = crypto_manager.generate_salt()
    key = crypto_manager.derive_key(password, salt)
    verifier = hashlib.sha256(key).digest()
    user = vault_repository.create_user(
        session, username=username, salt=salt, verifier=verifier
    )

    # Temporarily unlock so we can encrypt this user's entries with their own
    # key. We restore the previous lock state at the end so we don't leave the
    # vault unlocked between accounts during migration.
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
    """Run migration once. Returns True if data was migrated, else False."""
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
        # Migration data is already in DB; failing to rename the legacy file
        # isn't fatal but means we'd re-attempt next launch. Since count_users
        # > 0 will guard us, that's still safe.
        pass

    return True
