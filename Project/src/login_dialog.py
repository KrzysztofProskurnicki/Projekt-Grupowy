from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../config/config.json')

class LoginDialog(QWidget):
    """Custom styled login dialog matching app theme."""
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Password Manager")
        self.setFixedSize(450, 480)  # Increased height for new field
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
            QPushButton {
                background-color: #0a84ff;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
            QPushButton:hover {
                background-color: #409cff;
            }
            QPushButton:pressed {
                background-color: #0066cc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Icon/Title
        title_label = QLabel("🔐")
        title_label.setStyleSheet("font-size: 48px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # App name
        app_label = QLabel("Password Manager")
        app_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f5f5f7;")
        app_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_label)
        
        # Subtitle
        subtitle = QLabel("Sign in to your account")
        subtitle.setStyleSheet("font-size: 14px; color: #98989d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Username input (NEW)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.returnPressed.connect(self.verify)
        layout.addWidget(self.password_input)
        
        # Error label (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff453a; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        layout.addStretch()
        
        # Login button
        login_btn = QPushButton("Unlock")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.verify)
        layout.addWidget(login_btn)
        
    def verify(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
             self.error_label.setText("Please enter username")
             self.username_input.setFocus()
             return

        # Load config to check password
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                correct_password = config.get('master_password', 'admin') # Default is admin
        except FileNotFoundError:
            correct_password = 'admin'
            
        if password == correct_password:
            self.authenticated = True
            self.close()
        else:
            self.error_label.setText("Invalid password")
            self.password_input.clear()
