"""Data Manager - obsługa operacji I/O na plikach JSON."""

import json
from typing import List, Dict, Any, Optional
from config import DATA_FILE, CONFIG_FILE


class DataManager:
    """Zarządza odczytem/zapisem danych do plików JSON."""
    
    @staticmethod
    def load_passwords() -> List[Dict[str, Any]]:
        """Załaduj hasła z pliku JSON."""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Zwróć pustą listę jeśli błąd
    
    @staticmethod
    def save_passwords(data: List[Dict[str, Any]]) -> None:
        """Zapisz hasła do pliku JSON."""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Załaduj konfigurację z pliku JSON."""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Zwróć pusty dict jeśli błąd
    
    @staticmethod
    def save_config(data: Dict[str, Any]) -> None:
        """Zapisz konfigurację do pliku JSON."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def get_master_password() -> str:
        """Pobierz hasło główne z konfiguracji."""
        config = DataManager.load_config()
        return config.get('master_password', 'admin')  # Domyślnie 'admin'
