"""Registration dialog for creating new user profiles."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from services.authentication_service import AuthenticationService
from constants import (MSG_PASSWORDS_NOT_MATCH, MSG_USERNAME_TAKEN, 
                       MSG_FILL_ALL_FIELDS, MSG_ACCOUNT_CREATED)


class RegisterDialog(QWidget):
    """Registration form for creating new user accounts."""
    
    def __init__(self, login_dialog=None):
        """Initialize registration dialog.
        
        Args:
            login_dialog: Reference to the login dialog to return to.
        """
        super().__init__()
        self.login_dialog = login_dialog
        self.auth_service = AuthenticationService()
        self.init_ui()
    
    def init_ui(self):
        """Build the registration form UI."""
        self.setWindowTitle("Password Manager - Create Account")
        self.setFixedSize(450, 560)
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1e;
            }
            QLabel {
                color: #f5f5f7;
            }
            QLineEdit {
                background-color: #2c2c2e;
                color: #f5f5f7;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #38383a;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #0a84ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("👤")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Create Account")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f5f5f7;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Fill in the details to create your profile")
        subtitle.setStyleSheet("font-size: 14px; color: #98989d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        layout.addWidget(self.password_input)
        
        # Confirm Password input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.returnPressed.connect(self.create_account)
        layout.addWidget(self.confirm_password_input)
        
        # Status label (for errors and success messages)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff453a; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3c;
                color: #f5f5f7;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
            QPushButton:hover {
                background-color: #48484a;
            }
            QPushButton:pressed {
                background-color: #2c2c2e;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        btn_layout.addWidget(back_btn)
        
        # Create button
        create_btn = QPushButton("Create")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #30d158;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
            QPushButton:hover {
                background-color: #28b84c;
            }
            QPushButton:pressed {
                background-color: #1f9e3e;
            }
        """)
        create_btn.clicked.connect(self.create_account)
        btn_layout.addWidget(create_btn)
        
        layout.addLayout(btn_layout)
    
    def create_account(self):
        """Validate inputs and create a new user account."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate all fields are filled
        if not username or not password or not confirm_password:
            self.status_label.setStyleSheet("color: #ff453a; font-size: 14px;")
            self.status_label.setText(MSG_FILL_ALL_FIELDS)
            return
        
        # Validate passwords match
        if password != confirm_password:
            self.status_label.setStyleSheet("color: #ff453a; font-size: 14px;")
            self.status_label.setText(MSG_PASSWORDS_NOT_MATCH)
            self.confirm_password_input.clear()
            return
        
        # Try to register user
        success = self.auth_service.register(username, password)
        if not success:
            self.status_label.setStyleSheet("color: #ff453a; font-size: 14px;")
            self.status_label.setText(MSG_USERNAME_TAKEN)
            return
        
        # Success - show message and go back to login
        self.status_label.setStyleSheet("color: #30d158; font-size: 14px;")
        self.status_label.setText(MSG_ACCOUNT_CREATED)
        
        # Clear fields
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        
        # Return to login after a short delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, self.go_back)
    
    def go_back(self):
        """Return to the login dialog."""
        if self.login_dialog:
            self.login_dialog.show()
        self.close()
