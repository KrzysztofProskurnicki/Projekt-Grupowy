"""Password model - dataclass representing a single password entry."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Password:
    """Password data model."""
    
    # Podstawowe dane
    name: str              # Nazwa konta (np. "GitHub")
    email: str             # Email/login użytkownika
    password: str          # Zaszyfrowane hasło
    
    # Wizualizacja
    color: str             # Kolor ikony (hex)
    
    # Atrybuty
    weak_password: bool = False    # Czy hasło jest słabe
    favorite: bool = False         # Czy w ulubionych
    
    # Opcjonalne
    website: Optional[str] = None  # URL strony
    notes: Optional[str] = None    # Notatki użytkownika
    
    def to_dict(self) -> dict:
        """Konwertuj do słownika (dla JSON)."""
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'color': self.color,
            'weak_password': self.weak_password,
            'favorite': self.favorite,
            'website': self.website,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Password':
        """Utwórz obiekt z słownika (z JSON)."""
        return cls(
            name=data.get('name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            color=data.get('color', '#333'),
            weak_password=data.get('weak_password', False),
            favorite=data.get('favorite', False),
            website=data.get('website'),
            notes=data.get('notes')
        )
    
    def get_initial(self) -> str:
        """Zwróć pierwszą literę nazwy (dla ikony)."""
        return self.name[0].upper() if self.name else '?'
