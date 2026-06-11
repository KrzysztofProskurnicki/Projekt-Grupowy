"""Zmienne constant (stałe) aplikacji"""

# Indeksy widgetu stosu
# (szczegóły wpisu są teraz panelem wewnątrz widoku listy,
#  a formularz dodawania hasła jest modalem - nie mają własnych indeksów)
VIEW_INDEX_PASSWORD_LIST = 0
VIEW_INDEX_SECURITY = 1
VIEW_INDEX_SETTINGS = 2
VIEW_INDEX_PROFILE = 3

# Indeksy nawigacji sidebara
NAV_INDEX_ALL_PASSWORDS = 0
NAV_INDEX_FAVORITES = 1
NAV_INDEX_SECURITY = 2
NAV_INDEX_SETTINGS = 3
NAV_INDEX_PROFILE = 4

# Typy filtrów
FILTER_ALL = 'all'
FILTER_FAVORITES = 'favorites'
FILTER_SECURITY = 'security'

# Komunikaty
MSG_COPIED = "Copied!"
MSG_INCORRECT_PASSWORD = "Invalid username or password"
MSG_ENTER_USERNAME = "Please enter username"
MSG_PASSWORDS_NOT_MATCH = "Passwords do not match"
MSG_USERNAME_TAKEN = "This username is already taken"
MSG_FILL_ALL_FIELDS = "Please fill in all fields"
MSG_ACCOUNT_CREATED = "Account created successfully!"

# Komunikaty profilu
MSG_PASSWORD_CHANGED = "Master password changed successfully!"
MSG_ACCOUNT_DELETED = "Account deleted successfully."
MSG_EXPORT_SUCCESS = "Vault exported successfully!"
MSG_WRONG_CURRENT_PASSWORD = "Current password is incorrect."
MSG_NEW_PASSWORDS_NOT_MATCH = "New passwords do not match."
