"""Cryptographically secure password generator.

Ported from baza v1/generator.py.
"""

import secrets
import string


def generate_strong_password(
    length: int = 16,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a strong random password.

    Guarantees at least one character from every selected class, then fills the
    remainder from the union of all selected classes and shuffles. Uses
    :mod:`secrets` for CSPRNG randomness.
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
        # Ensure we don't produce a shorter password than the guarantees imply.
        chars = chars[:length]
    else:
        for _ in range(length - len(chars)):
            chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
