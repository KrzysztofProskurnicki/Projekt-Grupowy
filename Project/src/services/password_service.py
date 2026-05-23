"""Password Service - per-user CRUD over the encrypted SQLite vault.

The public surface here is intentionally identical to the previous JSON-backed
implementation so existing UI code (main.py, views, widgets) doesn't have to
change. Internally we delegate persistence to :mod:`vault_repository` and
encryption to the shared :data:`crypto_service.crypto_manager`.

Returned dictionaries match the legacy schema used by the UI:
``{name, email, password, notes, color, weak_password, favorite}``.
"""

from typing import Any, Dict, List, Optional

from services.crypto_service import crypto_manager
from services import vault_repository


class PasswordService:
    """Manages CRUD + filtering for the currently logged-in user's vault."""

    def __init__(self, username: str) -> None:
        self._username = username
        self._user_id: Optional[int] = None
        self._cache: List[Dict[str, Any]] = []
        self._resolve_user_id()
        self.load_passwords()

    def _resolve_user_id(self) -> None:
        with vault_repository.session_scope() as session:
            user = vault_repository.find_user(session, self._username)
            self._user_id = user.id if user is not None else None

    # --- loading ---

    def load_passwords(self) -> None:
        """Load and decrypt the current user's entries into an in-memory cache."""
        if self._user_id is None:
            self._cache = []
            return

        with vault_repository.session_scope() as session:
            entries = vault_repository.list_entries(session, self._user_id)
            self._cache = [self._entry_to_dict(e) for e in entries]

    def save_passwords(self) -> None:  # kept for backwards compatibility
        """No-op: writes happen synchronously inside add_password/toggle_favorite."""
        return

    @staticmethod
    def _decrypt_optional(blob: Optional[bytes]) -> str:
        if blob is None:
            return ""
        try:
            return crypto_manager.decrypt(blob)
        except Exception:
            return ""

    def _entry_to_dict(self, entry) -> Dict[str, Any]:
        return {
            "name": entry.name,
            "email": self._decrypt_optional(entry.enc_email),
            "password": self._decrypt_optional(entry.enc_password),
            "notes": self._decrypt_optional(entry.enc_notes),
            "color": entry.color,
            "weak_password": entry.weak_password,
            "favorite": entry.favorite,
        }

    # --- read API ---

    def get_all_passwords(self) -> List[Dict[str, Any]]:
        return self._cache

    def get_favorites(self) -> List[Dict[str, Any]]:
        return [p for p in self._cache if p.get("favorite", False)]

    def get_weak_passwords(self) -> List[Dict[str, Any]]:
        return [p for p in self._cache if p.get("weak_password", False)]

    def search_passwords(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [
            p for p in self._cache
            if q in p.get("name", "").lower() or q in p.get("email", "").lower()
        ]

    def get_password_count(self) -> int:
        return len(self._cache)

    def get_favorites_count(self) -> int:
        return sum(1 for p in self._cache if p.get("favorite", False))

    def get_weak_count(self) -> int:
        return sum(1 for p in self._cache if p.get("weak_password", False))

    # --- write API ---

    def toggle_favorite(self, name: str, is_favorite: bool) -> None:
        if self._user_id is None:
            return
        with vault_repository.session_scope() as session:
            vault_repository.set_entry_favorite(session, self._user_id, name, is_favorite)
        for entry in self._cache:
            if entry["name"] == name:
                entry["favorite"] = is_favorite
                break

    def add_password(self, password_data: Dict[str, Any]) -> None:
        """Encrypt and persist a new entry. ``password_data`` follows the
        legacy dict shape produced by AddPasswordView (name/email/password/
        notes/color/weak_password/favorite)."""
        if self._user_id is None:
            return

        name = password_data.get("name", "")
        email = password_data.get("email", "")
        password = password_data.get("password", "")
        notes = password_data.get("notes", "")
        color = password_data.get("color", "#333333")
        favorite = bool(password_data.get("favorite", False))
        weak = bool(password_data.get("weak_password", False))

        enc_email = crypto_manager.encrypt(email) if email else None
        enc_password = crypto_manager.encrypt(password) if password else None
        enc_notes = crypto_manager.encrypt(notes) if notes else None

        with vault_repository.session_scope() as session:
            vault_repository.add_entry(
                session,
                user_id=self._user_id,
                name=name,
                color=color,
                favorite=favorite,
                weak_password=weak,
                enc_email=enc_email,
                enc_password=enc_password,
                enc_notes=enc_notes,
            )

        self._cache.append({
            "name": name,
            "email": email,
            "password": password,
            "notes": notes,
            "color": color,
            "weak_password": weak,
            "favorite": favorite,
        })
