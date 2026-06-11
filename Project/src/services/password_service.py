"""Serwis haseł - operacje CRUD dla użytkownika na szyfrowanym sejfie SQLite"""

from typing import Any, Dict, List, Optional

from services.crypto_service import crypto_manager
from services.security_service import SecurityService
from services import vault_repository


class PasswordService:

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

    # --- ładowanie ---

    def load_passwords(self) -> None:
        """Załaduj i odszyfruj wpisy bieżącego użytkownika do cache w pamięci."""
        if self._user_id is None:
            self._cache = []
            return

        with vault_repository.session_scope() as session:
            entries = vault_repository.list_entries(session, self._user_id)
            self._cache = [self._entry_to_dict(e) for e in entries]

    def save_passwords(self) -> None:  # zachowane dla kompatybilności wstecznej
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
        password = self._decrypt_optional(entry.enc_password)
        # Siła liczona na żywo z odszyfrowanego hasła (zxcvbn), nie z bazy -
        # dzięki temu zmiana algorytmu oceny działa też dla starych wpisów
        ev = SecurityService.evaluate_password(password)
        return {
            "name": entry.name,
            "email": self._decrypt_optional(entry.enc_email),
            "password": password,
            "notes": self._decrypt_optional(entry.enc_notes),
            "color": entry.color,
            "weak_password": ev["level"] == "weak",
            "strength": ev["level"],
            "pw_score": ev["score"],
            "dictionary": ev["dictionary"],
            "favorite": entry.favorite,
        }

    # --- API odczytu ---

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

    # --- API zapisu ---

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
        """Zaszyfruj i utrwal nowy wpis"""
        if self._user_id is None:
            return

        name = password_data.get("name", "")
        email = password_data.get("email", "")
        password = password_data.get("password", "")
        notes = password_data.get("notes", "")
        color = password_data.get("color", "#333333")
        favorite = bool(password_data.get("favorite", False))
        ev = SecurityService.evaluate_password(password)
        weak = ev["level"] == "weak"

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
            "strength": ev["level"],
            "pw_score": ev["score"],
            "dictionary": ev["dictionary"],
            "favorite": favorite,
        })

    def update_password(self, original_name: str, password_data: Dict[str, Any]) -> bool:
        """Zaszyfruj i utrwal edytowany wpis (status ulubionego zostaje)."""
        if self._user_id is None:
            return False

        name = password_data.get("name", "")
        email = password_data.get("email", "")
        password = password_data.get("password", "")
        notes = password_data.get("notes", "")
        color = password_data.get("color", "#333333")
        ev = SecurityService.evaluate_password(password)
        weak = ev["level"] == "weak"

        enc_email = crypto_manager.encrypt(email) if email else None
        enc_password = crypto_manager.encrypt(password) if password else None
        enc_notes = crypto_manager.encrypt(notes) if notes else None

        with vault_repository.session_scope() as session:
            updated = vault_repository.update_entry(
                session,
                self._user_id,
                original_name,
                name=name,
                color=color,
                weak_password=weak,
                enc_email=enc_email,
                enc_password=enc_password,
                enc_notes=enc_notes,
            )
        if not updated:
            return False

        for entry in self._cache:
            if entry["name"] == original_name:
                entry.update({
                    "name": name,
                    "email": email,
                    "password": password,
                    "notes": notes,
                    "color": color,
                    "weak_password": weak,
                    "strength": ev["level"],
                    "pw_score": ev["score"],
                    "dictionary": ev["dictionary"],
                })
                break
        return True

    # --- eksport ---

    def export_to_csv(self, filepath: str) -> None:
        """Wyeksportuj wszystkie odszyfrowane hasła do pliku CSV (name, email, password)"""
        import csv

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Email", "Password"])
            for entry in self._cache:
                writer.writerow([
                    entry.get("name", ""),
                    entry.get("email", ""),
                    entry.get("password", ""),
                ])

