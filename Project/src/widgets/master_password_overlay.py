"""Widget nakładki hasła głównego - okno uwierzytelniania"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from services.authentication_service import AuthenticationService
from styles import TEXT_PRIMARY


class MasterPasswordOverlay(QWidget):
    
    def __init__(self, parent, on_success_callback, auth_service: AuthenticationService):
        """Inicjalizuj nakładki hasła głównego
        
        Argumenty:
            parent: Widget nadrzędny
            on_success_callback: Funkcja wywoływana po pomyślnym uwierzytelnieniu
            auth_service: Instancja serwisu uwierzytelniania
        """
        super().__init__(parent)
        self.on_success = on_success_callback
        self.auth_service = auth_service
        self.resize(parent.size())

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Kontener
        container = QFrame()
        container.setFixedSize(320, 180)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 12px;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: {styles.font_px(16)}px;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: #2c2c2e;
                color: white;
                border: 1px solid #48484a;
                border-radius: 6px;
                padding: 8px;
                font-size: {styles.font_px(14)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #0a84ff;
            }}
            QPushButton {{
                background-color: #3a3a3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: {styles.font_px(14)}px;
            }}
            QPushButton:hover {{
                background-color: #48484a;
            }}
            QPushButton#primary {{
                background-color: #0a84ff;
            }}
            QPushButton#primary:hover {{
                background-color: #0077ed;
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(16)
        
        # Tytuł
        title_lbl = QLabel("Enter Master Password")
        title_lbl.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_lbl)
        
        # Pole wejściowe
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.returnPressed.connect(self.verify_password)
        container_layout.addWidget(self.password_input)
        
        # Przyciski
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.close)
        
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primary")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.verify_password)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        
        container_layout.addLayout(btn_layout)
        layout.addWidget(container)
        
        self.password_input.setFocus()
    
    def verify_password(self):
        """Zweryfikuj wpisane hasło względem hasła głównego"""
        entered_pwd = self.password_input.text()
        
        if self.auth_service.verify_master_password(entered_pwd):
            self.on_success()
            self.close()
        else:
            # Mignij czerwonym obramowaniem przy błędzie
            self.password_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2c2c2e;
                    color: white;
                    border: 1px solid #ff453a;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            QTimer.singleShot(1000, lambda: self.password_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2c2c2e;
                    color: white;
                    border: 1px solid #48484a;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #0a84ff;
                }
            """))

    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
