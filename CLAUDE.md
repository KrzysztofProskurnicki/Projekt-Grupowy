# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PyQt5 desktop password manager (Polish UI/comments mixed with English code). All UI text and code identifiers are in English; some docstrings and user-facing copy are in Polish.

## Running

```powershell
# Install deps. The encrypted vault uses Argon2id from `cryptography` (>=42)
# plus SQLAlchemy 2.x; PyQt5 powers the UI; zxcvbn powers the strength meter.
pip install PyQt5 zxcvbn cryptography SQLAlchemy

# Run the app
python Project/src/main.py
```

The standalone `argon2-cffi` package in `requirements.txt` is NOT needed - we use
`cryptography.hazmat.primitives.kdf.argon2.Argon2id` directly.

A bundled `Project/venv/` exists (Python 3.7). Activate with `Project\venv\Scripts\Activate.ps1` if you want to use it; otherwise any local Python 3.8+ works.

There are no tests, linter config, or build scripts in this repo - just `python Project/src/main.py`.

## Import layout (important)

Modules in `Project/src/` use **flat imports** (`from styles import *`, `from services.password_service import PasswordService`, `from widgets.password_item_widget import ...`). They rely on `src/` being on `sys.path`. Running `python Project/src/main.py` works because Python prepends the script's directory. If you ever invoke modules differently (e.g. `python -m`), you must `cd Project/src` first or imports will fail.

## Architecture

Three-layer split inside `Project/src/`:

1. **Views / windows** (top-level `.py` in `src/`): `main.py` (MainWindow), `login_dialog.py`, `register_dialog.py`, `sidebar.py`, `security_dashboard.py`, `detail_view.py`, `add_password_view.py`. Each view emits Qt signals; MainWindow wires them to services.
2. **Services** (`src/services/`): pure business logic, no Qt. See "Crypto / persistence stack" below for the full breakdown. `PasswordService(username)` is instantiated **per logged-in user**, decrypts that user's entries at construction time and caches them in memory. `AuthenticationService` validates credentials with Argon2id + a SHA256 verifier against the SQLite `users` table.
3. **Widgets** (`src/widgets/`): reusable Qt components (gauges, nav buttons, list items, overlays, notifications).

Models split into two packages:
- `src/models/` (`password.py`, `user.py`) - legacy dataclass scaffolding, currently unused by the active code, which passes around raw dicts (`name`, `email`, `password`, `color`, `weak_password`, `favorite`, `notes`).
- `src/models/db_models.py` - the **SQLAlchemy ORM models** (`User`, `PasswordEntry`) backing the encrypted vault.

### Crypto / persistence stack

The vault is encrypted at rest. The key derivation + symmetric encryption is in
`services/crypto_service.py`; the SQLite layer is in `services/vault_repository.py`.

- **`CryptoManager` singleton** (`crypto_service.crypto_manager`): module-level
  instance. Holds the derived master key in RAM only between login and logout.
  `AuthenticationService.authenticate` calls `unlock(key)`, `logout` calls
  `lock()`. `PasswordService` reads/writes through this singleton - so you must
  not import or use `PasswordService` before a successful authenticate, or
  decryption will raise.
- **Key derivation**: `Argon2id(iterations=4, memory_cost=64MiB, lanes=2)` to a
  32-byte key. Per-user salt (16B) is stored on the `users` row.
- **Verifier**: we store `SHA256(derived_key)` in `users.verifier`. Login
  re-derives the key, hashes it, and compares - never compares passwords or
  keys directly.
- **Encryption**: AES-GCM (`AESGCM(master_key)`) with a fresh 12-byte nonce
  per field. The stored blob format is `nonce || ciphertext` in a single
  `LargeBinary` column. Encrypted fields: `enc_email`, `enc_password`,
  `enc_notes`.
- **Plaintext columns** (`name`, `color`, `favorite`, `weak_password`): kept
  unencrypted so the sidebar, filter logic, and badges work without
  decrypting every row.

### App lifecycle

`run_app()` in `main.py`:
1. Calls `migrate_if_needed()` once on startup (see "Migration" below).
2. Loops: show `LoginDialog`, on success open `MainWindow(username)`, wait for
   logout. `MainWindow._on_logout` calls `AuthenticationService().logout()`
   which **locks the CryptoManager and zeroes the key**, then emits the
   logout signal so `run_app` returns to the login screen.
3. Closing the main window directly (not via the logout button) exits the
   app without locking - acceptable because the process dies and the key
   dies with it.

Preserve this ordering. In particular, anything that needs to decrypt must run
between login and logout.

### Migration

`services/migration.py:migrate_if_needed()` runs at the start of every launch
and is idempotent. If `Project/data/users.json` exists and the DB has zero
users, it walks the old JSON: creates each user with a fresh salt/verifier
derived from their legacy plaintext password, then re-encrypts each entry
with that user's key. On success it renames the file to
`users.json.migrated.bak` so we don't (a) re-run on the same data or
(b) leave plaintext passwords lying around. Don't delete or rewrite the
migration entry point - existing accounts depend on it for the first launch
after a pull.

### View switching

`MainWindow.stacked_widget` holds 7 pages indexed 0-6. The indices are defined in `constants.py` (`VIEW_INDEX_*` and matching `NAV_INDEX_*`). When adding a new page, add a constant rather than hardcoding the int - `main.py:117-147` already mixes both styles, prefer the constants.

### App lifecycle

`run_app()` in `main.py` is a **login/logout loop**: it shows `LoginDialog`, opens `MainWindow(username)` on success, listens for `logout_signal`, and loops back to login. Closing the main window without logout exits the app. Preserve this pattern when modifying auth flow.

### View switching

`MainWindow.stacked_widget` holds 7 pages indexed 0-6. The indices are defined in `constants.py` (`VIEW_INDEX_*` and matching `NAV_INDEX_*`). When adding a new page, add a constant rather than hardcoding the int - `main.py:117-147` already mixes both styles, prefer the constants.

### Data storage

- `Project/data/vault.db`: **the active store**. SQLite database with two tables:
  - `users` (id, username UNIQUE, salt, verifier, created_at)
  - `password_entries` (id, user_id FK, name, color, favorite, weak_password, enc_email, enc_password, enc_notes, created_at)
  Created automatically on first run by `vault_repository.init_db()` via
  `Base.metadata.create_all` (idempotent `CREATE TABLE IF NOT EXISTS`).
- `Project/data/users.json` (LEGACY): the pre-encryption JSON store. Will be
  migrated and renamed to `users.json.migrated.bak` on first launch. If you
  see this file in a working copy after a successful run, something is wrong.
- `Project/data/users.json.migrated.bak`: post-migration backup. Safe to
  delete after verifying the migration worked. **Do not commit this file** -
  it contains the legacy plaintext passwords.
- `Project/config/config.json`: legacy unused. `DataManager` and its
  `master_password` config field are no longer referenced by the active code
  path. Safe to ignore; left in place only because `DataManager` is still
  exported by `services/__init__.py`.

### `Project/baza v1/`

Older CLI prototype using SQLAlchemy + cryptography + argon2 against `sejfy.db`. **Not imported by the PyQt app** and not part of the active codebase - treat it as reference material only. The lingering deps in `requirements.txt` come from here.

## Conventions

- Styling is centralized in `src/styles.py` (`STYLESHEET`) and color/size constants. Many widgets still inline `setStyleSheet(...)` strings - matches the existing pattern, don't refactor unless asked.
- Window size is fixed at 1500x1000 minimum (`config.py`). The UI is not designed to be responsive below that.
- Polish docstrings/comments are acceptable and consistent with the existing code; don't translate them wholesale.
