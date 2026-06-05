"""Kryptograficznie bezpieczny generator haseł"""

import secrets
import string

def generate_strong_password(
    length: int = 16,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Wygeneruj silne losowe hasło.

    Gwarantuje co najmniej jeden znak z każdej wybranej klasy, następnie
    wypełnia resztę znakami z sumy wszystkich wybranych klas i miesza wynik.
    Używa :mod:`secrets` jako kryptograficznie bezpiecznego generatora losowego.
    """
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase if use_upper else ""
    digits = string.digits if use_digits else ""
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?" if use_symbols else ""

    all_chars = lowercase + uppercase + digits + symbols
    if not all_chars:
        raise ValueError("At least one character class must be selected.")

    chars = [secrets.choice(lowercase)]
    if use_upper:
        chars.append(secrets.choice(uppercase))
    if use_digits:
        chars.append(secrets.choice(digits))
    if use_symbols:
        chars.append(secrets.choice(symbols))

    if length < len(chars):
        chars = chars[:length]
    else:
        for _ in range(length - len(chars)):
            chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
