# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PyQt5 desktop password manager. UI text and code identifiers are in English; docstrings and some comments are in Polish (acceptable and consistent - do not translate wholesale).

## Running

```powershell
# Install deps. Encryption uses Argon2id from `cryptography` (>=42) + AES-GCM,
# SQLAlchemy 2.x for persistence, PyQt5 for UI, zxcvbn for the strength meter.
pip install PyQt5 zxcvbn cryptography SQLAlchemy

# Run the app (must be run as a script so Python puts src/ on sys.path)
python Project/src/main.py
```

`Project/requirements.txt` is a frozen `pip freeze` (includes transitive deps like
`argon2-cffi`, `cffi`, `greenlet`). The app does NOT use the standalone
`argon2-cffi` package - it derives keys via
`cryptography.hazmat.primitives.kdf.argon2.Argon2id` directly. A bundled
`Project/venv/` (Python 3.7) exists; any local Python 3.8+ works (`bytes | None`
type hints in `crypto_service.py` require 3.10+).

There are no tests, linter config, or build scripts - just run `main.py`.

## Import layout (important)

Modules in `Project/src/` use **flat imports** (`from styles import *`,
`from services.password_service import PasswordService`). They rely on `src/`
being on `sys.path`, which only happens because Python prepends the script's
directory when you run `python Project/src/main.py`. Running modules any other
way (e.g. `python -m`) breaks imports unless you first `cd Project/src`.

## Architecture

Three layers inside `Project/src/`:

1. **Views / windows** (top-level `.py` in `src/`): `main.py` (MainWindow),
   `login_dialog.py`, `register_dialog.py`, `sidebar.py`, `security_dashboard.py`,
   `detail_view.py`, `add_password_view.py`, `settings_view.py`, `profile_view.py`.
   Each view emits Qt signals; MainWindow wires them to services.
2. **Services** (`src/services/`): pure business logic, no Qt. See "Crypto /
   persistence stack" below.
3. **Widgets** (`src/widgets/`): reusable Qt components (gauges, nav buttons,
   list items, overlays, notifications).

Models split into two packages:
- `src/models/` (`password.py`, `user.py`) - legacy dataclass scaffolding,
  unused by the active code, which passes around raw dicts (`name`, `email`,
  `password`, `notes`, `color`, `weak_password`, `favorite`).
- `src/models/db_models.py` - the **SQLAlchemy ORM models** (`User`,
  `PasswordEntry`) backing the encrypted vault.

### Crypto / persistence stack

The vault is encrypted at rest. Key derivation + symmetric encryption live in
`services/crypto_service.py`; the SQLite layer in `services/vault_repository.py`.

- **`CryptoManager` singleton** (`crypto_service.crypto_manager`): module-level
  instance holding the derived master key in RAM only between login and logout.
  `AuthenticationService.authenticate` calls `unlock(key)`, `logout` calls
  `lock()`. `PasswordService` and any decrypt path read through this singleton -
  so do **not** instantiate/use `PasswordService` before a successful
  `authenticate`, or decryption raises `"Vault locked"`.
- **Key derivation**: `Argon2id(iterations=4, memory_cost=64MiB, lanes=2)` to a
  32-byte key. Per-user 16-byte salt stored on the `users` row.
- **Verifier**: `users.verifier` stores `SHA256(derived_key)`. Login re-derives
  the key, hashes it, and compares - it never compares passwords or keys directly.
- **Encryption**: AES-GCM with a fresh 12-byte nonce per field. Stored blob is
  `nonce || ciphertext` in one `LargeBinary` column. Encrypted fields:
  `enc_email`, `enc_password`, `enc_notes`.
- **Plaintext columns** (`name`, `color`, `favorite`, `weak_password`): kept
  unencrypted so the sidebar, filters, and badges work without decrypting rows.

`PasswordService(username)` is instantiated **per logged-in user**: it resolves
the user id, then decrypts that user's entries into an in-memory `_cache` of
dicts at construction. `save_passwords()` is a no-op kept for backward compat -
writes go straight through `vault_repository` and update `_cache` in place.

### Auth, profile, and re-encryption

`AuthenticationService` is stateless-per-instance but shares module-level session
state (`_state.current_user_id/current_username`). Beyond login/register/logout it
owns the **profile operations**:
- `change_master_password(old, new, progress_callback)`: verifies the old
  password, derives a new key/salt, then **decrypts every entry with the old key
  and re-encrypts with the new** before swapping the user's salt/verifier and the
  in-RAM key. `ProfileView` runs this on a `ChangePasswordWorker(QThread)` with a
  progress bar - keep it off the UI thread.
- `delete_current_account()`: cascades delete of the user and all entries, then
  locks the vault.

`PasswordService.export_to_csv()` writes **decrypted** name/email/password rows -
`ProfileView` exposes it as "Export Vault".

### Settings + theming

`services/settings_service.py:SettingsService` is a **singleton** persisting to
`Project/config/settings.json` with validation. Keys: `auto_lock_minutes`,
`clipboard_clear_seconds`, `theme` (`dark`/`light`), `font_size` (10-22).

Theming is unusual: `styles.py` keeps the active palette as **module-level
globals** (`DARK_BG`, `CARD_BG`, `TEXT_PRIMARY`, ...). `styles.apply_theme(name)`
**rebinds those globals** in place and `get_stylesheet(theme)` returns the
QApplication stylesheet. Because globals are rebound, any widget that captured a
color into an inline `setStyleSheet(...)` string at build time will NOT update on
theme change - views implement a `refresh_theme()` that rebuilds their UI, and
`MainWindow._refresh_all_views()` calls it on every view plus `refresh_list()`.
When adding a themed view, add a `refresh_theme()` method and include it in that
loop (`main.py:228-230`).

`MainWindow` also drives two security timers from settings:
- **Auto-lock**: a `QTimer` reset by an app-wide `eventFilter` on key/mouse
  activity; firing calls `_on_logout()` (locks the vault).
- **Clipboard clear**: a single-shot timer started on clipboard change that
  wipes the clipboard after `clipboard_clear_seconds`.

### App lifecycle

`run_app()` in `main.py`:
1. `migrate_if_needed()` once on startup (see Migration).
2. Loads settings, applies font + theme to the `QApplication`.
3. Loops: show `LoginDialog`; on success open `MainWindow(username)`; wait for
   `logout_signal`, then loop back to login. `MainWindow._on_logout` removes the
   event filter, stops the auto-lock timer, calls `AuthenticationService().logout()`
   (**locks CryptoManager, zeroes the key**), emits the signal, and closes.
4. Closing the main window directly (not via logout) exits the app without
   locking - acceptable because the process dies and the key dies with it.

Preserve this ordering: anything that decrypts must run between login and logout.

### Migration

`services/migration.py:migrate_if_needed()` runs at every launch and is
idempotent. If `Project/data/users.json` exists and the DB has zero users, it
walks the old JSON, creates each user with a fresh salt/verifier from their legacy
plaintext password, and re-encrypts each entry with that user's key. On success it
renames the file to `users.json.migrated.bak`. Don't delete or rewrite this entry
point - existing accounts depend on it for the first launch after a pull.

### View switching

`MainWindow.stacked_widget` holds 7 pages. Indices 0-5 are defined in
`constants.py` (`VIEW_INDEX_*`, with matching `NAV_INDEX_*` for the sidebar):
0 list, 1 detail, 2 security, 3 vault (a "Coming Soon" placeholder), 4 settings,
5 profile. The **add-password form is index 6**, reached only via the header
"+ Add" button and still hardcoded (`show_add_form`, `main.py`). Prefer adding a
constant over hardcoding when you touch this.

### Data storage

- `Project/data/vault.db`: **the active store**. SQLite, two tables:
  - `users` (id, username UNIQUE, salt, verifier, created_at)
  - `password_entries` (id, user_id FK, name, color, favorite, weak_password,
    enc_email, enc_password, enc_notes, created_at)
  Created on first run by `vault_repository.init_db()` (idempotent).
- `Project/config/settings.json`: app settings (auto-lock, clipboard, theme,
  font). Auto-created with defaults if missing.
- `Project/data/users.json` (LEGACY): pre-encryption JSON store, migrated and
  renamed to `users.json.migrated.bak` on first launch.
- `Project/config/config.json`: legacy/unused. `DataManager` and its
  `master_password` field are no longer on the active path; left only because
  `DataManager` is still exported by `services/__init__.py`.

> **Data files are currently tracked in git.** `vault.db` and
> `users.json.migrated.bak` were committed upstream. They contain real vault data
> (and the `.bak` holds legacy plaintext passwords), and they cause "untracked
> working tree files would be overwritten by merge" failures on pull. Treat them
> as data, not code - prefer gitignoring/untracking them rather than committing
> local changes to them.

### `Project/baza v1/`

(Removed upstream.) Was an older standalone CLI prototype, never imported by the
PyQt app. If you see references to it, treat as historical.

## Conventions

- Styling is centralized in `src/styles.py` (`STYLESHEET`, color/size constants,
  `apply_theme`/`get_stylesheet`). Many widgets still inline `setStyleSheet(...)` -
  matches the existing pattern; don't refactor unless asked, but remember inline
  strings won't react to theme changes without a `refresh_theme()`.
- Window size fixed at 1500x1000 (`config.py`); the UI isn't responsive below that.
- No em-dashes or en-dashes in docs - use plain hyphens.
