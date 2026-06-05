"""Widok szczegółowy - wyświetla szczegółowe informacje o wpisie hasła"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QGuiApplication
from widgets.notification_popup import NotificationPopup
from widgets.master_password_overlay import MasterPasswordOverlay
from services.authentication_service import AuthenticationService
import styles
from constants import MSG_COPIED



class DetailView(QWidget):

    def __init__(self, switch_back_callback, favorite_callback=None):
        """Inicjalizuj widok szczegółów

        Argumenty:
            switch_back_callback: Funkcja powrotu do poprzedniego widoku
            favorite_callback: Funkcja przełączająca status ulubionego wpisu
        """
        super().__init__()
        self.switch_back_callback = switch_back_callback
        self.favorite_callback = favorite_callback
        self.current_name = ""

        # Zmienne stanu
        self.is_favorite = True
        self.password_visible = False
        self.auth_service = AuthenticationService()
        self.actual_password = ""

        # Główny layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        self._build_ui()

    # --- Budowanie UI ---
    def _build_ui(self):

        # --- GÓRNA WARSTWA: nawigacja (przycisk powrotu) ---
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("< All Passwords")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.COLOR_BLUE};
                font-size: 16px;
                border: none;
                text-align: left;
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: #409cff;
            }}
        """)
        self.back_btn.clicked.connect(self.switch_back_callback)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.main_layout.addLayout(top_bar)

        # --- HEADER LAYER: Ikona + Tytuł + Gwiazdka ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)

        # Ikona główna
        self.icon_label = QLabel("G")
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            background-color: {styles.CARD_BG};
            color: {styles.TEXT_PRIMARY};
            border-radius: 20px;
            font-size: 40px;
            font-weight: bold;
        """)

        # Tytuł i Link (Pionowo)
        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        self.title_label = QLabel("GitHub")
        self.title_label.setStyleSheet(
            f"font-size: 32px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
        )
        self.link_label = QLabel("https://github.com")
        self.link_label.setStyleSheet(
            f"font-size: 16px; color: {styles.COLOR_BLUE};"
        )
        self.link_label.setCursor(Qt.PointingHandCursor)
        # Opcjonalnie: link_label.mousePressEvent...

        title_box.addWidget(self.title_label)
        title_box.addWidget(self.link_label)

        # Gwiazdka (ulubione)
        self.star_btn = QPushButton("★")
        self.star_btn.setFixedSize(40, 40)
        self.star_btn.setCursor(Qt.PointingHandCursor)
        self.update_star_style()
        self.star_btn.clicked.connect(self.toggle_favorite)

        header_layout.addWidget(self.icon_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.star_btn)

        self.main_layout.addLayout(header_layout)

        # --- WARSTWA PÓL ---
        # Pola: nazwa użytkownika, hasło, strona, notatki
        self.create_field("USERNAME", "john.doe@email.com", is_copyable=True)
        self.create_field("PASSWORD", "•••••••••••••", is_copyable=True, is_password=True)
        self.create_field("WEBSITE", "https://github.com", is_copyable=True)
        self.create_field("NOTES", "Main development account", is_multiline=True)

        self.main_layout.addStretch()

    # --- Motyw ---
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def refresh_theme(self):
        """Usówa wszystkie widgety potomne i przebuduj UI z bieżącymi kolorami motywu

        Zachowuje pola stanu: current_name, is_favorite, actual_password,
        password_visible.
        """
        # Zapisz stan
        saved_name = self.current_name
        saved_favorite = self.is_favorite
        saved_password = self.actual_password
        saved_visible = self.password_visible

        # Wyczytaj układ
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        self._build_ui()

        # Przywróć stan
        self.current_name = saved_name
        self.is_favorite = saved_favorite
        self.actual_password = saved_password
        self.password_visible = saved_visible
        self.update_star_style()

    # --- Pola ---
    def create_field(self, label_text, value_text, is_copyable=False, is_password=False, is_multiline=False):
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: {styles.CARD_BG};
            border-radius: 12px;
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Etykieta
        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            f"color: {styles.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;"
        )
        layout.addWidget(lbl)

        # Wiersz wartości
        row = QHBoxLayout()

        # Używa QTextEdit dla pól wielowierszowych (notatki), a QLabel dla pozostałych
        if is_multiline:
            value_widget = QTextEdit()
            value_widget.setPlainText(value_text)
            value_widget.setStyleSheet(f"""
                QTextEdit {{
                    color: {styles.TEXT_PRIMARY};
                    font-size: 18px;
                    border: none;
                    background: transparent;
                }}
            """)
            value_widget.setMinimumHeight(60)
            value_widget.setMaximumHeight(100)
            self.notes_edit = value_widget
        else:
            value_widget = QLabel(value_text)
            value_widget.setStyleSheet(
                f"color: {styles.TEXT_PRIMARY}; font-size: 18px; border: none; background: transparent;"
            )

            # Jeśli chcemy identyfikować pola do późniejszej aktualizacji
            if label_text == "USERNAME": self.username_lbl = value_widget
            elif label_text == "PASSWORD": self.password_lbl = value_widget
            elif label_text == "WEBSITE":  self.website_lbl = value_widget

        row.addWidget(value_widget)
        row.addStretch()

        # Akcje (kopiowanie, podgląd)
        if is_password:
            self.eye_btn = QPushButton("👁")
            self.eye_btn.setFixedSize(30, 30)
            self.eye_btn.setCursor(Qt.PointingHandCursor)
            self.eye_btn.setStyleSheet(
                f"color: {styles.COLOR_BLUE}; border: none; font-size: 16px; background: transparent;"
            )
            self.eye_btn.clicked.connect(self.toggle_password_visibility)
            row.addWidget(self.eye_btn)

            # Przycisk kopiowania hasła
            copy_pwd_btn = QPushButton("❐")
            copy_pwd_btn.setFixedSize(30, 30)
            copy_pwd_btn.setCursor(Qt.PointingHandCursor)
            copy_pwd_btn.setStyleSheet(
                f"color: {styles.COLOR_BLUE}; border: none; font-size: 16px; background: transparent;"
            )
            copy_pwd_btn.clicked.connect(lambda: self.copy_with_notification(self.actual_password, "PASSWORD"))
            row.addWidget(copy_pwd_btn)

        if is_copyable and not is_multiline and not is_password:
            copy_btn = QPushButton("❐")
            copy_btn.setFixedSize(30, 30)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setStyleSheet(
                f"color: {styles.COLOR_BLUE}; border: none; font-size: 16px; background: transparent;"
            )
            copy_btn.clicked.connect(lambda checked, w=value_widget, l=label_text: self.copy_with_notification(w.text(), l))
            row.addWidget(copy_btn)

        layout.addLayout(row)
        self.main_layout.addWidget(container)


    def request_master_password(self, on_success):
        if self.auth_service.is_authenticated():
            on_success()
            return

        def auth_success_wrapper():
            self.auth_service.set_authenticated(True)
            on_success()

        overlay = MasterPasswordOverlay(self, auth_success_wrapper, self.auth_service)
        overlay.show()

    def toggle_password_visibility_with_auth(self):
        """Przełącz widoczne hasła po weryfikacją hasła głównego (master password)"""
        if not self.password_visible:
            self.request_master_password(self._show_password)
        else:
            self.password_visible = False
            self.password_lbl.setText("•••••••••••••")
            self.eye_btn.setText("👁")


    def _show_password(self):
        self.password_visible = True
        self.password_lbl.setText(self.actual_password)
        self.eye_btn.setText("👁‍🗨")


    def copy_password_with_auth(self):
        self.request_master_password(self._copy_password_action)

    def _copy_password_action(self):
        QGuiApplication.clipboard().setText(self.actual_password)
        self.show_notification(MSG_COPIED)

    def copy_with_notification(self, text, field_name):
        """Skopiuj tekst i pokaż powiadomienie

        Argumenty:
            text: Tekst do skopiowania do schowka
            field_name: Nazwa kopiowanego pola
        """
        QGuiApplication.clipboard().setText(text)
        self.show_notification(MSG_COPIED)

    def show_notification(self, message):
        popup = NotificationPopup(message, self)
        popup.show()


    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.update_star_style()

        if self.favorite_callback and self.current_name:
            self.favorite_callback(self.current_name, self.is_favorite)

    def update_star_style(self):
        if self.is_favorite:
            self.star_btn.setText("★")
            self.star_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {styles.COLOR_YELLOW};
                    font-size: 24px;
                    border: none;
                }}
                QPushButton:hover {{
                    color: #ffe066;
                }}
            """)
        else:
            self.star_btn.setText("☆")
            self.star_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {styles.TEXT_SECONDARY};
                    font-size: 24px;
                    border: none;
                }}
                QPushButton:hover {{
                    color: {styles.COLOR_YELLOW};
                }}
            """)

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_lbl.setText(self.actual_password)
            self.eye_btn.setText("👁‍🗨")
        else:
            self.password_lbl.setText("•••••••••••••")
            self.eye_btn.setText("👁")


    def update_data(self, entry: dict):
        name = entry.get("name", "")
        email = entry.get("email", "")
        color = entry.get("color", styles.CARD_BG)
        favorite = bool(entry.get("favorite", False))
        notes = entry.get("notes", "")
        password = entry.get("password", "")
        letter = name[0].upper() if name else "?"

        self.current_name = name
        self.is_favorite = favorite
        self.actual_password = password
        self.update_star_style()

        self.title_label.setText(name)
        self.icon_label.setText(letter)
        self.icon_label.setStyleSheet(f"""
            background-color: {color};
            color: {styles.TEXT_PRIMARY};
            border-radius: 20px;
            font-size: 40px;
            font-weight: bold;
        """)

        self.link_label.setText(name)
        self.username_lbl.setText(email)
        self.website_lbl.setText(name)
        self.notes_edit.setPlainText(notes)

        # Ukryj hasło do czasu ponownego uwierzytelnienia użytkownika.
        self.password_visible = False
        self.password_lbl.setText("•••••••••••••" if password else "")
        self.eye_btn.setText("👁")
