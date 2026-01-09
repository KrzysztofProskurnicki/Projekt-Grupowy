# db_manager.py
import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, VaultMetadata, PasswordEntry
from crypto_utils import crypto_manager

DB_FILE = "sejfy.db"
# Połączenie z bazą SQLite
engine = create_engine(f"sqlite:///{DB_FILE}")
Session = sessionmaker(bind=engine)


def initialize_database(master_password: str):
    """
    Tworzy strukturę bazy i konfiguruje zabezpieczenia przy pierwszym uruchomieniu.
    """
    if os.path.exists(DB_FILE):
        print("Baza już istnieje!")
        return False

    Base.metadata.create_all(engine)
    session = Session()

    # 1. Sól (Salt) - losowe dane, które sprawiają, że nawet to samo hasło
    # da inny klucz szyfrujący w innej bazie.
    salt = crypto_manager.generate_salt()

    # 2. Wyprowadzenie klucza (Master Key) - to trwa chwilę (Argon2id)
    key = crypto_manager.derive_key(master_password, salt)

    # 3. Weryfikator (Verifier) - Hash klucza master.
    # Dlaczego? Bo nie przechowujemy hasła ani klucza master w bazie.
    # Przechowujemy tylko SHA256(klucz). Przy logowaniu odtworzymy klucz,
    # zrobimy jego hash i porównamy z tym tutaj. Jak pasują -> hasło było dobre.
    verifier = hashlib.sha256(key).digest()

    metadata = VaultMetadata(salt=salt, verifier=verifier)
    session.add(metadata)
    session.commit()
    session.close()

    print("Baza utworzona pomyślnie.")
    return True


def login(password: str) -> bool:
    """
    Weryfikuje hasło i ładuje klucz do pamięci RAM.
    """
    if not os.path.exists(DB_FILE):
        print("Baza nie istnieje. Najpierw ją utwórz.")
        return False

    session = Session()
    meta = session.query(VaultMetadata).first()

    # 1. Próba odtworzenia klucza z podanego hasła i zapisanej soli
    derived_key = crypto_manager.derive_key(password, meta.salt)

    # 2. Sprawdzenie czy klucz jest poprawny (porównanie hashów)
    check_verifier = hashlib.sha256(derived_key).digest()

    if check_verifier == meta.verifier:
        # SUKCES: Klucz jest poprawny.
        # Zapisujemy go w pamięci RAM (w obiekcie crypto_manager).
        # Będzie tam siedział aż do zamknięcia programu.
        crypto_manager.master_key = derived_key
        session.close()
        return True
    else:
        # PORAŻKA: Klucz błędny, nic nie zapisujemy.
        session.close()
        return False


def add_password(title, username, password, url=""):
    """
    Szyfruje dane i zapisuje nowy wpis w bazie.
    """
    session = Session()

    # Szyfrowanie Hasła
    # Funkcja encrypt zwraca: ciphertext (szyfrogram) i nonce (unikalny numer).
    c_pass, n_pass = crypto_manager.encrypt(password)

    # PAKOWANIE: Sklejamy Nonce + Ciphertext w jeden ciąg bajtów.
    # Standardowo Nonce dla AES-GCM to 12 bajtów.
    # Dzięki temu w bazie w jednej kolumnie mamy wszystko co potrzebne do odszyfrowania.
    stored_pass = n_pass + c_pass

    # Szyfrowanie Loginu (to samo podejście)
    c_user, n_user = crypto_manager.encrypt(username)
    stored_user = n_user + c_user

    entry = PasswordEntry(
        title=title,
        enc_username=stored_user,
        enc_password=stored_pass,
        # Pole nonce w modelu stało się zbędne, bo dokleiliśmy je do danych wyżej.
        # Zostawiamy puste bajty, żeby baza nie krzyczała błędami.
        nonce=b'',
        enc_url=b''
    )
    session.add(entry)
    session.commit()
    session.close()
    print(f"Dodano hasło dla {title}")


def get_all_passwords():
    """
    Pobiera wszystkie wpisy i odszyfrowuje je w locie.
    """
    session = Session()
    entries = session.query(PasswordEntry).all()

    results = []
    for entry in entries:
        try:
            # Rozpakowanie Loginu
            # Wiemy, że pierwsze 12 bajtów to zawsze Nonce
            user_nonce = entry.enc_username[:12]
            user_cipher = entry.enc_username[12:]
            dec_user = crypto_manager.decrypt(user_cipher, user_nonce)

            # Rozpakowanie Hasła
            pass_nonce = entry.enc_password[:12]
            pass_cipher = entry.enc_password[12:]
            dec_pass = crypto_manager.decrypt(pass_cipher, pass_nonce)

            results.append(f"{entry.title} | Login: {dec_user} | Hasło: {dec_pass}")
        except Exception:
            results.append(f"{entry.title} | BŁĄD ODSZYFROWANIA (Uszkodzone dane?)")

    session.close()
    return results