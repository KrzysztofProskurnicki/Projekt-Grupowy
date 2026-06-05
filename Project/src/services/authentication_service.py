"""Serwis uwierzytelniania - logowanie i rejestracja przez SQLite + Argon2id"""

import hashlib
from typing import Optional

from services.crypto_service import crypto_manager
from services import vault_repository


class _AuthState:
    """Stan sesji na poziomie modułu współdzielony przez wszystkie instancje AuthenticationService"""
    current_user_id: Optional[int] = None
    current_username: Optional[str] = None


_state = _AuthState()

vault_repository.init_db()


def _verifier_for(key: bytes) -> bytes:
    return hashlib.sha256(key).digest()


class AuthenticationService:
    """Zarządza uwierzytelnianiem użytkownika i stanem ponownej autoryzacji widoku."""

    def __init__(self) -> None:
        self._view_unlocked: bool = False

    # --- uwierzytelnianie ---
    def authenticate(self, username: str, password: str) -> bool:
        """Zweryfikuj dane logowania i odblokuj sejf po sukcesie."""
        with vault_repository.session_scope() as session:
            user = vault_repository.find_user(session, username)
            if user is None:
                return False

            try:
                derived = crypto_manager.derive_key(password, user.salt)
            except Exception:
                return False

            if _verifier_for(derived) != user.verifier:
                return False

            crypto_manager.unlock(derived)
            _state.current_user_id = user.id
            _state.current_username = user.username
            return True

    def register(self, username: str, password: str) -> bool:
        """Utwórz nowego użytkownika. Zwraca False, jeśli nazwa jest zajęta"""
        with vault_repository.session_scope() as session:
            if vault_repository.find_user(session, username) is not None:
                return False

            salt = crypto_manager.generate_salt()
            derived = crypto_manager.derive_key(password, salt)
            verifier = _verifier_for(derived)
            vault_repository.create_user(
                session, username=username, salt=salt, verifier=verifier
            )
            return True

    def verify_master_password(self, password: str) -> bool:
        """Ponownie zweryfikuj hasło aktualnie zalogowanego użytkownika"""
        if _state.current_user_id is None:
            return False
        with vault_repository.session_scope() as session:
            user = session.get(vault_repository.User, _state.current_user_id)
            if user is None:
                return False
            try:
                derived = crypto_manager.derive_key(password, user.salt)
            except Exception:
                return False
            return _verifier_for(derived) == user.verifier

    def logout(self) -> None:
        """Wyczyść cały stan sesji i usuń klucz główny z RAM"""
        crypto_manager.lock()
        _state.current_user_id = None
        _state.current_username = None
        self._view_unlocked = False

    # --- flaga ponownej autoryzacji widoku ---
    def is_authenticated(self) -> bool:
        return self._view_unlocked

    def set_authenticated(self, status: bool) -> None:
        self._view_unlocked = status

    # --- pomocniki tylko do odczytu ---

    def get_current_user(self) -> Optional[str]:
        return _state.current_username

    def get_current_user_id(self) -> Optional[int]:
        return _state.current_user_id

    def is_vault_unlocked(self) -> bool:
        return crypto_manager.is_unlocked() and _state.current_user_id is not None

    # --- operacje profilu ---

    def get_user_created_at(self):
        """Zwróć date utworzenia bieżącego użytkownika albo None."""
        if _state.current_user_id is None:
            return None
        with vault_repository.session_scope() as session:
            user = vault_repository.get_user_by_id(session, _state.current_user_id)
            return user.created_at if user else None

    def change_master_password(
        self, old_password: str, new_password: str, progress_callback=None
    ) -> bool:
        """Zmień hasło główne: zweryfikuj stare, przeszyfruj wpisy i zaktualizuj dane logowania.

        Argumenty:
            old_password: Bieżące hasło główne używane do weryfikacji.
            new_password: Nowe hasło główne do ustawienia.
            progress_callback: Opcjonalna funkcja callable(int) przyjmująca postęp 0-100%.

        Zwraca:
            True po sukcesie, False jeśli old_password jest błędne.
        """
        if _state.current_user_id is None:
            return False

        # 1. Zweryfikuj stare hasło
        if not self.verify_master_password(old_password):
            return False

        # 2. Wyprowadź nowy klucz
        new_salt = crypto_manager.generate_salt()
        new_key = crypto_manager.derive_key(new_password, new_salt)
        new_verifier = _verifier_for(new_key)

        # 3. Przeszyfruj każdy wpis: odszyfruj starym kluczem, zaszyfruj nowym
        with vault_repository.session_scope() as session:
            entries = vault_repository.list_entries(session, _state.current_user_id)
            total = len(entries)

            for i, entry in enumerate(entries):
                # Odszyfruj bieżącym kluczem
                plain_email = ""
                plain_password = ""
                plain_notes = ""
                try:
                    if entry.enc_email:
                        plain_email = crypto_manager.decrypt(entry.enc_email)
                    if entry.enc_password:
                        plain_password = crypto_manager.decrypt(entry.enc_password)
                    if entry.enc_notes:
                        plain_notes = crypto_manager.decrypt(entry.enc_notes)
                except Exception:
                    pass

                # Zaszyfruj nowym kluczem
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                import os
                aesgcm = AESGCM(new_key)

                def _enc(text):
                    if not text:
                        return None
                    nonce = os.urandom(12)
                    return nonce + aesgcm.encrypt(nonce, text.encode("utf-8"), None)

                vault_repository.update_entry_encrypted_fields(
                    session,
                    entry.id,
                    enc_email=_enc(plain_email),
                    enc_password=_enc(plain_password),
                    enc_notes=_enc(plain_notes),
                )

                if progress_callback and total > 0:
                    progress_callback(int((i + 1) / total * 100))

            # 4. Zaktualizuj dane logowania użytkownika
            vault_repository.update_user_credentials(
                session, _state.current_user_id, new_salt, new_verifier
            )

        # 5. Nowy klucz w pamięci
        crypto_manager.unlock(new_key)

        if progress_callback:
            progress_callback(100)

        return True

    def delete_current_account(self) -> bool:
        """Usuń aktualnie zalogowanego użytkownika i wszystkie jego dane sejfu."""
        if _state.current_user_id is None:
            return False
        with vault_repository.session_scope() as session:
            result = vault_repository.delete_user(session, _state.current_user_id)
        if result:
            crypto_manager.lock()
            _state.current_user_id = None
            _state.current_username = None
            self._view_unlocked = False
        return result

