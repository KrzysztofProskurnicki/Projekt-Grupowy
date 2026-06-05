"""Komponent sidebara z przyciskami nawigacji i wylogowaniem."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from widgets.nav_button_widget import NavButtonWidget
import styles


class Sidebar(QFrame):
    nav_clicked = pyqtSignal(int)
    logout_clicked = pyqtSignal()
    
    def __init__(self, username: str = "User"):
        super().__init__()
        self.setObjectName("Sidebar")
        self._username = username
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Nagłówek sidebara
        app_title = QLabel("Passwords")
        app_title.setObjectName("AppTitle")
        layout.addWidget(app_title)
        
        # Kontener nawigacji
        nav_container = QWidget()
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(8, 8, 8, 8)
        self.nav_layout.setSpacing(4)
        
        # Zdefiniuj konfigurację przycisków
        self.buttons_config = [
            ("All Passwords", "🔑", 12),
            ("Favorites", "⭐", 3),
            ("Security Recommendations", "🛡️", 2),
            ("Vault", "🔒", 0),
            ("Settings", "⚙️", 0),
            ("Profile", "👤", 0)
        ]
        
        self.nav_buttons = []
        for i, (text, icon, count) in enumerate(self.buttons_config):
            is_active = (i == 0)
            btn = NavButtonWidget(text, icon, count, is_active)
            btn.btn.clicked.connect(lambda checked, idx=i: self.handle_click(idx))
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        layout.addWidget(nav_container)
        layout.addStretch()
        
        # Stopka użytkownika
        self.user_footer = QLabel(f"Logged in as: {self._username}")
        self.user_footer.setStyleSheet(
            f"color: {styles.TEXT_SECONDARY}; padding: 16px 16px 8px 16px; font-size: 12px;"
        )
        layout.addWidget(self.user_footer)
        
        # Przycisk wylogowania
        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.COLOR_RED};
                border: 1px solid {styles.COLOR_RED};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
                margin: 4px 16px 16px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 69, 58, 0.15);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 69, 58, 0.3);
            }}
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(logout_btn)

    def handle_click(self, index):
        for i, nav_widget in enumerate(self.nav_buttons):
            if i == index:
                nav_widget.btn.setChecked(True)
                nav_widget.badge.setStyleSheet("color: white;")
            else:
                nav_widget.btn.setChecked(False)
                nav_widget.badge.setStyleSheet(f"color: {styles.TEXT_SECONDARY};")
        
        self.nav_clicked.emit(index)
        
    def update_badge(self, index, count):
        """Zaktualizuj licznik odznaki dla konkretnego przycisku"""
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].badge.setText(str(count) if count > 0 else "")
