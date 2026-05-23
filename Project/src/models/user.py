"""User model - Data class representing application user profile."""

from dataclasses import dataclass


@dataclass
class User:
    """Represents a user profile with credentials."""
    
    user_name: str
    password: str
    authenticated: bool = False
    
    def authenticate(self) -> None:
        """Mark user as authenticated."""
        self.authenticated = True
    
    def logout(self) -> None:
        """Mark user as logged out."""
        self.authenticated = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'user_name': self.user_name,
            'password': self.password
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User from dictionary (from JSON)."""
        return cls(
            user_name=data.get('user_name', ''),
            password=data.get('password', '')
        )
