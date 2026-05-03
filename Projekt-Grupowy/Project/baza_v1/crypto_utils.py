# crypto_utils.py
import os
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoManager:
    def __init__(self):
        # Klucz będzie przechowywany w RAMie po zalogowaniu
        self.master_key: bytes = None

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        ZŁOTY STANDARD: Argon2id.
        Zamienia tekstowe hasło w 32-bajtowy klucz.

        Poprawione parametry dla biblioteki 'cryptography':
        - iterations (zamiast time_cost)
        - lanes (zamiast parallelism)
        """
        kdf = Argon2id(
            salt=salt,
            length=32,  # Klucz AES-256 wymaga 32 bajtów
            iterations=4,  # To jest odpowiednik time_cost
            memory_cost=65536,  # 64 MB pamięci RAM
            lanes=2,  # To jest odpowiednik parallelism (wątki)
        )
        return kdf.derive(password.encode('utf-8'))

    def generate_salt(self) -> bytes:
        """Generuje losową sól (16 bajtów)."""
        return os.urandom(16)

    def encrypt(self, data: str) -> tuple[bytes, bytes]:
        """
        Szyfruje tekst algorytmem AES-GCM.
        Zwraca (szyfrogram, nonce).
        """
        if not self.master_key:
            raise ValueError("Sejf zablokowany! Najpierw podaj hasło.")

        aesgcm = AESGCM(self.master_key)
        nonce = os.urandom(12)  # Unikalny numer jednorazowy

        # Szyfrowanie
        ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        return ciphertext, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes) -> str:
        """
        Odszyfrowuje dane algorytmem AES-GCM.
        """
        if not self.master_key:
            raise ValueError("Sejf zablokowany! Najpierw podaj hasło.")

        aesgcm = AESGCM(self.master_key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception:
            raise ValueError("Błąd deszyfracji: Nieprawidłowy klucz lub uszkodzone dane.")


# Globalna instancja
crypto_manager = CryptoManager()