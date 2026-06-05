"""Model użytkownika - klasa danych reprezentująca profil użytkownika aplikacji"""

from dataclasses import dataclass


@dataclass
class User:
    """Reprezentuje profil użytkownika z danymi logowania"""
    
    user_name: str
    password: str
    authenticated: bool = False
    
    def authenticate(self) -> None:
        """Oznacz użytkownika jako uwierzytelnionego"""
        self.authenticated = True
    
    def logout(self) -> None:
        """Oznacz użytkownika jako wylogowanego"""
        self.authenticated = False
    
    def to_dict(self) -> dict:
        """Konwertuj do słownika na potrzeby serializacji JSON"""
        return {
            'user_name': self.user_name,
            'password': self.password
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Utwórz użytkownika (z JSON)."""
        return cls(
            user_name=data.get('user_name', ''),
            password=data.get('password', '')
        )
