"""Authentication Service - User authentication logic."""

from services.data_manager import DataManager


class AuthenticationService:
    """Manages user authentication and session state."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.data_manager = DataManager()
        self._is_authenticated = False
        self._current_user = None
    
    def verify_master_password(self, password: str) -> bool:
        """Verify if provided password matches master password (legacy).
        
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
    
    def get_current_user(self) -> str:
        """Get currently authenticated username.
        
        Returns:
            Username string or None.
        """
        return self._current_user
    
    def set_authenticated(self, status: bool) -> None:
        """Set authentication status.
        
        Args:
            status: New authentication status.
        """
        self._is_authenticated = status
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with username and password against user profiles.
        
        Args:
            username: Username to authenticate.
            password: Password to authenticate with.
            
        Returns:
            True if authentication successful, False otherwise.
        """
        user = self.data_manager.find_user(username)
        if user and user.get('password') == password:
            self._is_authenticated = True
            self._current_user = username
            return True
        return False
    
    def register(self, username: str, password: str) -> bool:
        """Register a new user profile.
        
        Args:
            username: New username.
            password: New password.
            
        Returns:
            True if registration successful, False if username already taken.
        """
        return self.data_manager.register_user(username, password)
    
    def logout(self) -> None:
        """Clear authentication status."""
        self._is_authenticated = False
        self._current_user = None
