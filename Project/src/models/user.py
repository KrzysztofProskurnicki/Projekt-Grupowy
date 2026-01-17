"""User model - Data class representing application user."""

from dataclasses import dataclass


@dataclass
class User:
    """Represents an authenticated user."""
    
    username: str
    authenticated: bool = False
    
    def authenticate(self) -> None:
        """Mark user as authenticated."""
        self.authenticated = True
    
    def logout(self) -> None:
        """Mark user as logged out."""
        self.authenticated = False
