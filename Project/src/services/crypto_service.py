"""Crypto service - Argon2id key derivation + AES-GCM encryption.

Adapted from baza v1/crypto_utils.py. Provides a module-level singleton
``crypto_manager`` that the rest of the app shares; the master key lives
in RAM after login and is cleared on logout.
"""

import os
from typing import Tuple
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Argon2id parameters - "golden standard" defaults.
_ARGON2_ITERATIONS = 4
_ARGON2_MEMORY_COST = 65536  # 64 MiB
_ARGON2_LANES = 2
_KEY_LENGTH = 32  # AES-256
_SALT_LENGTH = 16
_NONCE_LENGTH = 12


class CryptoManager:
    """Holds the unlocked master key in RAM for the current session."""

    def __init__(self) -> None:
        self.master_key: bytes | None = None

    # --- key derivation ---

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(_SALT_LENGTH)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive a 32-byte key from password+salt using Argon2id."""
        kdf = Argon2id(
            salt=salt,
            length=_KEY_LENGTH,
            iterations=_ARGON2_ITERATIONS,
            memory_cost=_ARGON2_MEMORY_COST,
            lanes=_ARGON2_LANES,
        )
        return kdf.derive(password.encode("utf-8"))

    # --- session lock / unlock ---

    def unlock(self, key: bytes) -> None:
        """Store derived key in RAM (call after successful login)."""
        self.master_key = key

    def lock(self) -> None:
        """Clear master key from RAM (call on logout)."""
        self.master_key = None

    def is_unlocked(self) -> bool:
        return self.master_key is not None

    # --- encryption ---

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt a string. Returns ``nonce || ciphertext`` as one blob."""
        if not self.master_key:
            raise ValueError("Vault locked - login first.")
        aesgcm = AESGCM(self.master_key)
        nonce = os.urandom(_NONCE_LENGTH)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + ciphertext

    def decrypt(self, blob: bytes) -> str:
        """Decrypt a ``nonce || ciphertext`` blob produced by :meth:`encrypt`."""
        if not self.master_key:
            raise ValueError("Vault locked - login first.")
        if blob is None or len(blob) < _NONCE_LENGTH:
            raise ValueError("Encrypted blob is too short.")
        aesgcm = AESGCM(self.master_key)
        nonce = blob[:_NONCE_LENGTH]
        ciphertext = blob[_NONCE_LENGTH:]
        try:
            return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception as exc:
            raise ValueError("Decryption failed - wrong key or corrupted data.") from exc


# Shared, app-wide instance. AuthenticationService unlocks it on login,
# PasswordService reads/writes through it, logout clears the key.
crypto_manager = CryptoManager()
