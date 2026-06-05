"""Serwis kryptograficzny - wyprowadzanie klucza Argon2id i szyfrowanie AES-GCM"""

import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Parametry Argon2id - domyślne wartości "złotego standardu".
_ARGON2_ITERATIONS = 4
_ARGON2_MEMORY_COST = 65536  # 64 MiB
_ARGON2_LANES = 2
_KEY_LENGTH = 32  # AES-256
_SALT_LENGTH = 16
_NONCE_LENGTH = 12


class CryptoManager:
    """Przechowuje odblokowany klucz główny w RAM dla bieżącej sesji."""

    def __init__(self) -> None:
        self.master_key: bytes | None = None

    # --- wyprowadzanie klucza ---

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(_SALT_LENGTH)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Wyprowadź 32-bajtowy klucz z password i salt przy użyciu Argon2id"""
        kdf = Argon2id(
            salt=salt,
            length=_KEY_LENGTH,
            iterations=_ARGON2_ITERATIONS,
            memory_cost=_ARGON2_MEMORY_COST,
            lanes=_ARGON2_LANES,
        )
        return kdf.derive(password.encode("utf-8"))

    # --- blokowanie i odblokowywanie sesji ---

    def unlock(self, key: bytes) -> None:
        self.master_key = key

    def lock(self) -> None:
        self.master_key = None

    def is_unlocked(self) -> bool:
        return self.master_key is not None

    # --- szyfrowanie ---

    def encrypt(self, plaintext: str) -> bytes:
        """Zaszyfruj string. Zwraca ``nonce || ciphertext`` jako jeden blob"""
        if not self.master_key:
            raise ValueError("Vault locked - login first.")
        aesgcm = AESGCM(self.master_key)
        nonce = os.urandom(_NONCE_LENGTH)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + ciphertext

    def decrypt(self, blob: bytes) -> str:
        """Odszyfruj blob ``nonce || ciphertext`` utworzony przez :meth:`encrypt`."""
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

crypto_manager = CryptoManager()
