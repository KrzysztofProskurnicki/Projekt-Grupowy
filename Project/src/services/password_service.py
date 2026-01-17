"""Password Service - logika biznesowa operacji na hasłach."""

from typing import List, Dict, Any
from models.password import Password
from services.data_manager import DataManager


class PasswordService:
    """Zarządza operacjami CRUD i filtrowaniem haseł."""
    
    def __init__(self):
        """Inicjalizuj serwis haseł."""
        self.data_manager = DataManager()  # Manager plików JSON
        self._passwords_data: List[Dict[str, Any]] = []  # Cache haseł
        self.load_passwords()  # Załaduj przy starcie
    
    def load_passwords(self) -> None:
        """Load passwords from file."""
        self._passwords_data = self.data_manager.load_passwords()
    
    def save_passwords(self) -> None:
        """Save passwords to file."""
        self.data_manager.save_passwords(self._passwords_data)
    
    def get_all_passwords(self) -> List[Dict[str, Any]]:
        """Get all passwords.
        
        Returns:
            List of all password dictionaries.
        """
        return self._passwords_data
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        """Get only favorite passwords.
        
        Returns:
            List of favorite password dictionaries.
        """
        return [p for p in self._passwords_data if p.get('favorite', False)]
    
    def get_weak_passwords(self) -> List[Dict[str, Any]]:
        """Get only weak passwords.
        
        Returns:
            List of weak password dictionaries.
        """
        return [p for p in self._passwords_data if p.get('weak_password', False)]
    
    def search_passwords(self, query: str) -> List[Dict[str, Any]]:
        """Search passwords by name or email.
        
        Args:
            query: Search query string.
            
        Returns:
            List of matching password dictionaries.
        """
        query_lower = query.lower()
        return [
            p for p in self._passwords_data
            if query_lower in p.get('name', '').lower() 
            or query_lower in p.get('email', '').lower()
        ]
    
    def toggle_favorite(self, name: str, is_favorite: bool) -> None:
        """Toggle favorite status for a password.
        
        Args:
            name: Name of the password entry.
            is_favorite: New favorite status.
        """
        for entry in self._passwords_data:
            if entry['name'] == name:
                entry['favorite'] = is_favorite
                break
        self.save_passwords()
    
    def add_password(self, password_data: Dict[str, Any]) -> None:
        """Add a new password entry.
        
        Args:
            password_data: Dictionary with password information.
        """
        self._passwords_data.append(password_data)
        self.save_passwords()
    
    def get_password_count(self) -> int:
        """Get total password count."""
        return len(self._passwords_data)
    
    def get_favorites_count(self) -> int:
        """Get favorite passwords count."""
        return sum(1 for p in self._passwords_data if p.get('favorite', False))
    
    def get_weak_count(self) -> int:
        """Get weak passwords count."""
        return sum(1 for p in self._passwords_data if p.get('weak_password', False))
