"""Plik konfiguracji"""

import os

# Pobierz katalog bazowy (folder src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# Utwórz folder 'data', jeśli nie istnieje
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Utwórz folder 'config', jeśli nie istnieje
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Szyfrowana baza sejfu (SQLite)
DB_FILE = os.path.join(DATA_DIR, 'vault.db')

# Ustawienia aplikacji
WINDOW_TITLE = "Password Manager"
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
WINDOW_MIN_WIDTH = 1500
WINDOW_MIN_HEIGHT = 1000

# Ustawienia fontu
FONT_FAMILY_WINDOWS = "Segoe UI"
FONT_FAMILY_OTHER = "Helvetica Neue"
FONT_SIZE_DEFAULT = 14
