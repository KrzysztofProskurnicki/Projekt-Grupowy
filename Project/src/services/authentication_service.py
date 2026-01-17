"""Authentication Service - User authentication logic."""

from services.data_manager import DataManager


class AuthenticationService:
    """Manages user authentication and session state."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.data_manager = DataManager()
        self._is_authenticated = False
    
    def verify_master_password(self, password: str) -> bool:
        """Verify if provided password matches master password.
        
        Args:
            password: Password to verify.
            
        Returns:
            True if password is correct, False otherwise.
        """
        master_password = self.data_manager.get_master_password()
        return password == master_password
    
    def get_master_password(self) -> str:
        """Get master password from config.
        
        Returns:
            Master password string.
        """
        return self.data_manager.get_master_password()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated in current session.
        
        Returns:
            True if authenticated, False otherwise.
        """
        return self._is_authenticated
    
    def set_authenticated(self, status: bool) -> None:
        """Set authentication status.
        
        Args:
            status: New authentication status.
        """
        self._is_authenticated = status
    
    def authenticate(self, password: str) -> bool:
        """Authenticate user with password and set session status.
        
        Args:
            password: Password to authenticate with.
            
        Returns:
            True if authentication successful, False otherwise.
        """
        if self.verify_master_password(password):
            self._is_authenticated = True
            return True
        return False
    
    def logout(self) -> None:
        """Clear authentication status."""
        self._is_authenticated = False
