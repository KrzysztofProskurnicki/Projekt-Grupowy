"""Configuration file - Paths and application settings."""

import os

# Get base directory (src folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# Data file paths
USERS_FILE = os.path.join(PROJECT_DIR, 'data', 'users.json')
CONFIG_FILE = os.path.join(PROJECT_DIR, 'config', 'config.json')

# Encrypted vault database (SQLite). Lives next to legacy users.json so the
# data/ directory stays the single home for persistent user data.
DB_FILE = os.path.join(PROJECT_DIR, 'data', 'vault.db')

# Application settings
WINDOW_TITLE = "Password Manager UI"
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
WINDOW_MIN_WIDTH = 1500
WINDOW_MIN_HEIGHT = 1000

# Font settings
FONT_FAMILY_WINDOWS = "Segoe UI"
FONT_FAMILY_OTHER = "Helvetica Neue"
FONT_SIZE_DEFAULT = 14
