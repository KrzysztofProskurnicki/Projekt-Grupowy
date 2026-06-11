"""Komponent sidebara z przyciskami nawigacji i wylogowaniem (wg wzorca Vault)."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from widgets.nav_button_widget import NavButtonWidget
from widgets.icons import tinted_pixmap
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
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(0)

        # --- Branding: kafelek z tarczą + nazwa aplikacji ---
        brand_row = QWidget()
        brand_row.setStyleSheet("background: transparent; border: none;")
        brand_layout = QHBoxLayout(brand_row)
        brand_layout.setContentsMargins(8, 4, 8, 22)
        brand_layout.setSpacing(11)

        brand_icon = QLabel()
        brand_icon.setFixedSize(32, 32)
        brand_icon.setAlignment(Qt.AlignCenter)
        brand_icon.setPixmap(tinted_pixmap("shield-check", "#ffffff", 19))
        brand_icon.setStyleSheet(
            f"background-color: {styles.COLOR_BLUE}; border-radius: 8px; border: none;"
        )
        brand_layout.addWidget(brand_icon)

        brand_name = QLabel("Password Manager")
        brand_name.setStyleSheet(
            f"font-size: 19px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        brand_layout.addWidget(brand_name)
        brand_layout.addStretch()

        layout.addWidget(brand_row)

        # --- Kontener nawigacji ---
        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent; border: none;")
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(4)

        # Zdefiniuj konfigurację przycisków
        self.buttons_config = [
            ("All Passwords", "key-round", 0),
            ("Favorites", "star", 0),
            ("Security", "shield-check", 0),
            ("Settings", "settings", 0),
            ("Profile", "user", 0)
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

        # --- Karta konta zalogowanego użytkownika ---
        account_card = QWidget()
        account_card.setObjectName("accountCard")
        account_card.setStyleSheet(
            f"QWidget#accountCard {{ background-color: {styles.CARD_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 8px; }}"
        )
        account_layout = QHBoxLayout(account_card)
        account_layout.setContentsMargins(10, 8, 10, 8)
        account_layout.setSpacing(11)

        initial = (self._username[0].upper() if self._username else "?")
        avatar = QLabel(initial)
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background-color: {styles.COLOR_BLUE}; color: white; border-radius: 17px;"
            " font-size: 15px; font-weight: bold; border: none;"
        )
        account_layout.addWidget(avatar)

        name_box = QVBoxLayout()
        name_box.setContentsMargins(0, 0, 0, 0)
        name_box.setSpacing(1)
        name_lbl = QLabel(self._username)
        name_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        sub_lbl = QLabel("Signed in")
        sub_lbl.setStyleSheet(
            f"font-size: 12px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        name_box.addWidget(name_lbl)
        name_box.addWidget(sub_lbl)
        account_layout.addLayout(name_box)
        account_layout.addStretch()

        layout.addWidget(account_card)
        layout.addSpacing(10)

        # --- Przycisk wylogowania ---
        logout_btn = QPushButton("  Logout")
        logout_btn.setIcon(QIcon(tinted_pixmap("log-out", styles.COLOR_RED, 18)))
        logout_btn.setIconSize(QSize(18, 18))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.COLOR_RED};
                border: 1px solid {styles.COLOR_RED};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {styles.RED_SOFT};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 69, 58, 30%);
            }}
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(logout_btn)

    def handle_click(self, index):
        for i, nav_widget in enumerate(self.nav_buttons):
            if i == index:
                nav_widget.btn.setChecked(True)
                nav_widget.badge.setStyleSheet("color: rgba(255, 255, 255, 85%); font-size: 13px; font-weight: 600; background: transparent;")
                nav_widget.set_icon_color("white")
                nav_widget.update_style(True)
            else:
                nav_widget.btn.setChecked(False)
                nav_widget.badge.setStyleSheet(f"color: {styles.TEXT_TERTIARY}; font-size: 13px; font-weight: 600; background: transparent;")
                nav_widget.set_icon_color(styles.TEXT_SECONDARY)
                nav_widget.update_style(False)

        self.nav_clicked.emit(index)

    def update_badge(self, index, count):
        """Zaktualizuj licznik odznaki dla konkretnego przycisku"""
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].badge.setText(str(count) if count > 0 else "")
