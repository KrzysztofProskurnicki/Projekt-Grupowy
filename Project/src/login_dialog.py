import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from Project.baza_v1 import db_manager


class LoginDialog(QDialog):
    """Login/setup screen for the encrypted vault."""

    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.setup_mode = not db_manager.vault_exists()
        self.reset_mode = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Password Manager")
        self.setFixedSize(450, 450)
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
            QPushButton#secondary {
                background-color: transparent;
                color: #ff9f0a;
                border: 1px solid #ff9f0a;
            }
            QPushButton#secondary:hover {
                background-color: #3a2a12;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title_label = QLabel("Password Manager")
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #f5f5f7;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet("font-size: 14px; color: #98989d;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        layout.addSpacing(20)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Master password")
        self.password_input.returnPressed.connect(self.verify)
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Repeat master password")
        self.confirm_input.returnPressed.connect(self.verify)
        layout.addWidget(self.confirm_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff453a; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        layout.addStretch()

        self.action_btn = QPushButton("")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.verify)
        layout.addWidget(self.action_btn)

        self.reset_btn = QPushButton("Reset master password")
        self.reset_btn.setObjectName("secondary")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.start_reset)
        layout.addWidget(self.reset_btn)
        self.update_mode()

    def update_mode(self):
        if self.reset_mode:
            self.subtitle.setText("Reset vault and create a new master password")
            self.password_input.setPlaceholderText("New master password")
            self.action_btn.setText("Reset vault")
        elif self.setup_mode:
            self.subtitle.setText("Create your encrypted vault")
            self.password_input.setPlaceholderText("Master password")
            self.action_btn.setText("Create vault")
        else:
            self.subtitle.setText("Unlock encrypted vault")
            self.password_input.setPlaceholderText("Master password")
            self.action_btn.setText("Unlock")

        self.confirm_input.setVisible(self.setup_mode or self.reset_mode)
        self.reset_btn.setVisible(not self.setup_mode and not self.reset_mode)

    def start_reset(self):
        result = QMessageBox.warning(
            self,
            "Reset vault",
            "Resetting the master password creates a new empty vault. Existing passwords will not be readable without the old master password. A backup of the current database will be saved.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result != QMessageBox.Yes:
            return

        self.reset_mode = True
        self.error_label.setText("")
        self.password_input.clear()
        self.confirm_input.clear()
        self.update_mode()
        self.password_input.setFocus()

    def verify(self):
        password = self.password_input.text()
        if not password:
            self.error_label.setText("Enter master password")
            self.password_input.setFocus()
            return

        if self.setup_mode or self.reset_mode:
            if len(password) < 8:
                self.error_label.setText("Master password must have at least 8 characters")
                return
            if password != self.confirm_input.text():
                self.error_label.setText("Passwords do not match")
                self.confirm_input.clear()
                self.confirm_input.setFocus()
                return

            if self.reset_mode:
                db_manager.reset_vault(password)
            else:
                db_manager.initialize_database(password)
            self.authenticated = True
            self.accept()
            return

        if db_manager.login(password):
            self.authenticated = True
            self.accept()
        else:
            self.error_label.setText("Invalid master password")
            self.password_input.clear()
            self.password_input.setFocus()
