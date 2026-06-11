import json
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(os.path.dirname(_BASE_DIR))
_SETTINGS_FILE = os.path.join(_PROJECT_DIR, 'config', 'settings.json')

_DEFAULTS = {
    'auto_lock_minutes': 0,
    'clipboard_clear_seconds': 0,
    'theme': 'system',
    'accent': 'blue',
    'font_size': 14,
}

_VALID_AUTO_LOCK = (0, 1, 5, 10, 15, 30)
_VALID_CLIPBOARD_CLEAR = (0, 10, 30, 60, 120)
_VALID_THEMES = ('system', 'dark', 'light')
_VALID_ACCENTS = ('blue', 'indigo', 'purple', 'pink', 'orange', 'green')
_FONT_SIZE_MIN = 10
_FONT_SIZE_MAX = 18


class SettingsService:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings: dict = dict(_DEFAULTS)
        self.load()

    def get(self, key: str):
        """Zwróć wartość dla *key* albo wartość domyślną, jeśli klucz jest nieznany"""
        return self._settings.get(key, _DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        """Ustaw *key* na *value* (z walidacją) i zapisz na dysku"""
        value = self._validate(key, value)
        self._settings[key] = value
        self.save()

    def save(self) -> None:
        """Zapisz bieżące ustawienia do pliku JSON"""
        config_dir = os.path.dirname(_SETTINGS_FILE)
        os.makedirs(config_dir, exist_ok=True)
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as fh:
            json.dump(self._settings, fh, indent=4)

    def load(self) -> None:
        """Odczytaj ustawienia z pliku JSON, tworząc domyślne, jeśli plik nie istnieje"""
        if os.path.isfile(_SETTINGS_FILE):
            try:
                with open(_SETTINGS_FILE, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    for key, value in data.items():
                        try:
                            self._settings[key] = self._validate(key, value)
                        except (ValueError, TypeError):
                            self._settings[key] = _DEFAULTS.get(key, value)
            except (json.JSONDecodeError, OSError):
                self._settings = dict(_DEFAULTS)
        else:
            self._settings = dict(_DEFAULTS)
            self.save()

    # --- Właściwości ---

    @property
    def auto_lock_minutes(self) -> int:
        return self.get('auto_lock_minutes')

    @auto_lock_minutes.setter
    def auto_lock_minutes(self, value: int) -> None:
        self.set('auto_lock_minutes', value)

    @property
    def clipboard_clear_seconds(self) -> int:
        return self.get('clipboard_clear_seconds')

    @clipboard_clear_seconds.setter
    def clipboard_clear_seconds(self, value: int) -> None:
        self.set('clipboard_clear_seconds', value)

    @property
    def theme(self) -> str:
        return self.get('theme')

    @theme.setter
    def theme(self, value: str) -> None:
        self.set('theme', value)

    @property
    def accent(self) -> str:
        return self.get('accent')

    @accent.setter
    def accent(self, value: str) -> None:
        self.set('accent', value)

    @property
    def font_size(self) -> int:
        return self.get('font_size')

    @font_size.setter
    def font_size(self, value: int) -> None:
        self.set('font_size', value)

    # --- Walidacja ---

    @staticmethod
    def _validate(key: str, value):
        """Zwraca zwalidowane wartości albo zgłosi ``ValueError``."""
        if key == 'auto_lock_minutes':
            value = int(value)
            if value not in _VALID_AUTO_LOCK:
                raise ValueError(
                    f"auto_lock_minutes must be one of {_VALID_AUTO_LOCK}, got {value}"
                )
        elif key == 'clipboard_clear_seconds':
            value = int(value)
            if value not in _VALID_CLIPBOARD_CLEAR:
                raise ValueError(
                    f"clipboard_clear_seconds must be one of {_VALID_CLIPBOARD_CLEAR}, got {value}"
                )
        elif key == 'theme':
            value = str(value)
            if value not in _VALID_THEMES:
                raise ValueError(
                    f"theme must be one of {_VALID_THEMES}, got {value!r}"
                )
        elif key == 'accent':
            value = str(value)
            if value not in _VALID_ACCENTS:
                raise ValueError(
                    f"accent must be one of {_VALID_ACCENTS}, got {value!r}"
                )
        elif key == 'font_size':
            value = int(value)
            if not (_FONT_SIZE_MIN <= value <= _FONT_SIZE_MAX):
                raise ValueError(
                    f"font_size must be between {_FONT_SIZE_MIN} and {_FONT_SIZE_MAX}, got {value}"
                )
        return value
