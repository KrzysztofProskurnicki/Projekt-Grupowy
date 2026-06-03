"""Authentication Service - user login/registration backed by SQLite + Argon2id.

Public API is unchanged from the previous JSON-backed version so the UI layer
(LoginDialog, RegisterDialog, DetailView, MasterPasswordOverlay) does not need
to be touched. Internally:

* user credentials -> Argon2id salt + SHA256(key) verifier in the ``users``
  table (no plaintext password is ever stored);
* on successful login the derived key is loaded into the shared
  :data:`crypto_service.crypto_manager` and stays there until logout;
* ``verify_master_password`` re-derives the current user's key and compares it
  to the stored verifier (so the master-password overlay in the detail view
  actually re-validates the logged-in user, not a hardcoded admin password).
"""

import hashlib
from typing import Optional

from services.crypto_service import crypto_manager
from services import vault_repository


class _AuthState:
    """Module-level session state shared by every AuthenticationService instance."""
    current_user_id: Optional[int] = None
    current_username: Optional[str] = None


_state = _AuthState()


# Ensure tables exist as soon as the service module is imported. This is
# idempotent (CREATE TABLE IF NOT EXISTS) so it costs effectively nothing.
vault_repository.init_db()


def _verifier_for(key: bytes) -> bytes:
    return hashlib.sha256(key).digest()


class AuthenticationService:
    """Manages user authentication and per-view re-auth state."""

    def __init__(self) -> None:
        # Per-instance flag preserved for DetailView's "did we already
        # re-prompt for the master password while viewing this entry" UX.
        # Module-level vault unlock state is tracked separately via crypto_manager.
        self._view_unlocked: bool = False

    # --- authentication ---

    def authenticate(self, username: str, password: str) -> bool:
        """Verify credentials and unlock the vault on success."""
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
        """Create a new user. Returns False if the username is taken."""
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
        """Re-verify the currently logged-in user's password.

        Used by :class:`MasterPasswordOverlay` to gate sensitive actions
        (revealing/copying a stored password) inside the detail view.
        """
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
        """Clear all session state and zero the master key in RAM."""
        crypto_manager.lock()
        _state.current_user_id = None
        _state.current_username = None
        self._view_unlocked = False

    # --- per-view re-auth flag (used by DetailView) ---

    def is_authenticated(self) -> bool:
        return self._view_unlocked

    def set_authenticated(self, status: bool) -> None:
        self._view_unlocked = status

    # --- read-only helpers ---

    def get_current_user(self) -> Optional[str]:
        return _state.current_username

    def get_current_user_id(self) -> Optional[int]:
        return _state.current_user_id

    def is_vault_unlocked(self) -> bool:
        return crypto_manager.is_unlocked() and _state.current_user_id is not None

    # --- profile operations ---

    def get_user_created_at(self):
        """Return the creation datetime of the current user, or None."""
        if _state.current_user_id is None:
            return None
        with vault_repository.session_scope() as session:
            user = vault_repository.get_user_by_id(session, _state.current_user_id)
            return user.created_at if user else None

    def change_master_password(
        self, old_password: str, new_password: str, progress_callback=None
    ) -> bool:
        """Change the master password: verify old, re-encrypt all entries, update credentials.

        Args:
            old_password: Current master password for verification.
            new_password: New master password to set.
            progress_callback: Optional callable(int) receiving 0-100 progress %.

        Returns:
            True on success, False if old_password is wrong.
        """
        if _state.current_user_id is None:
            return False

        # 1. Verify old password
        if not self.verify_master_password(old_password):
            return False

        # 2. Derive new key
        new_salt = crypto_manager.generate_salt()
        new_key = crypto_manager.derive_key(new_password, new_salt)
        new_verifier = _verifier_for(new_key)

        # 3. Re-encrypt every entry: decrypt with old key, encrypt with new key
        with vault_repository.session_scope() as session:
            entries = vault_repository.list_entries(session, _state.current_user_id)
            total = len(entries)

            for i, entry in enumerate(entries):
                # Decrypt with current key
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

                # Encrypt with new key
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

            # 4. Update user credentials
            vault_repository.update_user_credentials(
                session, _state.current_user_id, new_salt, new_verifier
            )

        # 5. Switch in-memory key to the new one
        crypto_manager.unlock(new_key)

        if progress_callback:
            progress_callback(100)

        return True

    def delete_current_account(self) -> bool:
        """Delete the currently logged-in user and all their vault data."""
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

