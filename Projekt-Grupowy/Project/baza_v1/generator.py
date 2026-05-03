import secrets
import string

def generate_strong_password(
        length=16,
        use_upper=True,
        use_digits=True,
        use_symbols=True
) -> str:
    """
    Generuje kryptograficznie bezpieczne hasło.
    Gwarantuje wystąpienie co najmniej jednego znaku z każdej wybranej grupy.
    """

    # 1. Definiujemy zestawy znaków
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase if use_upper else ""
    digits = string.digits if use_digits else ""
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?" if use_symbols else ""

    all_chars = lowercase + uppercase + digits + symbols

    if not all_chars:
        raise ValueError("Musisz wybrać co najmniej jeden typ znaków!")

    # 2. Gwarancja minimalnych wymagań
    password_chars = [secrets.choice(lowercase)]  # Zawsze co najmniej jedna mała

    if use_upper:
        password_chars.append(secrets.choice(uppercase))
    if use_digits:
        password_chars.append(secrets.choice(digits))
    if use_symbols:
        password_chars.append(secrets.choice(symbols))

    # 3. Dopełnianie reszty długości losowymi znakami ze wszystkich zbiorów
    remaining_length = length - len(password_chars)
    for _ in range(remaining_length):
        password_chars.append(secrets.choice(all_chars))

    # 4. Mieszanie (Shuffle)
    # Lista jest obecnie w kolejności, trzeba to wymieszać.
    # Używamy SystemRandom do tasowania.
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)