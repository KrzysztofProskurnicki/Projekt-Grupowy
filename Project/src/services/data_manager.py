"""Data Manager - obsługa operacji I/O na plikach JSON."""

import json
from typing import List, Dict, Any, Optional
from config import USERS_FILE, CONFIG_FILE


class DataManager:
    """Zarządza odczytem/zapisem danych do plików JSON."""
    
    # --- Konfiguracja ---
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Załaduj konfigurację z pliku JSON."""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    @staticmethod
    def save_config(data: Dict[str, Any]) -> None:
        """Zapisz konfigurację do pliku JSON."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def get_master_password() -> str:
        """Pobierz hasło główne z konfiguracji."""
        config = DataManager.load_config()
        return config.get('master_password', 'admin')
    
    # --- Zarządzanie profilami użytkowników ---
    
    @staticmethod
    def load_users() -> List[Dict[str, Any]]:
        """Załaduj listę użytkowników z pliku JSON"""
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def save_users(data: List[Dict[str, Any]]) -> None:
        """Zapisz listę użytkowników do pliku JSON"""
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def find_user(username: str) -> Optional[Dict[str, Any]]:
        """Wyszukaj użytkownika po nazwie.
        
        Args:
            username: Nazwa użytkownika do wyszukania.
            
        Returns:
            Słownik użytkownika lub None jeśli nie znaleziono.
        """
        users = DataManager.load_users()
        for user in users:
            if user.get('user_name') == username:
                return user
        return None
    
    @staticmethod
    def register_user(username: str, password: str) -> bool:
        """Zarejestruj nowego użytkownika z pustą listą haseł
        
        Args:
            username: Nazwa nowego użytkownika.
            password: Hasło nowego użytkownika.
            
        Returns:
            True jeśli rejestracja się powiodła, False jeśli użytkownik już istnieje.
        """
        if DataManager.find_user(username) is not None:
            return False
        
        users = DataManager.load_users()
        users.append({
            'user_name': username,
            'password': password,
            'passwords': []
        })
        DataManager.save_users(users)
        return True
    
    # --- Zarządzanie hasłami per user ---
    
    @staticmethod
    def load_user_passwords(username: str) -> List[Dict[str, Any]]:
        """Załaduj hasła przypisane do konkretnego użytkownika.
        
        Args:
            username: Nazwa użytkownika.
            
        Returns:
            Lista słowników z hasłami użytkownika.
        """
        user = DataManager.find_user(username)
        if user is None:
            return []
        return user.get('passwords', [])
    
    @staticmethod
    def save_user_passwords(username: str, passwords: List[Dict[str, Any]]) -> None:
        """Zapisz hasła użytkownika do pliku users.json.
        
        Args:
            username: Nazwa użytkownika.
            passwords: Lista słowników z hasłami do zapisania.
        """
        users = DataManager.load_users()
        for user in users:
            if user.get('user_name') == username:
                user['passwords'] = passwords
                break
        DataManager.save_users(users)
